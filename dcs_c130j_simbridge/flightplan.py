"""Portable flight-plan files used by DCS C-130J SimBridge."""

from __future__ import annotations

import json
import math
from typing import Any

FILE_FORMAT = "dcs-c130j-simbridge-flight-plan"
FILE_VERSION = 1

_WAYPOINT_FIELDS = ("name", "type_label", "wp_type", "lat", "lon", "rwy", "elev")


def build_flight_plan_document(
    waypoints: list[dict[str, Any]],
    route_name: str,
    theater: str,
) -> dict[str, Any]:
    """Build a versioned, JSON-serializable document for sharing a route."""
    return {
        "format": FILE_FORMAT,
        "version": FILE_VERSION,
        "route_name": route_name.strip(),
        "theater": theater,
        "waypoints": [dict(wp) for wp in waypoints],
    }


def save_flight_plan(
    path: str,
    waypoints: list[dict[str, Any]],
    route_name: str,
    theater: str,
) -> None:
    """Validate and save a shareable flight-plan document."""
    document = build_flight_plan_document(waypoints, route_name, theater)
    validate_flight_plan_document(document)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(document, file, indent=2, ensure_ascii=False)
        file.write("\n")


def load_flight_plan(path: str) -> dict[str, Any]:
    """Load and validate a shareable flight-plan document."""
    with open(path, "r", encoding="utf-8") as file:
        document = json.load(file)
    validate_flight_plan_document(document)
    return document


def validate_flight_plan_document(document: Any) -> None:
    """Raise ValueError when a document is not a supported flight plan."""
    if not isinstance(document, dict):
        raise ValueError("The file must contain a JSON object.")
    if document.get("format") != FILE_FORMAT:
        raise ValueError("This is not a DCS C-130J SimBridge flight-plan file.")
    if document.get("version") != FILE_VERSION:
        raise ValueError(f"Unsupported flight-plan file version: {document.get('version')!r}.")
    if not isinstance(document.get("route_name"), str):
        raise ValueError("The flight plan route name must be text.")
    if not isinstance(document.get("theater"), str):
        raise ValueError("The flight plan theater must be text.")

    waypoints = document.get("waypoints")
    if not isinstance(waypoints, list) or not waypoints:
        raise ValueError("The flight plan must contain at least one waypoint.")

    for index, waypoint in enumerate(waypoints, start=1):
        if not isinstance(waypoint, dict):
            raise ValueError(f"Waypoint {index} must be an object.")
        missing = [field for field in _WAYPOINT_FIELDS if field not in waypoint]
        if missing:
            raise ValueError(f"Waypoint {index} is missing: {', '.join(missing)}.")
        if not isinstance(waypoint["name"], str) or not waypoint["name"].strip():
            raise ValueError(f"Waypoint {index} must have a name.")
        if not isinstance(waypoint["type_label"], str):
            raise ValueError(f"Waypoint {index} has an invalid type label.")
        if not isinstance(waypoint["wp_type"], int) or waypoint["wp_type"] not in (0, 1, 2, 7):
            raise ValueError(f"Waypoint {index} has an invalid CNI waypoint type.")
        for coordinate in ("lat", "lon"):
            value = waypoint[coordinate]
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"Waypoint {index} has an invalid {coordinate} coordinate.")
        if not isinstance(waypoint["rwy"], str) or not isinstance(waypoint["elev"], str):
            raise ValueError(f"Waypoint {index} has invalid runway or elevation data.")
