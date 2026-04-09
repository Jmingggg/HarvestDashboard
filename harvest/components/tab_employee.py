"""
Tab 3 – By Employee: stacked bar, utilisation gauges, client breakdown subplots.
"""
from __future__ import annotations

import math
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..utils.constants import PLOTLY_LAYOUT, CLIENT_PALETTE


def render_tab_employee(df: pd.DataFrame, start_d, end_d) -> None:
    st.markdown("#### Employee Performance")

    # ── Aggregation ──────────────────────────────────────────────────────
    emp_df = (
        df.groupby("Employee")
        .agg(
            BillableHours=("Hours", lambda x: x[df.loc[x.index, "Billable"]].sum()),
            NonBillableHours=("Hours", lambda x: x[df.loc[x.index, "NonBillable"]].sum()),
            OutOfWorkHours=("Hours", lambda x: x[df.loc[x.index, "Out of Work"]].sum()),
            TotalHours=("Hours", "sum"),
        )
        .reset_index()
    )
    emp_df["Utilisation"] = (emp_df["BillableHours"] / emp_df["TotalHours"] * 100).round(1)
    emp_df = emp_df.sort_values("Utilisation", ascending=False)

    # Expected hours (7 hrs × weekdays in date range)
    AVERAGE_HOURS = 7
    all_days = pd.date_range(start=start_d, end=end_d, freq="D")
    expected_hours = sum(AVERAGE_HOURS for d in all_days if d.weekday() < 5)

    # ── Stacked bar per employee ─────────────────────────────────────────
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(name="Billable",     x=emp_df["Employee"], y=emp_df["BillableHours"],    marker_color="#2563eb"))
    fig5.add_trace(go.Bar(name="Non-Billable", x=emp_df["Employee"], y=emp_df["NonBillableHours"], marker_color="#f59e0b"))
    fig5.add_trace(go.Bar(name="Out of Work",  x=emp_df["Employee"], y=emp_df["OutOfWorkHours"],   marker_color="#94a3b8"))
    fig5.add_hline(
        y=expected_hours,
        line=dict(color="#ef4444", width=2, dash="dash"),
        annotation_text=f"Expected: {expected_hours} hrs",
        annotation_position="top right",
        annotation=dict(font=dict(color="#ef4444", size=12), bgcolor="rgba(255,255,255,0.8)"),
    )
    fig5.update_layout(
        **PLOTLY_LAYOUT,
        barmode="stack",
        height=500,
        yaxis=dict(gridcolor="#e2e8f0"),
        xaxis=dict(tickangle=-30),
    )
    st.plotly_chart(fig5, width="stretch")

    # ── Utilisation gauge cards ──────────────────────────────────────────
    st.markdown("#### Utilisation Rate per Employee")
    cols = st.columns(min(len(emp_df), 4))
    for i, (_, row) in enumerate(emp_df.iterrows()):
        color = (
            "#10b981" if row["Utilisation"] >= 70
            else ("#f59e0b" if row["Utilisation"] >= 40 else "#ef4444")
        )
        cols[i % len(cols)].markdown(
            f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px;
                        padding:18px 16px; margin-bottom:12px; text-align:center;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                <div style="font-size:.72rem; color:#64748b; letter-spacing:.08em;
                            text-transform:uppercase; margin-bottom:6px;">
                    {row['Employee']}
                </div>
                <div style="font-size:1.8rem; font-weight:700; color:{color};
                            font-family:'DM Serif Display',serif;">
                    {row['Utilisation']:.0f}%
                </div>
                <div style="font-size:.75rem; color:#94a3b8; margin-top:4px;">
                    {row['BillableHours']:.1f} / {row['TotalHours']:.1f} hrs
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Per-employee client breakdown (3-col subplot grid) ───────────────
    st.markdown("#### Client Hours per Employee")
    emp_client  = df.groupby(["Employee", "Client (Harvest)"])["Hours"].sum().reset_index()
    all_employees = emp_df["Employee"].tolist()
    n_emp, n_cols = len(all_employees), 3
    n_rows = math.ceil(n_emp / n_cols)

    all_clients   = sorted(emp_client["Client (Harvest)"].unique().tolist())
    client_colors = {c: CLIENT_PALETTE[i % len(CLIENT_PALETTE)] for i, c in enumerate(all_clients)}

    fig6 = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=all_employees,
        vertical_spacing=0.14,
        horizontal_spacing=0.06,
    )

    legend_added: set[str] = set()
    for idx, emp in enumerate(all_employees):
        r = idx // n_cols + 1
        c = idx % n_cols + 1
        emp_data = (
            emp_client[emp_client["Employee"] == emp]
            .sort_values("Hours", ascending=False)
        )
        for _, row in emp_data.iterrows():
            client  = row["Client (Harvest)"]
            show_lg = client not in legend_added
            if show_lg:
                legend_added.add(client)
            fig6.add_trace(
                go.Bar(
                    name=client,
                    x=[client],
                    y=[row["Hours"]],
                    marker_color=client_colors[client],
                    showlegend=show_lg,
                    legendgroup=client,
                    hovertemplate=f"<b>{client}</b><br>{row['Hours']:.1f} hrs<extra>{emp}</extra>",
                ),
                row=r, col=c,
            )

    fig6.update_layout(**PLOTLY_LAYOUT, height=280 * n_rows, barmode="group", showlegend=False)
    fig6.update_xaxes(showticklabels=False, showgrid=False)
    fig6.update_yaxes(gridcolor="#e2e8f0")
    for ann in fig6.layout.annotations:
        ann.font.update(size=12, color="#1e293b", family="DM Sans")

    st.plotly_chart(fig6, width="stretch")