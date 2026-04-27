import os
import datetime
import pandas as pd
import streamlit as st

from harvest.utils import load_data

BILLABLE_OPTIONS = ["Billable", "Non-Billable", "OOW"]


def _last_week_range():
    """Return (monday, sunday) of the previous calendar week."""
    today = datetime.date.today()
    # weekday(): Monday=0 … Sunday=6
    last_monday = today - datetime.timedelta(days=today.weekday() + 7)
    last_sunday = last_monday + datetime.timedelta(days=6)
    return last_monday, last_sunday


def render_sidebar() -> tuple[pd.DataFrame | None, list, list, list, object, object]:
    """
    Render the sidebar and return:
        (df_raw, sel_clients, sel_employees, sel_billable, start_d, end_d)

    Returns (None, [], [], [], None, None) when no file has been uploaded yet.
    """
    with st.sidebar:
        st.markdown("## 🌾 Harvest")
        st.markdown('<p class="section-label">Resource Dashboard</p>', unsafe_allow_html=True)
        st.divider()

        uploaded = st.file_uploader(
            "Upload CSV",
            type=["csv"],
            help="Upload a Harvest Persuasion Employees CSV export.",
        )

        if not uploaded:
            return None, [], [], [], None, None

        df_raw = load_data(uploaded)

        st.divider()
        st.markdown('<p class="section-label">Filters</p>', unsafe_allow_html=True)

        # Client filter
        clients = sorted(df_raw["Client (Harvest)"].dropna().unique().tolist())
        sel_clients = st.multiselect("Client", ["All"] + clients, default=["All"])
        if "All" in sel_clients or not sel_clients:
            sel_clients = clients

        # Employee filter
        employees_all = sorted(df_raw["Employee"].dropna().unique().tolist())
        sel_employees = st.multiselect("Employee", ["All"] + employees_all, default=["All"])
        if "All" in sel_employees or not sel_employees:
            sel_employees = employees_all

        # Billable type filter (Billable / Non-Billable / OOW)
        sel_billable = st.multiselect(
            "Billable",
            ["All"] + BILLABLE_OPTIONS,
            default=["All"],
            help="Billable = billable hours, Non-Billable = internal/overhead, OOW = out of work.",
        )
        if "All" in sel_billable or not sel_billable:
            sel_billable = BILLABLE_OPTIONS

        # Date range – default to last week Monday → Sunday
        min_d, max_d = df_raw["Date"].min(), df_raw["Date"].max()
        lw_mon, lw_sun = _last_week_range()
        default_start = max(min_d, lw_mon)
        default_end = min(max_d, lw_sun)
        # Fallback: if last-week window is entirely outside data range use full range
        if default_start > default_end:
            default_start, default_end = min_d, max_d

        date_range = st.date_input(
            "Date range",
            value=(default_start, default_end),
            min_value=min_d,
            max_value=max_d,
            format="YYYY-MM-DD",
        )
        start_d, end_d = (date_range if isinstance(date_range, tuple) and len(date_range) == 2
                          else (default_start, default_end))

        st.divider()
        st.markdown('<p class="section-label">Legend</p>', unsafe_allow_html=True)
        st.markdown(
            '<span class="badge badge-normal">Workday</span>&nbsp;'
            '<span class="badge badge-weekend">Weekend</span>&nbsp;'
            '<span class="badge badge-holiday">Holiday</span>',
            unsafe_allow_html=True,
        )

    return df_raw, sel_clients, sel_employees, sel_billable, start_d, end_d