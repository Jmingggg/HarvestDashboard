import os
import time
import pandas as pd
import streamlit as st
from harvest.agents import build_summarizer_agent


def _get_agent(api_key: str):
    """
    Cache the agent per API key. Rebuilds only when the key changes.
    Using st.cache_resource with a key-based hash.
    """
    @st.cache_resource(hash_funcs={str: lambda s: s})
    def _build(key: str):
        os.environ["API_KEY"] = key  # set BEFORE building
        return build_summarizer_agent()

    return _build(api_key)


def render_tab_summary(
    df: pd.DataFrame,
    emp_df: pd.DataFrame,
    emp_client: pd.DataFrame,
    client_task: pd.DataFrame,
    hours_pivot: pd.DataFrame,
) -> None:
    st.markdown("#### 📝 AI Workforce Utilisation Report")
    st.markdown(
        '<p style="color:#64748b; font-size:0.92rem; margin-bottom:16px;">'
        "Click <strong>Generate Report</strong> to have the AI analyse the current filtered "
        "data and produce a detailed workforce utilisation summary."
        "</p>",
        unsafe_allow_html=True,
    )

    # ── Controls row ──────────────────────────────────────────────────────
    key_input, col_btn, col_info = st.columns([3, 1, 1], vertical_alignment="bottom")

    # Persist the API key in session state so it survives reruns
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = ""

    api_key = key_input.text_input(
        label="GEMINI API KEY",
        type="password",
        value=st.session_state["api_key"],
        key="api_key_input",
        help="Get your API key from https://aistudio.google.com/api-keys",
    )
    # Sync back to session state
    st.session_state["api_key"] = api_key

    generate = col_btn.button(
        "✨ Generate Report",
        type="primary",
        use_container_width=True,
        disabled=not api_key.strip(),  # disable if no key
    )
    col_info.markdown(
        f'<span style="color:#94a3b8; font-size:0.82rem;">'
        f"Analysing {df['Employee'].nunique()} employees · "
        f"{df['Client (Harvest)'].nunique()} clients · "
        f"{len(df):,} time entries</span>",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Session-state cache ───────────────────────────────────────────────
    for key in ("summary_report", "summary_error", "response_time", "total_tokens"):
        st.session_state.setdefault(key, None)

    if generate:
        if not api_key.strip():
            st.warning("Please enter your Gemini API key before generating.")
            return

        # Reset state
        for key in ("summary_report", "summary_error", "response_time", "total_tokens"):
            st.session_state[key] = None

        try:
            # Agent is built/cached here, AFTER key is confirmed
            agent = _get_agent(api_key.strip())
        except Exception as exc:
            st.error(f"⚠️ Failed to initialise agent: {exc}")
            return

        prompt = _build_prompt(df, emp_df, emp_client, client_task, hours_pivot)

        with st.spinner("Analysing workforce data…"):
            try:
                start = time.time()
                response = agent.run(prompt)
                st.session_state["response_time"] = time.time() - start
                st.session_state["total_tokens"] = response.metrics.total_tokens
                st.session_state["summary_report"] = (
                    response.content if hasattr(response, "content") else str(response)
                )
            except ImportError as exc:
                st.session_state["summary_error"] = (
                    f"⚠️ Could not import the summarizer agent: `{exc}`. "
                    "Make sure `agno` is installed and your API key is configured."
                )
            except Exception as exc:
                st.session_state["summary_error"] = f"⚠️ Agent error: {exc}"

    # ── Render ────────────────────────────────────────────────────────────
    if st.session_state["summary_error"]:
        st.error(st.session_state["summary_error"])

    elif st.session_state["summary_report"]:
        report_md: str = st.session_state["summary_report"]
        st.markdown(report_md)

        time_card, token_card, _, download_card = st.columns(
            spec=(1, 1, 1, 1), vertical_alignment="bottom"
        )
        with time_card:
            st.metric("⏱️ Response Time", f"{st.session_state['response_time']:.2f}s")
        with token_card:
            st.metric("🪙 Total Tokens", f"{st.session_state['total_tokens']:,}")
        with download_card:
            st.download_button(
                label="⬇️ Download Report (Markdown)",
                data=report_md,
                file_name="harvest_utilisation_report.md",
                mime="text/markdown",
            )

    else:
        st.markdown(
            """
            <div style="text-align:center; padding:60px 40px; color:#94a3b8;">
                <div style="font-size:2.5rem; margin-bottom:12px;">🤖</div>
                <p style="font-size:1rem; margin:0;">
                    Your AI-generated report will appear here.<br>
                    Hit <strong style="color:#2563eb;">Generate Report</strong> above to start.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
