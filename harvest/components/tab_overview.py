"""
Tab 1 – Overview: donut chart, daily billable trend, weekly stacked bar,
and a non-billable breakdown (project name x task).
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..utils.constants import PLOTLY_LAYOUT


def render_tab_overview(
    df_raw: pd.DataFrame,
    df: pd.DataFrame,
    billable_h: float,
    nonbill_h: float,
    oow_h: float,
    util_rate: float
) -> None:
    c1, c2 = st.columns(2)

    # Donut: hour type split
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

    # Line: daily billable trend
    with c2:
        st.markdown("#### Daily Billable Trend")
        daily = df_raw.groupby("Date")["Hours"].sum().reset_index()
        daily["Date"] = pd.to_datetime(daily["Date"])
        daily_b = df_raw[df_raw["Billable"]].groupby("Date")["Hours"].sum().reset_index()
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

    # Stacked bar: weekly
    st.markdown("#### Weekly Hours by Type")
    weekly = df_raw.copy()
    weekly["Week"] = pd.to_datetime(weekly["Date"]).dt.to_period("W").dt.start_time
    weekly = weekly.groupby(["Week", "Type"])["Hours"].sum().reset_index()
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

    # Non-Billable Breakdown
    nb_df = df[df["NonBillable"]].copy()
    if nb_df.empty:
        return

    st.markdown("#### Non-Billable Hours Breakdown")
    st.markdown(
        '<p style="color:#64748b; font-size:0.88rem; margin-top:-8px; margin-bottom:12px;">'
        "All hours logged as <strong>Productive</strong> (non-billable) — "
        "broken down by project and task."
        "</p>",
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns(2)

    # Left: sunburst Project Name -> Task
    with col_left:
        st.markdown("##### Project -> Task (Sunburst)")

        sun_df = (
            nb_df.groupby(["Project Name", "Task"])["Hours"]
            .sum()
            .reset_index()
        )

        fig_sun = px.sunburst(
            sun_df,
            path=["Project Name", "Task"],
            values="Hours",
            color="Project Name",
            color_discrete_sequence=[
                "#f59e0b", "#fb923c", "#fbbf24", "#f97316",
                "#fde68a", "#fdba74", "#fef3c7",
            ],
            hover_data={"Hours": ":.1f"},
        )
        fig_sun.update_traces(
            textinfo="label+percent entry",
            hovertemplate="<b>%{label}</b><br>%{value:.1f} hrs<br>%{percentRoot:.1%} of total<extra></extra>",
            insidetextorientation="radial",
        )
        fig_sun.update_layout(**PLOTLY_LAYOUT, height=400)
        st.plotly_chart(fig_sun, width="stretch")

    # Right: horizontal stacked bar Task coloured by Project Name
    with col_right:
        st.markdown("##### Hours by Task (coloured by Project)")

        task_proj_df = (
            nb_df.groupby(["Task", "Project Name"])["Hours"]
            .sum()
            .reset_index()
        )
        task_totals = task_proj_df.groupby("Task")["Hours"].sum().sort_values(ascending=True)
        ordered_tasks = task_totals.index.tolist()

        all_projects = nb_df["Project Name"].unique().tolist()
        palette = [
            "#f59e0b", "#fb923c", "#fbbf24", "#f97316",
            "#fde68a", "#fdba74", "#fef3c7", "#d97706",
        ]
        proj_palette = {proj: palette[i % len(palette)] for i, proj in enumerate(all_projects)}

        fig_bar = go.Figure()
        for proj, grp in task_proj_df.groupby("Project Name"):
            task_hours = {row["Task"]: row["Hours"] for _, row in grp.iterrows()}
            fig_bar.add_trace(go.Bar(
                name=proj,
                y=ordered_tasks,
                x=[task_hours.get(t, 0) for t in ordered_tasks],
                orientation="h",
                marker_color=proj_palette.get(proj, "#f59e0b"),
                hovertemplate=f"<b>{proj}</b><br>%{{y}}: %{{x:.1f}} hrs<extra></extra>",
            ))

        fig_bar.update_layout(
            **PLOTLY_LAYOUT,
            barmode="stack",
            height=400,
            yaxis=dict(gridcolor="#e2e8f0"),
            xaxis=dict(gridcolor="#e2e8f0", title="Hours"),
        )
        fig_bar.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=11),
            bgcolor="rgba(0,0,0,0)",
        ))
        st.plotly_chart(fig_bar, width="stretch")

    # Summary table
    st.markdown("##### Non-Billable Summary Table")
    summary_df = (
        nb_df.groupby(["Project Name", "Task"])
        .agg(Hours=("Hours", "sum"), Entries=("Hours", "count"))
        .reset_index()
        .sort_values(["Project Name", "Hours"], ascending=[True, False])
    )
    summary_df["Hours"] = summary_df["Hours"].round(2)
    total_nb = summary_df["Hours"].sum()
    summary_df["% of Non-Billable"] = (summary_df["Hours"] / total_nb * 100).round(1).astype(str) + "%"

    st.dataframe(
        summary_df.style
            .background_gradient(subset=["Hours"], cmap="YlOrBr")
            .format({"Hours": "{:.1f}", "Entries": "{:,}"}),
        hide_index=True,
        width="stretch",
    )