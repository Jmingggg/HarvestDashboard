"""
Date utility helpers: holiday calendar, date classification, and column labelling.
"""
import holidays

# Malaysian public holidays — Selangor subdivision, 2023-2028
MY_HOLIDAYS = holidays.country_holidays("MY", subdiv="SGR", years=range(2023, 2029))


def classify_date(d) -> str:
    """Return 'holiday', 'weekend', or 'workday' for a given date."""
    if d in MY_HOLIDAYS:
        return "holiday"
    if d.weekday() in (5, 6):
        return "weekend"
    return "workday"


def col_label(d) -> str:
    """Return a display-friendly column label with emoji prefix for pivot table headers."""
    cls = classify_date(d.date())
    if cls == "holiday":
        return f"🔴 {d.strftime('%d %b')}"
    if cls == "weekend":
        return f"🟡 {d.strftime('%d %b')}"
    return d.strftime("%d %b")