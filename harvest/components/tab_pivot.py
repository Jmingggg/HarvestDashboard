"""
Tab 4 – Hours Pivot: styled daily pivot table with weekend/holiday highlights
and an employee summary row.
"""
import streamlit as st
import pandas as pd

from ..utils.date_helpers import classify_date, col_label


def _style_cell(v: float, col_name: str) -> str:
    """Return inline CSS for a single pivot cell based on its column class."""
    if col_name.startswith("🔴"):
        return (
            "background-color: rgba(239,68,68,0.15); color: #dc2626; font-weight:600;"
            if v > 0
            else "background-color: rgba(239,68,68,0.07); color: #94a3b8;"
        )
    if col_name.startswith("🟡"):
        return (
            "background-color: rgba(245,158,11,0.18); color: #b45309; font-weight:600;"
            if v > 0
            else "background-color: rgba(245,158,11,0.08); color: #94a3b8;"
        )
    # Normal workday
    return "color: #2563eb; font-weight:500;" if v > 0 else "color: #cbd5e1;"


def render_tab_pivot(df: pd.DataFrame) -> None:
    st.markdown("#### Daily Hours Pivot — Weekend & Holiday Highlights")
    st.markdown(
        '<span class="badge badge-normal">Workday</span>&nbsp;'
        '<span class="badge badge-weekend">Weekend</span>&nbsp;'
        '<span class="badge badge-holiday">🏖 Public Holiday</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # Build pivot
    pivot = df.pivot_table(
        index="Employee",
        columns="Date",
        values="Hours",
        aggfunc="sum",
        fill_value=0,
    )
    pivot.columns = pd.to_datetime(pivot.columns)
    pivot = pivot.sort_index(axis=1)

    # Relabel columns with emoji prefixes
    pivot.columns = [col_label(c) for c in pivot.columns]

    # Apply per-column styling
    styled = pivot.style
    for col in pivot.columns:
        styled = styled.map(lambda v, c=col: _style_cell(v, c), subset=[col])
    styled = styled.format(lambda x: f"{x:.1f}" if x > 0 else "–")

    st.dataframe(styled, width="stretch")

    # ── Employee summary row ─────────────────────────────────────────────
    st.divider()
    st.markdown("#### Employee Summary Row")
    summary = df.groupby("Employee").agg(
        Total=("Hours", "sum"),
        Billable=("Hours", lambda x: x[df.loc[x.index, "Billable"]].sum()),
        Weekend=("Hours", lambda x: x[df.loc[x.index, "DateClass"] == "weekend"].sum()),
        Holiday=("Hours", lambda x: x[df.loc[x.index, "DateClass"] == "holiday"].sum()),
    ).reset_index()
    summary["Util %"]    = (summary["Billable"] / summary["Total"] * 100).round(1)
    summary["Weekend %"] = (summary["Weekend"]  / summary["Total"] * 100).round(1)

    st.dataframe(
        summary.style
            .format({
                "Total": "{:.1f}", "Billable": "{:.1f}",
                "Weekend": "{:.1f}", "Holiday": "{:.1f}",
                "Util %": "{:.1f}%", "Weekend %": "{:.1f}%",
            })
            .background_gradient(subset=["Util %"], cmap="Blues"),
        width="stretch",
        hide_index=True,
    )