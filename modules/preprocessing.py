"""Reusable cleanup and future-ML feature transformation."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


FEATURE_COLUMNS = [
    "monthly_kwh",
    "commute_km_week",
    "fuel_type",
    "diet_type",
    "meat_frequency",
    "flight_hours_year",
    "waste_recycle_level",
    "appliance_rating_avg",
    "secondary_consumption_score",
    "transport_mode",
    "public_transport_km_week",
    "household_size",
    "shopping_frequency",
    "waste_generation_level",
]

NUMERIC_FEATURES = [
    "monthly_kwh",
    "commute_km_week",
    "flight_hours_year",
    "appliance_rating_avg",
    "secondary_consumption_score",
    "public_transport_km_week",
    "household_size",
]

CATEGORICAL_FEATURES = [
    "fuel_type",
    "diet_type",
    "meat_frequency",
    "waste_recycle_level",
    "transport_mode",
    "shopping_frequency",
    "waste_generation_level",
]


def prepare_feature_frame(data: Mapping[str, Any] | pd.DataFrame) -> pd.DataFrame:
    """Return one or more records in a stable, model-ready raw feature schema.

    Missing optional fields remain missing here and are imputed by the fitted
    scikit-learn preprocessing pipeline. Extra identifying fields are excluded.
    """
    frame = data.copy() if isinstance(data, pd.DataFrame) else pd.DataFrame([dict(data)])
    for column in FEATURE_COLUMNS:
        if column not in frame.columns:
            frame[column] = np.nan
    frame = frame[FEATURE_COLUMNS].copy()
    for column in NUMERIC_FEATURES:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    for column in CATEGORICAL_FEATURES:
        frame[column] = frame[column].replace(r"^\s*$", np.nan, regex=True)
    return frame


def build_preprocessing_pipeline() -> ColumnTransformer:
    """Build the reusable impute/scale/one-hot pipeline for future ML training."""
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def preprocess_lifestyle_data(
    data: Mapping[str, Any] | pd.DataFrame,
    preprocessor: ColumnTransformer | None = None,
) -> tuple[np.ndarray, ColumnTransformer]:
    """Impute, one-hot encode, and scale data for a future ML model.

    Pass a fitted ``preprocessor`` for inference. If omitted, the pipeline is
    fit on this input; model training should instead fit it on the training set.
    """
    frame = prepare_feature_frame(data)
    pipeline = preprocessor or build_preprocessing_pipeline()
    transformed = pipeline.fit_transform(frame) if preprocessor is None else pipeline.transform(frame)
    return np.asarray(transformed, dtype=float), pipeline