"""Shared AOI configuration for P1/P2/P4 export scripts.

Keep this file as the single source of truth for the Avanos/Nevsehir
working bbox. Scripts that start Earth Engine exports should import this
constant instead of carrying their own hardcoded rectangle.
"""

from __future__ import annotations

BBOX_WGS84 = (34.60, 38.40, 35.00, 38.90)
AOI_LABEL = "avanos_nevsehir_extended_v2"


def bbox_list() -> list[float]:
    return list(BBOX_WGS84)


def bbox_text() -> str:
    west, south, east, north = BBOX_WGS84
    return f"lon {west:.2f}-{east:.2f}, lat {south:.2f}-{north:.2f}"


def ee_rectangle(ee_module):
    """Return an ee.Geometry.Rectangle using the shared bbox."""
    return ee_module.Geometry.Rectangle(bbox_list())
