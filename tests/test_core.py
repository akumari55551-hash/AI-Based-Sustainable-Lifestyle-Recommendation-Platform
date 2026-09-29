"""Focused unit tests for validation, calculations, preprocessing, and SQLite."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from database.database import get_assessment_history, get_latest_assessment, save_assessment
from modules.carbon_calculator import calculate_carbon_footprint
from modules.preprocessing import prepare_feature_frame, preprocess_lifestyle_data
from modules.scoring import PROTOTYPE_BASELINE_KG_CO2E, calculate_sustainability_score
from utils.validation import validate_lifestyle_data


VALID_PROFILE = {
    "name": "Alex Example",
    "email": "alex@example.org",
    "transport_mode": "car",
    "fuel_type": "petrol",
    "commute_km_week": 100,
    "public_transport_km_week": 20,
    "flight_hours_year": 4,
    "monthly_kwh": 150,
    "household_size": 2,
    "diet_type": "omnivore",
    "meat_frequency": "weekly",
    "shopping_frequency": "moderate",
    "secondary_consumption_score": 3,
    "waste_generation_level": "moderate",
    "waste_recycle_level": "medium",
    "appliance_rating_avg": None,
}


class ValidationTests(unittest.TestCase):
    def test_valid_lifestyle_input(self) -> None:
        self.assertEqual(validate_lifestyle_data(VALID_PROFILE), [])

    def test_negative_and_unrealistic_values_are_rejected(self) -> None:
        profile = {**VALID_PROFILE, "commute_km_week": -1, "monthly_kwh": 0}
        errors = validate_lifestyle_data(profile)
        self.assertTrue(any("commute" in message.lower() for message in errors))
        self.assertTrue(any("electricity" in message.lower() for message in errors))

    def test_missing_required_value_is_reported_and_optional_value_is_safe(self) -> None:
        profile = {key: value for key, value in VALID_PROFILE.items() if key != "monthly_kwh"}
        profile["household_size"] = None
        errors = validate_lifestyle_data(profile)
        self.assertTrue(any("monthly electricity" in message.lower() for message in errors))
        frame = prepare_feature_frame(profile)
        self.assertTrue(pd.isna(frame.loc[0, "appliance_rating_avg"]))


class CalculationTests(unittest.TestCase):
    def test_category_and_total_calculation(self) -> None:
        results = calculate_carbon_footprint(VALID_PROFILE)
        self.assertEqual(set(results), {"transport", "energy", "diet", "shopping", "waste", "total"})
        self.assertGreater(results["transport"], 0)
        self.assertGreater(results["energy"], 0)
        self.assertAlmostEqual(
            results["total"],
            round(sum(results[key] for key in ("transport", "energy", "diet", "shopping", "waste")), 2),
        )

    def test_score_is_normalized_and_bounded(self) -> None:
        self.assertEqual(calculate_sustainability_score(0), 100.0)
        self.assertEqual(calculate_sustainability_score(PROTOTYPE_BASELINE_KG_CO2E), 0.0)
        self.assertEqual(calculate_sustainability_score(PROTOTYPE_BASELINE_KG_CO2E * 2), 0.0)
        with self.assertRaises(ValueError):
            calculate_sustainability_score(-1)

    def test_preprocessing_encodes_and_scales_features(self) -> None:
        frame = pd.DataFrame(
            [
                VALID_PROFILE,
                {
                    **VALID_PROFILE,
                    "email": "other@example.org",
                    "monthly_kwh": 300,
                    "fuel_type": "na",
                    "transport_mode": "rail",
                    "diet_type": "vegetarian",
                    "meat_frequency": "none",
                    "shopping_frequency": "low",
                    "waste_generation_level": "low",
                    "waste_recycle_level": "high",
                },
            ]
        )
        raw = prepare_feature_frame(frame)
        transformed, fitted = preprocess_lifestyle_data(raw)
        self.assertEqual(transformed.shape[0], 2)
        self.assertGreaterEqual(transformed.shape[1], len(raw.columns))
        repeated, _ = preprocess_lifestyle_data(raw, fitted)
        self.assertEqual(repeated.shape, transformed.shape)


class DatabaseTests(unittest.TestCase):
    def test_insert_and_retrieve_assessment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "test.db"
            results = calculate_carbon_footprint(VALID_PROFILE)
            score = calculate_sustainability_score(results["total"])
            assessment_id, assessment_date = save_assessment(
                name=VALID_PROFILE["name"],
                email=VALID_PROFILE["email"],
                lifestyle_data={"monthly_kwh": VALID_PROFILE["monthly_kwh"]},
                carbon_results=results,
                sustainability_score=score,
                db_path=database_path,
            )
            history = get_assessment_history(VALID_PROFILE["email"], database_path)
            latest = get_latest_assessment(VALID_PROFILE["email"], database_path)
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]["assessment_id"], assessment_id)
            self.assertEqual(history[0]["assessment_date"], assessment_date)
            self.assertEqual(latest["total_co2"], results["total"])


if __name__ == "__main__":
    unittest.main()