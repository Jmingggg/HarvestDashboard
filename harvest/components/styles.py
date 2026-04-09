"""
Injects the global custom CSS for the Harvest dashboard.
"""
import streamlit as st

CSS = """
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
"""


def inject_css() -> None:
    """Inject global dashboard CSS into the Streamlit app."""
    st.markdown(CSS, unsafe_allow_html=True)