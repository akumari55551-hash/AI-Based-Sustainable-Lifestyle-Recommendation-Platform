"""Input validation for the lifestyle assessment form."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Any


VALID_CATEGORIES = {
    "transport_mode": {"car", "motorcycle", "public_bus", "rail", "active"},
    "fuel_type": {"petrol", "diesel", "hybrid", "electric", "na"},
    "diet_type": {"vegan", "vegetarian", "pescatarian", "omnivore"},
    "meat_frequency": {"none", "rarely", "weekly", "daily"},
    "shopping_frequency": {"low", "moderate", "high"},
    "waste_generation_level": {"low", "moderate", "high"},
    "waste_recycle_level": {"low", "medium", "high"},
}

NUMERIC_LIMITS = {
    "commute_km_week": (0, 2000),
    "public_transport_km_week": (0, 2000),
    "flight_hours_year": (0, 5000),
    "monthly_kwh": (0.000001, 100000),
    "household_size": (1, 20),
    "secondary_consumption_score": (0, 10),
    "appliance_rating_avg": (1, 5),
}

OPTIONAL_NUMERIC_FIELDS = {"household_size", "appliance_rating_avg"}
REQUIRED_CATEGORIES = set(VALID_CATEGORIES)


def validate_lifestyle_data(data: Mapping[str, Any]) -> list[str]:
    """Return user-readable validation errors; an empty list means valid input."""
    errors: list[str] = []
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    if not name:
        errors.append("Please enter your name.")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        errors.append("Please enter a valid email address for assessment history.")

    for field, allowed_values in VALID_CATEGORIES.items():
        value = data.get(field)
        if value is None or str(value).strip() == "":
            errors.append(f"Please select a value for {field.replace('_', ' ')}.")
        elif value not in allowed_values:
            errors.append(f"The selected {field.replace('_', ' ')} is not valid.")

    if data.get("transport_mode") == "car":
        if data.get("fuel_type") == "na":
            errors.append("Choose a fuel type for a car.")
    elif data.get("transport_mode") != "car" and data.get("fuel_type") not in {"na", None}:
        errors.append("Fuel type should be set to Not applicable unless car is selected.")

    numeric_fields = set(NUMERIC_LIMITS)
    for field in numeric_fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            if field in OPTIONAL_NUMERIC_FIELDS:
                continue
            if field == "monthly_kwh":
                errors.append("Please provide monthly electricity consumption.")
            else:
                errors.append(f"Please provide {field.replace('_', ' ')}.")
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            errors.append(f"{field.replace('_', ' ').capitalize()} must be a number.")
            continue
        low, high = NUMERIC_LIMITS[field]
        if not math.isfinite(number) or number < low or number > high:
            if field == "monthly_kwh":
                errors.append("Monthly electricity consumption must be positive and no more than 100,000 kWh.")
            else:
                errors.append(
                    f"{field.replace('_', ' ').capitalize()} must be between {low:g} and {high:g}."
                )

    try:
        commute = float(data.get("commute_km_week", 0))
        public_transport = float(data.get("public_transport_km_week", 0))
        if public_transport > commute:
            errors.append("Public transport distance cannot exceed total weekly travel distance.")
    except (TypeError, ValueError):
        pass  # The specific numeric validation message above is more useful.

    if data.get("diet_type") in {"vegan", "vegetarian"} and data.get("meat_frequency") not in {"none", None}:
        errors.append("Select 'No meat' for a vegan or vegetarian diet pattern.")
    return errors