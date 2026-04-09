import os
import pandas as pd
import streamlit as st

from harvest.utils import load_data


def render_sidebar() -> tuple[pd.DataFrame | None, list, list, object, object]:
    """
    Render the sidebar and return:
        (df_raw, sel_clients, sel_employees, start_d, end_d)

    Returns (None, [], [], None, None) when no file has been uploaded yet.
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
            return None, [], [], None, None

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

        # Date range
        min_d, max_d = df_raw["Date"].min(), df_raw["Date"].max()
        date_range = st.date_input(
            "Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d
        )
        start_d, end_d = (date_range if isinstance(date_range, tuple) and len(date_range) == 2
                          else (min_d, max_d))

        st.divider()
        st.markdown('<p class="section-label">Legend</p>', unsafe_allow_html=True)
        st.markdown(
            '<span class="badge badge-normal">Workday</span>&nbsp;'
            '<span class="badge badge-weekend">Weekend</span>&nbsp;'
            '<span class="badge badge-holiday">Holiday</span>',
            unsafe_allow_html=True,
        )

    return df_raw, sel_clients, sel_employees, start_d, end_d