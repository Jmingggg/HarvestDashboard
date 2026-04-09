"""
Tab 1 – Overview: donut chart, daily billable trend, weekly stacked bar.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from ..utils.constants import PLOTLY_LAYOUT


def render_tab_overview(df: pd.DataFrame, billable_h: float, nonbill_h: float,
                         oow_h: float, util_rate: float) -> None:
    c1, c2 = st.columns(2)

    # ── Donut: hour type split ───────────────────────────────────────────
    with c1:
        st.markdown("#### Hours Breakdown")
        fig = go.Figure(go.Pie(
            labels=["Billable", "Non-Billable", "Out of Work"],
            values=[billable_h, nonbill_h, oow_h],
            hole=.62,
            marker=dict(
                colors=["#2563eb", "#f59e0b", "#94a3b8"],
                line=dict(color="#ffffff", width=2),
            ),
            textinfo="label+percent",
            hovertemplate="%{label}: <b>%{value:.1f} hrs</b><extra></extra>",
        ))
        fig.add_annotation(
            text=f"<b>{util_rate:.0f}%</b><br><span style='font-size:11px'>utilised</span>",
            showarrow=False,
            font=dict(size=22, color="#1e293b"),
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=320)
        st.plotly_chart(fig, width="stretch")

    # ── Line: daily billable trend ───────────────────────────────────────
    with c2:
        st.markdown("#### Daily Billable Trend")
        daily   = df.groupby("Date")["Hours"].sum().reset_index()
        daily["Date"] = pd.to_datetime(daily["Date"])
        daily_b = df[df["Billable"]].groupby("Date")["Hours"].sum().reset_index()
        daily_b["Date"] = pd.to_datetime(daily_b["Date"])

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=daily["Date"], y=daily["Hours"],
            name="Total", mode="lines",
            line=dict(color="#cbd5e1", width=2),
            fill="tozeroy", fillcolor="rgba(203,213,225,0.3)",
        ))
        fig2.add_trace(go.Scatter(
            x=daily_b["Date"], y=daily_b["Hours"],
            name="Billable", mode="lines",
            line=dict(color="#2563eb", width=2.5),
            fill="tozeroy", fillcolor="rgba(37,99,235,0.12)",
        ))
        fig2.update_layout(**PLOTLY_LAYOUT, height=320,
                           yaxis=dict(gridcolor="#e2e8f0"),
                           xaxis=dict(gridcolor="#e2e8f0"))
        st.plotly_chart(fig2, width="stretch")

    # ── Stacked bar: weekly ──────────────────────────────────────────────
    st.markdown("#### Weekly Hours by Type")
    df = df.copy()
    df["Week"] = pd.to_datetime(df["Date"]).dt.to_period("W").dt.start_time
    weekly = df.groupby(["Week", "Type"])["Hours"].sum().reset_index()
    fig3 = px.bar(
        weekly, x="Week", y="Hours", color="Type",
        color_discrete_map={
            "Billable": "#4f8ef7",
            "Non Billable": "#f7974f",
            "Out of Work": "#6b7394",
        },
        barmode="stack",
    )
    fig3.update_layout(**PLOTLY_LAYOUT, height=300,
                       yaxis=dict(gridcolor="#e2e8f0"),
                       xaxis=dict(gridcolor="#e2e8f0"))
    st.plotly_chart(fig3, width="stretch")