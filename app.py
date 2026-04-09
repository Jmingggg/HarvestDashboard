"""
app.py – Entry point for the Harvest Resource Dashboard.

Run with:
    streamlit run app.py
"""
import streamlit as st

from harvest.components import (
    inject_css,
    render_sidebar,
    render_kpi_row,
    render_tab_overview,
    render_tab_client,
    render_tab_employee,
    render_tab_pivot,
)
from harvest.utils import apply_filters

# ─── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Harvest · Resource Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ─── Sidebar (upload + filters) ─────────────────────────────────────────────────
df_raw, sel_clients, sel_employees, start_d, end_d = render_sidebar()

# ─── Landing screen (no file uploaded) ──────────────────────────────────────────
if df_raw is None:
    st.markdown("""
    <div style="text-align:center; padding: 80px 40px;">
        <div style="font-size:4rem; margin-bottom:16px;">🌾</div>
        <h1 style="font-family:'DM Serif Display',serif; font-size:2.8rem; margin-bottom:8px;">
            Harvest Resource Dashboard
        </h1>
        <p style="color:#64748b; font-size:1.05rem; max-width:480px; margin:0 auto 32px;">
            Upload your Harvest Persuasion Employees CSV export from the sidebar to get started.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── Filter ─────────────────────────────────────────────────────────────────────
df = apply_filters(df_raw, sel_clients, sel_employees, start_d, end_d)

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ─── KPI strip ──────────────────────────────────────────────────────────────────
total_h, billable_h, util_rate = render_kpi_row(df)
nonbill_h = df[df["NonBillable"]]["Hours"].sum()
oow_h     = df[df["Out of Work"]]["Hours"].sum()

# ─── Tabs ───────────────────────────────────────────────────────────────────────
tab_overview, tab_client, tab_employee, tab_pivot, tab_summary = st.tabs([
    "📊 Overview", "🏢 By Client", "👤 By Employee", "📅 Hours Pivot", "📝 Summary"
])

with tab_overview:
    render_tab_overview(df, billable_h, nonbill_h, oow_h, util_rate)

with tab_client:
    client_task = render_tab_client(df)

with tab_employee:
    emp_df, emp_client = render_tab_employee(df, start_d, end_d)

with tab_pivot:
    hours_pivot = render_tab_pivot(df)
    
with tab_summary:
    st.dataframe(
        data=client_task,
        width="stretch",
        hide_index=True
    )
    st.markdown("---")
    
    st.dataframe(
        data=emp_df,
        width="stretch",
        hide_index=True
    )
    st.markdown("---")
    
    st.dataframe(
        data=emp_client,
        width="stretch",
        hide_index=True
    )
    st.markdown("---")
    
    st.dataframe(
        data=hours_pivot,
        width="stretch",
        hide_index=True
    )
    st.markdown("---")
    
    
