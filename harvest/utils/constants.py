"""
Shared constants: colours, Plotly layout defaults, and palette.
"""

COLORS = {
    "billable": "#4f8ef7",
    "nonbillable": "#f7974f",
    "outofwork": "#6b7394",
    "weekend_fill": "rgba(247,151,79,0.25)",
    "holiday_fill": "rgba(247,97,79,0.25)",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#1e293b"),
    margin=dict(l=0, r=0, t=36, b=0),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
    colorway=["#2563eb", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#f97316"],
)

CLIENT_PALETTE = [
    "#2563eb", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6",
    "#f97316", "#06b6d4", "#ec4899", "#84cc16", "#6366f1",
    "#14b8a6", "#f43f5e", "#a855f7", "#eab308", "#22c55e",
    "#0ea5e9", "#d946ef", "#fb923c", "#4ade80", "#818cf8",
]