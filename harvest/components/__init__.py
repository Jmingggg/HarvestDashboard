from .styles import inject_css
from .sidebar import render_sidebar
from .kpi_row import render_kpi_row
from .tab_overview import render_tab_overview
from .tab_client import render_tab_client
from .tab_employee import render_tab_employee
from .tab_pivot import render_tab_pivot

__all__ = [
    "inject_css",
    "render_sidebar",
    "render_kpi_row",
    "render_tab_overview",
    "render_tab_client",
    "render_tab_employee",
    "render_tab_pivot",
]