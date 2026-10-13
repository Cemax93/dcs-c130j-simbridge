"""Theater configuration loading."""

import json
import os
import sys

from .data import DEFAULT_THEATERS


def load_theaters(json_filename="theaters.json"):
    """Load external theater overrides, falling back to built-in data."""
    theaters = dict(DEFAULT_THEATERS)
    external_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), json_filename)
    if not os.path.isfile(external_path):
        return theaters

    try:
        with open(external_path, "r", encoding="utf-8") as file:
            custom = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        print(f"Warning: failed to load external '{json_filename}': {error}", file=sys.stderr)
        return theaters

    if isinstance(custom, dict):
        for theater_name, theater_data in custom.items():
            if isinstance(theater_data, dict) and "airports" in theater_data:
                theaters[theater_name] = theater_data
    return theaters
