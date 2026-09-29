"""Project-generated sustainability indicator; not an official standard."""

from __future__ import annotations

import numpy as np


PROTOTYPE_BASELINE_KG_CO2E = 8000.0


def calculate_sustainability_score(
    total_co2: float,
    baseline_kg_co2e: float = PROTOTYPE_BASELINE_KG_CO2E,
) -> float:
    """Return a 0-100 inverse footprint indicator relative to the prototype baseline."""
    if not np.isfinite(total_co2) or total_co2 < 0:
        raise ValueError("Total CO2e must be a finite, non-negative number.")
    if not np.isfinite(baseline_kg_co2e) or baseline_kg_co2e <= 0:
        raise ValueError("The comparison baseline must be a finite, positive number.")
    score = np.clip(100 * (1 - total_co2 / baseline_kg_co2e), 0, 100)
    return round(float(score), 1)