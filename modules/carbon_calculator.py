"""CSV-driven deterministic annual carbon-footprint calculations."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Mapping


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FACTOR_PATH = PROJECT_ROOT / "data" / "emission_factors.csv"


def load_emission_factors(path: str | Path = DEFAULT_FACTOR_PATH) -> dict[str, float]:
    """Load factors from CSV, rejecting malformed or duplicate activities."""
    factors: dict[str, float] = {}
    with Path(path).open("r", encoding="utf-8-sig", newline="") as factor_file:
        reader = csv.DictReader(factor_file)
        required = {"category", "activity", "factor", "unit", "source/reference", "notes"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("Emission factor CSV is missing one or more required columns.")
        for row in reader:
            activity = (row.get("activity") or "").strip()
            try:
                factor = float(row["factor"])
            except (TypeError, ValueError) as error:
                raise ValueError(f"Invalid factor for activity '{activity}'.") from error
            if not activity or activity in factors or factor < 0:
                raise ValueError(f"Missing, duplicate, or negative factor for activity '{activity}'.")
            factors[activity] = factor
    return factors


def calculate_carbon_footprint(
    lifestyle_data: Mapping[str, Any],
    factor_path: str | Path = DEFAULT_FACTOR_PATH,
) -> dict[str, float]:
    """Calculate annual category estimates in kg CO2e using activity × factor.

    Commute distance is annualized to 52 weeks; flight hours use an explicit
    prototype conversion of 800 passenger-km/hour. Electricity is apportioned
    across the entered household size. All factors are loaded from the CSV.
    """
    factors = load_emission_factors(factor_path)
    transport_mode = str(lifestyle_data["transport_mode"])
    fuel_type = str(lifestyle_data.get("fuel_type", "na"))
    main_activity = {
        "car": f"car_{fuel_type}",
        "motorcycle": "motorcycle",
        "public_bus": "public_bus",
        "rail": "rail",
        "active": "active",
    }[transport_mode]

    commute_km_week = float(lifestyle_data["commute_km_week"])
    public_transport_km_week = float(lifestyle_data.get("public_transport_km_week", 0) or 0)
    non_transit_km_week = commute_km_week - public_transport_km_week
    flight_hours_year = float(lifestyle_data.get("flight_hours_year", 0) or 0)
    transport = (
        non_transit_km_week * 52 * factors[main_activity]
        + public_transport_km_week * 52 * factors["public_bus"]
        + flight_hours_year * 800 * factors["flight"]
    )

    household_size = float(lifestyle_data.get("household_size") or 1)
    energy = float(lifestyle_data["monthly_kwh"]) * 12 / household_size * factors["electricity"]

    diet = factors[f"diet_{lifestyle_data['diet_type']}"] + factors[
        f"meat_{lifestyle_data['meat_frequency']}"
    ]
    shopping = (
        factors[f"shopping_{lifestyle_data['shopping_frequency']}"]
        + float(lifestyle_data["secondary_consumption_score"])
        * factors["secondary_consumption_point"]
    )
    waste = factors[f"waste_{lifestyle_data['waste_generation_level']}"] * factors[
        f"recycling_{lifestyle_data['waste_recycle_level']}"
    ]

    categories = {
        "transport": transport,
        "energy": energy,
        "diet": diet,
        "shopping": shopping,
        "waste": waste,
    }
    total = sum(categories.values())
    return {**{key: round(value, 2) for key, value in categories.items()}, "total": round(total, 2)}