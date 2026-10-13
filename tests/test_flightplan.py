import json
import tempfile
import unittest
from pathlib import Path

from dcs_c130j_simbridge.flightplan import (
    FILE_FORMAT,
    build_flight_plan_document,
    load_flight_plan,
    save_flight_plan,
    validate_flight_plan_document,
)


WAYPOINT = {
    "name": "TEST",
    "type_label": "WPT",
    "wp_type": 0,
    "lat": 45.5,
    "lon": -37.5,
    "rwy": "",
    "elev": "-999",
}


class FlightPlanFileTests(unittest.TestCase):
    def test_document_has_stable_format_marker(self):
        document = build_flight_plan_document([WAYPOINT], "TRAINING", "Caucasus")
        self.assertEqual(document["format"], FILE_FORMAT)

    def test_round_trip_preserves_route(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "training.simbridge.json"
            save_flight_plan(str(path), [WAYPOINT], "TRAINING", "Caucasus")
            document = load_flight_plan(str(path))
        self.assertEqual(document["route_name"], "TRAINING")
        self.assertEqual(document["waypoints"], [WAYPOINT])

    def test_invalid_format_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_flight_plan_document({"format": "other", "version": 1})

    def test_saved_file_is_readable_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "training.simbridge.json"
            save_flight_plan(str(path), [WAYPOINT], "TRAINING", "Caucasus")
            self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)
