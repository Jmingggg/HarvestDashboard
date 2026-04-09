"""
KPI row component: renders the six top-level metric cards.
"""
import streamlit as st
import pandas as pd

from ..utils.data_loader import fmt_hours


def render_kpi_row(df: pd.DataFrame) -> tuple[float, float, float]:
    """
    Render the KPI metrics strip and return (total_h, billable_h, util_rate)
    for downstream use by chart components.
    """
    total_h    = df["Hours"].sum()
    billable_h = df[df["Billable"]]["Hours"].sum()
    nonbill_h  = df[df["NonBillable"]]["Hours"].sum()
    oow_h      = df[df["Out of Work"]]["Hours"].sum()
    util_rate  = billable_h / total_h * 100 if total_h else 0
    num_emp    = df["Employee"].nunique()

    st.markdown('<p class="section-label" style="margin-top:8px;">Overview</p>', unsafe_allow_html=True)
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Employees",   num_emp)
    k2.metric("Total Hours", fmt_hours(total_h))
    k3.metric("Billable",    fmt_hours(billable_h), f"{util_rate:.1f}% of total")
    k4.metric("Non-Billable", fmt_hours(nonbill_h))
    k5.metric("Out of Work", fmt_hours(oow_h))
    k6.metric("Utilisation", f"{util_rate:.1f}%", delta_color="normal")

    st.divider()
    return total_h, billable_h, util_rate