import math
import streamlit as st
import holidays
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Harvest · Resource Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:        #f5f7fa;
    --surface:   #ffffff;
    --card:      #ffffff;
    --border:    #e2e8f0;
    --accent:    #2563eb;
    --accent2:   #f59e0b;
    --accent3:   #10b981;
    --danger:    #ef4444;
    --text:      #1e293b;
    --muted:     #64748b;
    --weekend:   rgba(245,158,11,0.15);
    --holiday:   rgba(239,68,68,0.15);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}

/* Background */
.stApp { background: var(--bg); }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--border);
    box-shadow: 2px 0 12px rgba(0,0,0,0.06);
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--text);
}

/* Headings */
h1, h2, h3, h4 { font-family: 'DM Serif Display', serif; color: var(--text); }

/* Metric cards */
[data-testid="metric-container"] {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 700; color: var(--accent) !important; }
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 0.8rem !important; letter-spacing: .08em; text-transform: uppercase; }
[data-testid="stMetricDelta"] { font-size: 0.85rem !important; }

/* Divider */
hr { border-color: var(--border); }

/* Selectbox / multiselect */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #f0f6ff;
    border: 2px dashed #bfdbfe;
    border-radius: 16px;
    padding: 16px;
}

/* Dataframe / table */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid var(--border); }

/* Tabs */
[data-testid="stTabs"] button {
    color: var(--muted) !important;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

/* Badge helpers */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: .04em;
}
.badge-weekend { background: rgba(245,158,11,.18); color: #b45309; }
.badge-holiday { background: rgba(239,68,68,.15); color: #dc2626; }
.badge-normal  { background: rgba(37,99,235,.10); color: #2563eb; }

/* Section label */
.section-label {
    font-size: 1rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ────────────────────────────────────────────────────────────────────
MY_HOLIDAYS = holidays.country_holidays("MY", subdiv="SGR", years=range(2023, 2029))

def classify_date(d):
    """Return 'holiday', 'weekend', or 'workday'."""
    if d in MY_HOLIDAYS:
        return "holiday"
    if d.weekday() in (5, 6):
        return "weekend"
    return "workday"

@st.cache_data
def load_data(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df["Billable"]    = df["Type"] == "Billable"
    df["Out of Work"] = df["Type"] == "Out of Work"
    df["NonBillable"] = (~df["Billable"]) & (~df["Out of Work"])
    df["DateClass"]   = df["Date"].map(classify_date)
    return df

def fmt_hours(h: float) -> str:
    return f"{h:,.1f} hrs"

COLORS = {
    "billable":     "#4f8ef7",
    "nonbillable":  "#f7974f",
    "outofwork":    "#6b7394",
    "weekend_fill": "rgba(247,151,79,0.25)",
    "holiday_fill": "rgba(247,97,79,0.25)",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#1e293b"),
    margin=dict(l=0, r=0, t=36, b=0),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
    colorway=["#2563eb","#f59e0b","#10b981","#ef4444","#8b5cf6","#f97316"],
)

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌾 Harvest")
    st.markdown('<p class="section-label">Resource Dashboard</p>', unsafe_allow_html=True)
    st.divider()

    uploaded = st.file_uploader("Upload CSV", type=["csv"], help="Upload a Harvest Persuasion Employees CSV export.")

    if uploaded:
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
        date_range = st.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_d, end_d = date_range
        else:
            start_d, end_d = min_d, max_d

        st.divider()
        st.markdown('<p class="section-label">Legend</p>', unsafe_allow_html=True)
        st.markdown("""
        <span class="badge badge-normal">Workday</span>&nbsp;
        <span class="badge badge-weekend">Weekend</span>&nbsp;
        <span class="badge badge-holiday">Holiday</span>
        """, unsafe_allow_html=True)

# ─── Main ───────────────────────────────────────────────────────────────────────
if not uploaded:
    st.markdown("""
    <div style="text-align:center; padding: 80px 40px;">
        <div style="font-size:4rem; margin-bottom:16px;">🌾</div>
        <h1 style="font-family:'DM Serif Display',serif; font-size:2.8rem; margin-bottom:8px;">Harvest Resource Dashboard</h1>
        <p style="color:#64748b; font-size:1.05rem; max-width:480px; margin:0 auto 32px;">
            Upload your Harvest Persuasion Employees CSV export from the sidebar to get started.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── Filter data ────────────────────────────────────────────────────────────────
df = df_raw[
    df_raw["Client (Harvest)"].isin(sel_clients) &
    df_raw["Employee"].isin(sel_employees) &
    df_raw["Date"].between(start_d, end_d)
].copy()

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ─── KPI row ────────────────────────────────────────────────────────────────────
total_h      = df["Hours"].sum()
billable_h   = df[df["Billable"]]["Hours"].sum()
nonbill_h    = df[df["NonBillable"]]["Hours"].sum()
oow_h        = df[df["Out of Work"]]["Hours"].sum()
util_rate    = billable_h / total_h * 100 if total_h else 0
num_emp      = df["Employee"].nunique()

st.markdown('<p class="section-label" style="margin-top:8px;">Overview</p>', unsafe_allow_html=True)
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Employees",      num_emp)
k2.metric("Total Hours",    fmt_hours(total_h))
k3.metric("Billable",       fmt_hours(billable_h), f"{util_rate:.1f}% of total")
k4.metric("Non-Billable",   fmt_hours(nonbill_h))
k5.metric("Out of Work",    fmt_hours(oow_h))
k6.metric("Utilisation",    f"{util_rate:.1f}%", delta_color="normal")

st.divider()

# ─── Tabs ───────────────────────────────────────────────────────────────────────
tab_overview, tab_client, tab_employee, tab_pivot = st.tabs([
    "📊 Overview", "🏢 By Client", "👤 By Employee", "📅 Hours Pivot"
])

# ══════════════════════════════════════════════════════════════════════
# TAB 1 – OVERVIEW
# ══════════════════════════════════════════════════════════════════════
with tab_overview:
    c1, c2 = st.columns(2)

    # Donut – hour type split
    with c1:
        st.markdown("#### Hours Breakdown")
        labels = ["Billable", "Non-Billable", "Out of Work"]
        values = [billable_h, nonbill_h, oow_h]
        fig = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=.62,
            marker=dict(colors=["#2563eb","#f59e0b","#94a3b8"],
                        line=dict(color="#ffffff", width=2)),
            textinfo="label+percent",
            hovertemplate="%{label}: <b>%{value:.1f} hrs</b><extra></extra>"
        ))
        fig.add_annotation(text=f"<b>{util_rate:.0f}%</b><br><span style='font-size:11px'>utilised</span>",
                           showarrow=False, font=dict(size=22, color="#1e293b"))
        fig.update_layout(**PLOTLY_LAYOUT, height=320)
        st.plotly_chart(fig, width="stretch")

    # Line – daily billable hours trend
    with c2:
        st.markdown("#### Daily Billable Trend")
        daily = df.groupby("Date")["Hours"].sum().reset_index()
        daily["Date"] = pd.to_datetime(daily["Date"])
        daily_b = df[df["Billable"]].groupby("Date")["Hours"].sum().reset_index()
        daily_b["Date"] = pd.to_datetime(daily_b["Date"])
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=daily["Date"], y=daily["Hours"],
            name="Total", mode="lines",
            line=dict(color="#cbd5e1", width=2),
            fill="tozeroy", fillcolor="rgba(203,213,225,0.3)"
        ))
        fig2.add_trace(go.Scatter(
            x=daily_b["Date"], y=daily_b["Hours"],
            name="Billable", mode="lines",
            line=dict(color="#2563eb", width=2.5),
            fill="tozeroy", fillcolor="rgba(37,99,235,0.12)"
        ))
        fig2.update_layout(**PLOTLY_LAYOUT, height=320,
                           yaxis=dict(gridcolor="#e2e8f0"),
                           xaxis=dict(gridcolor="#e2e8f0"))
        st.plotly_chart(fig2, width="stretch")

    # Stacked bar – weekly
    st.markdown("#### Weekly Hours by Type")
    df["Week"] = pd.to_datetime(df["Date"]).dt.to_period("W").dt.start_time
    weekly = df.groupby(["Week","Type"])["Hours"].sum().reset_index()
    fig3 = px.bar(weekly, x="Week", y="Hours", color="Type",
                  color_discrete_map={"Billable":"#4f8ef7","Non Billable":"#f7974f","Out of Work":"#6b7394"},
                  barmode="stack")
    fig3.update_layout(**PLOTLY_LAYOUT, height=300,
                       yaxis=dict(gridcolor="#e2e8f0"), xaxis=dict(gridcolor="#e2e8f0"))
    st.plotly_chart(fig3, width="stretch")


# ══════════════════════════════════════════════════════════════════════
# TAB 2 – BY CLIENT
# ══════════════════════════════════════════════════════════════════════
with tab_client:
    st.markdown("#### Client Hour Breakdown")
    client_df = df.groupby("Client (Harvest)").agg(
        TotalHours=("Hours","sum"),
        BillableHours=("Hours", lambda x: x[df.loc[x.index,"Billable"]].sum()),
    ).reset_index().sort_values("TotalHours", ascending=False)
    client_df["Utilisation"] = (client_df["BillableHours"] / client_df["TotalHours"] * 100).round(1)

    fig4 = px.bar(client_df, x="TotalHours", y="Client (Harvest)",
                  orientation="h", color="Utilisation",
                  color_continuous_scale=["#dbeafe","#2563eb","#10b981"],
                  hover_data={"BillableHours":":.1f","Utilisation":":.1f"},
                  labels={"TotalHours":"Total Hours","Client (Harvest)":"Client"})
    fig4.update_layout(**PLOTLY_LAYOUT, height=max(300, len(client_df)*38),
                       yaxis=dict(categoryorder="total ascending", gridcolor="#e2e8f0"),
                       coloraxis_colorbar=dict(title="Util %"))
    st.plotly_chart(fig4, width="stretch")

    # Table
    st.markdown("#### Detail Table")
    display_client = client_df.rename(columns={
        "Client (Harvest)":"Client",
        "TotalHours":"Total Hours",
        "BillableHours":"Billable Hours",
        "Utilisation":"Utilisation %"
    })
    st.dataframe(
        display_client.style
            .background_gradient(subset=["Total Hours"], cmap="Blues")
            .format({"Total Hours":"{:.1f}","Billable Hours":"{:.1f}","Utilisation %":"{:.1f}%"}),
        width="stretch", hide_index=True
    )


# ══════════════════════════════════════════════════════════════════════
# TAB 3 – BY EMPLOYEE
# ══════════════════════════════════════════════════════════════════════
with tab_employee:
    st.markdown("#### Employee Performance")

    emp_df = df.groupby("Employee").agg(
        BillableHours=("Hours", lambda x: x[df.loc[x.index,"Billable"]].sum()),
        NonBillableHours=("Hours", lambda x: x[df.loc[x.index,"NonBillable"]].sum()),
        OutOfWorkHours=("Hours", lambda x: x[df.loc[x.index,"Out of Work"]].sum()),
        TotalHours=("Hours","sum")
    ).reset_index()
    emp_df["Utilisation"] = (emp_df["BillableHours"] / emp_df["TotalHours"] * 100).round(1)
    emp_df = emp_df.sort_values("Utilisation", ascending=False)
    
    # Expected hours = every weekday (Mon-Fri) in selected date range x n hrs
    average_hours = 7
    all_days = pd.date_range(start=start_d, end=end_d, freq="D")
    expected_hours = sum(average_hours for d in all_days if d.weekday() < 5)

    fig5 = go.Figure()
    fig5.add_trace(go.Bar(name="Billable", x=emp_df["Employee"], y=emp_df["BillableHours"],
                          marker_color="#2563eb"))
    fig5.add_trace(go.Bar(name="Non-Billable", x=emp_df["Employee"], y=emp_df["NonBillableHours"],
                          marker_color="#f59e0b"))
    fig5.add_trace(go.Bar(name="Out of Work", x=emp_df["Employee"], y=emp_df["OutOfWorkHours"],
                          marker_color="#94a3b8"))
    fig5.add_hline(
        y=expected_hours,
        line=dict(color="#ef4444", width=2, dash="dash"),
        annotation_text=f"Expected: {expected_hours} hrs",
        annotation_position="top right",
        annotation=dict(font=dict(color="#ef4444", size=12), bgcolor="rgba(255,255,255,0.8)"),
    )
    fig5.update_layout(**PLOTLY_LAYOUT, barmode="stack", height=500,
                       yaxis=dict(gridcolor="#e2e8f0"), xaxis=dict(tickangle=-30))
    st.plotly_chart(fig5, width="stretch")

    # Utilisation gauge row
    st.markdown("#### Utilisation Rate per Employee")
    cols = st.columns(min(len(emp_df), 4))
    for i, (_, row) in enumerate(emp_df.iterrows()):
        col = cols[i % len(cols)]
        color = "#10b981" if row["Utilisation"] >= 70 else ("#f59e0b" if row["Utilisation"] >= 40 else "#ef4444")
        col.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px;
                    padding:18px 16px; margin-bottom:12px; text-align:center;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <div style="font-size:.72rem; color:#64748b; letter-spacing:.08em; text-transform:uppercase; margin-bottom:6px;">
                {row['Employee']}
            </div>
            <div style="font-size:1.8rem; font-weight:700; color:{color}; font-family:'DM Serif Display',serif;">
                {row['Utilisation']:.0f}%
            </div>
            <div style="font-size:.75rem; color:#94a3b8; margin-top:4px;">
                {row['BillableHours']:.1f} / {row['TotalHours']:.1f} hrs
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Per-employee client breakdown — 3-col subplot grid
    st.markdown("#### Client Hours per Employee")
    emp_client = df.groupby(["Employee", "Client (Harvest)"])["Hours"].sum().reset_index()
    all_employees = emp_df["Employee"].tolist()
    n_emp  = len(all_employees)
    n_cols = 3
    n_rows = math.ceil(n_emp / n_cols)

    all_clients = sorted(emp_client["Client (Harvest)"].unique().tolist())
    palette = ["#2563eb","#f59e0b","#10b981","#ef4444","#8b5cf6","#f97316",
               "#06b6d4","#ec4899","#84cc16","#6366f1"]
    client_colors = {c: palette[i % len(palette)] for i, c in enumerate(all_clients)}

    def short_name(e):
        parts = e.split()
        return parts[0] + (" " + parts[1][0] + "." if len(parts) > 1 else "")

    subplot_titles = [short_name(e) for e in all_employees]

    fig6 = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=subplot_titles,
        vertical_spacing=0.14,
        horizontal_spacing=0.06,
    )

    legend_added = set()
    for idx, emp in enumerate(all_employees):
        r = idx // n_cols + 1
        c = idx % n_cols + 1
        emp_data = emp_client[emp_client["Employee"] == emp].sort_values("Hours", ascending=False)
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

    fig6.update_layout(
        **PLOTLY_LAYOUT,
        height=280 * n_rows,
        barmode="group",
    )
    fig6.update_layout(showlegend=False)
    fig6.update_xaxes(showticklabels=False, showgrid=False)
    fig6.update_yaxes(gridcolor="#e2e8f0")
    for ann in fig6.layout.annotations:
        ann.font.update(size=12, color="#1e293b", family="DM Sans")

    st.plotly_chart(fig6, width="stretch")


# ══════════════════════════════════════════════════════════════════════
# TAB 4 – HOURS PIVOT (with weekend/holiday highlights)
# ══════════════════════════════════════════════════════════════════════
with tab_pivot:
    st.markdown("#### Daily Hours Pivot — Weekend & Holiday Highlights")
    st.markdown("""
    <span class="badge badge-normal">Workday</span>&nbsp;
    <span class="badge badge-weekend">Weekend</span>&nbsp;
    <span class="badge badge-holiday">🏖 Public Holiday</span>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    pivot = df.pivot_table(
        index="Employee", columns="Date",
        values="Hours", aggfunc="sum", fill_value=0
    )
    pivot.columns = pd.to_datetime(pivot.columns)
    pivot = pivot.sort_index(axis=1)

    # Build styler
    def style_pivot(val, date):
        cls = classify_date(date.date() if hasattr(date, "date") else date)
        if cls == "holiday":
            return "background-color: rgba(247,97,79,0.22); color: #f7614f; font-weight:600;"
        elif cls == "weekend":
            return "background-color: rgba(247,151,79,0.18); color: #f7974f; font-weight:600;"
        elif val > 0:
            return "color: #4f8ef7;"
        return "color: #2a2f45;"

    styled = pivot.style

    for col in pivot.columns:
        styled = styled.map(
            lambda v, c=col: style_pivot(v, c),
            subset=[col]
        )

    styled = styled.format(lambda x: f"{x:.1f}" if x > 0 else "–")

    # Rename columns to readable date strings with class prefix
    def col_label(d):
        cls = classify_date(d.date())
        if cls == "holiday": return f"🔴 {d.strftime('%d %b')}"
        if cls == "weekend": return f"🟡 {d.strftime('%d %b')}"
        return d.strftime("%d %b")

    pivot.columns = [col_label(c) for c in pivot.columns]
    styled = pivot.style

    for col in pivot.columns:
        if col.startswith("🔴"):
            styled = styled.map(
                lambda v: "background-color: rgba(239,68,68,0.15); color: #dc2626; font-weight:600;" if v > 0
                          else "background-color: rgba(239,68,68,0.07); color: #94a3b8;",
                subset=[col]
            )
        elif col.startswith("🟡"):
            styled = styled.map(
                lambda v: "background-color: rgba(245,158,11,0.18); color: #b45309; font-weight:600;" if v > 0
                          else "background-color: rgba(245,158,11,0.08); color: #94a3b8;",
                subset=[col]
            )
        else:
            styled = styled.map(
                lambda v: "color: #2563eb; font-weight:500;" if v > 0 else "color: #cbd5e1;",
                subset=[col]
            )

    styled = styled.format(lambda x: f"{x:.1f}" if x > 0 else "–")

    st.dataframe(styled, width="stretch")

    # Row totals helper
    st.divider()
    st.markdown("#### Employee Summary Row")
    summary = df.groupby("Employee").agg(
        Total=("Hours","sum"),
        Billable=("Hours", lambda x: x[df.loc[x.index,"Billable"]].sum()),
        Weekend=("Hours", lambda x: x[df.loc[x.index,"DateClass"] == "weekend"].sum()),
        Holiday=("Hours", lambda x: x[df.loc[x.index,"DateClass"] == "holiday"].sum()),
    ).reset_index()
    summary["Util %"] = (summary["Billable"] / summary["Total"] * 100).round(1)
    summary["Weekend %"] = (summary["Weekend"] / summary["Total"] * 100).round(1)
    st.dataframe(
        summary.style
            .format({"Total":"{:.1f}","Billable":"{:.1f}",
                     "Weekend":"{:.1f}","Holiday":"{:.1f}",
                     "Util %":"{:.1f}%","Weekend %":"{:.1f}%"})
            .background_gradient(subset=["Util %"], cmap="Blues"),
        width="stretch", hide_index=True
    )
