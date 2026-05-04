"""
Data loading and preprocessing for the Harvest Resource Dashboard.
"""
import pandas as pd
import streamlit as st

from .date_helpers import classify_date


@st.cache_data
def load_data(file) -> pd.DataFrame:
    """
    Load a Harvest CSV export, parse dates, derive boolean flag columns,
    and classify each date as workday / weekend / holiday.
    """
    df = pd.read_csv(file)
    df["Date"] = pd.to_datetime(df["Date"], format="mixed").dt.date
    df["Billable"] = df["Type"] == "Billable"
    df["Out of Work"] = df["Type"] == "Out of Work"
    df["NonBillable"] = (~df["Billable"]) & (~df["Out of Work"])
    df["DateClass"] = df["Date"].map(classify_date)
    return df


def apply_filters(
    df_raw: pd.DataFrame,
    sel_clients: list,
    sel_employees: list,
    sel_billable: list,
    start_d,
    end_d,
) -> pd.DataFrame:
    """Return a filtered copy of df_raw based on sidebar selections."""
    # Map friendly label → boolean column name
    _BILLABLE_MAP = {
        "Billable": "Billable",
        "Non-Billable": "NonBillable",
        "OOW": "Out of Work",
    }
    billable_mask = pd.Series(False, index=df_raw.index)
    for label in sel_billable:
        col = _BILLABLE_MAP.get(label)
        if col and col in df_raw.columns:
            billable_mask |= df_raw[col]

    return df_raw[
        df_raw["Client (Harvest)"].isin(sel_clients)
        & df_raw["Employee"].isin(sel_employees)
        & billable_mask
        & df_raw["Date"].between(start_d, end_d)
    ].copy()


def fmt_hours(h: float) -> str:
    """Format a float as a human-readable hours string."""
    return f"{h:,.1f} hrs"