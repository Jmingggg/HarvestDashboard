import pandas as pd
import streamlit as st


def _build_prompt(
    df: pd.DataFrame,
    emp_df: pd.DataFrame,
    emp_client: pd.DataFrame,
    client_task: pd.DataFrame,
    hours_pivot: pd.DataFrame,
) -> str:
    """
    Serialise the dataframes into a structured prompt string for the summarizer agent.
    Converts DataFrames to compact markdown tables so the LLM can read them easily.
    """
 
    def df_to_md(frame: pd.DataFrame, max_rows: int = 200) -> str:
        return frame.head(max_rows).to_markdown(index=False)
 
    sections = [
        # "## Raw Time Entries (sample)\n" + df_to_md(
        #     df[["Employee", "Date", "Client (Harvest)", "Task", "Hours", "Type", "DateClass"]]
        # ),
        "## Employee Performance Summary\n" + df_to_md(emp_df),
        "## Employee × Client Hours\n" + df_to_md(emp_client),
        "## Client × Task Detail\n" + df_to_md(client_task),
        "## Daily Hours Pivot (Employee × Date)\n" + df_to_md(hours_pivot),
    ]
 
    return "\n\n---\n\n".join(sections)


def render_tab_summary(
    df: pd.DataFrame,
    emp_df: pd.DataFrame,
    emp_client: pd.DataFrame,
    client_task: pd.DataFrame,
    hours_pivot: pd.DataFrame,
) -> None:
    """
    Render the AI Summary tab.
 
    Parameters
    ----------
    df          : Filtered raw DataFrame (from apply_filters).
    emp_df      : Employee performance aggregation (from render_tab_employee).
    emp_client  : Employee × Client hours breakdown (from render_tab_employee).
    client_task : Client × Task detail table (from render_tab_client).
    hours_pivot : Daily pivot summary rows (from render_tab_pivot).
    """
    st.markdown("#### 📝 AI Workforce Utilisation Report")
    st.markdown(
        '<p style="color:#64748b; font-size:0.92rem; margin-bottom:16px;">'
        "Click <strong>Generate Report</strong> to have the AI analyse the current filtered "
        "data and produce a detailed workforce utilisation summary."
        "</p>",
        unsafe_allow_html=True,
    )
 
    # ── Controls row ─────────────────────────────────────────────────────
    col_btn, col_info = st.columns([1, 4])
    generate = col_btn.button("✨ Generate Report", type="primary", use_container_width=True)
    col_info.markdown(
        f'<span style="color:#94a3b8; font-size:0.82rem;">'
        f"Analysing {df['Employee'].nunique()} employees · "
        f"{df['Client (Harvest)'].nunique()} clients · "
        f"{len(df):,} time entries</span>",
        unsafe_allow_html=True,
    )
 
    st.divider()
 
    # ── Session-state cache so report survives reruns ─────────────────────
    if "summary_report" not in st.session_state:
        st.session_state["summary_report"] = None
    if "summary_error" not in st.session_state:
        st.session_state["summary_error"] = None
    if "total_tokens" not in st.session_state:
        st.session_state["total_tokens"] = None
 
    if generate:
        st.session_state["summary_report"] = None
        st.session_state["summary_error"] = None
        st.session_state["total_tokens"] = None
 
        prompt = _build_prompt(df, emp_df, emp_client, client_task, hours_pivot)
 
        with st.spinner("🤖 Analysing workforce data…"):
            try:
                from harvest.agents import build_summarizer_agent
 
                agent = build_summarizer_agent()
                response = agent.run(prompt)
                
                st.session_state["total_tokens"] = response.metrics.total_tokens
 
                if hasattr(response, "content"):
                    report_md = response.content
                else:
                    report_md = str(response)
 
                st.session_state["summary_report"] = report_md
 
            except ImportError as exc:
                st.session_state["summary_error"] = (
                    f"⚠️ Could not import the summarizer agent: `{exc}`. "
                    "Make sure `agno` is installed and your API key is configured."
                )
            except Exception as exc:  # noqa: BLE001
                st.session_state["summary_error"] = f"⚠️ Agent error: {exc}"
 
    # ── Render cached report or error ─────────────────────────────────────
    if st.session_state["summary_error"]:
        st.error(st.session_state["summary_error"])
 
    elif st.session_state["summary_report"]:
        report_md: str = st.session_state["summary_report"]
        st.markdown(report_md)

        bottom_cols = st.columns((1, 1, 1, 1))
        with bottom_cols[-1]: 
            # Download button
            st.download_button(
                label="⬇️ Download Report (Markdown)",
                data=report_md,
                file_name="harvest_utilisation_report.md",
                mime="text/markdown",
                use_container_width=False,
            )
            
            st.metric("Total Tokens", f"{st.session_state['total_tokens']:,}")
 
    else:
        # Empty state
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
