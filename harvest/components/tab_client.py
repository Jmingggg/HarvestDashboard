"""
Tab 2 – By Client: horizontal bar chart and detail table.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from ..utils.constants import PLOTLY_LAYOUT


def render_tab_client(df: pd.DataFrame) -> None:
    st.markdown("#### Client Hour Breakdown")

    # ── Aggregation ──────────────────────────────────────────────────────
    client_df = (
        df.groupby("Client (Harvest)")
        .agg(
            TotalHours=("Hours", "sum"),
            BillableHours=("Hours", lambda x: x[df.loc[x.index, "Billable"]].sum()),
        )
        .reset_index()
        .sort_values("TotalHours", ascending=False)
    )
    client_df["Utilisation"] = (
        client_df["BillableHours"] / client_df["TotalHours"] * 100
    ).round(1)

    # ── Horizontal bar ───────────────────────────────────────────────────
    fig4 = px.bar(
        client_df,
        x="TotalHours",
        y="Client (Harvest)",
        orientation="h",
        color="Utilisation",
        color_continuous_scale=["#dbeafe", "#2563eb", "#10b981"],
        hover_data={"BillableHours": ":.1f", "Utilisation": ":.1f"},
        labels={"TotalHours": "Total Hours", "Client (Harvest)": "Client"},
        text=client_df["TotalHours"].map(lambda h: f"{h:,.1f} hrs"),
    )
    fig4.update_traces(textposition="outside", textfont=dict(size=12, color="#1e293b"))
    fig4.update_layout(
        **PLOTLY_LAYOUT,
        height=max(300, len(client_df) * 38),
        yaxis=dict(categoryorder="total ascending", gridcolor="#e2e8f0"),
        coloraxis_colorbar=dict(title="Util %"),
        uniformtext_minsize=10,
        uniformtext_mode="hide",
        xaxis=dict(range=[0, client_df["TotalHours"].max() * 1.18]),
    )
    st.plotly_chart(fig4, width="stretch")

    # ── Detail table ─────────────────────────────────────────────────────
    st.markdown("#### Detail Table")
    client_task_df = (
        df.groupby(["Client (Harvest)", "Project Name", "Task"])
        .agg(
            TotalHours=("Hours", "sum"),
            BillableHours=("Hours", lambda x: x[df.loc[x.index, "Billable"]].sum()),
        )
        .reset_index()
    )
    client_totals = client_task_df.groupby("Client (Harvest)")["TotalHours"].transform("sum")
    client_task_df = (
        client_task_df.assign(ClientTotal=client_totals)
        .sort_values(by=["ClientTotal", "TotalHours"], ascending=[False, False])
        .drop(columns="ClientTotal")
    )
    display_client = client_task_df.rename(columns={
        "Client (Harvest)": "Client",
        "Project Name": "Project",
        "Task": "Task",
        "TotalHours": "Total Hours",
        "BillableHours": "Billable Hours",
    })
    st.dataframe(
        display_client.style
            .background_gradient(subset=["Total Hours"], cmap="Blues")
            .format({"Total Hours": "{:.1f}", "Billable Hours": "{:.1f}"}),
        width="stretch",
        hide_index=True,
    )
    
    return display_client
