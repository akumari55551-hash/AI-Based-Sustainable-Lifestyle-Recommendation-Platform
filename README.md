# AI-Based Sustainable Lifestyle Recommendation Platform

An academic prototype for collecting lifestyle data, estimating annual category-wise greenhouse-gas emissions, and tracking assessments locally. The current implementation is deliberately limited to deterministic carbon assessment, a project-generated indicator score, and SQLite history; it does not make AI-powered recommendations.

> **Synopsis note:** No separate project synopsis file was present in the provided workspace. This implementation follows the project scope and future-feature terminology supplied in the project brief. Confirm benchmark factors and terminology against the approved synopsis before academic submission.

## Problem statement

People often lack a simple way to see how everyday choices may contribute to their personal carbon footprint. This prototype collects a short lifestyle profile and provides a transparent, approximate annual CO₂-equivalent estimate by category. It is an educational prototype, not a carbon audit or official environmental rating.

## Features implemented in this 30% prototype

- Five-domain lifestyle assessment: transportation, domestic energy, diet, shopping/consumption, and waste.
- Input validation and reusable preprocessing/data preparation.
- Deterministic, CSV-driven emission-factor calculations; no ML model is used for emissions.
- Category breakdown, total estimated footprint, highest-impact category, and a project-generated 0–100 sustainability indicator.
- Interactive Streamlit dashboard with Plotly charts.
- SQLite user, assessment, and carbon-result records; per-email assessment history and trend chart.
- Synthetic sample profiles and a future ML data-preparation pipeline outline.

### CURRENT IMPLEMENTATION

Carbon assessment + dashboard + history + data pipeline.

### FUTURE

K-Means behavioral clustering + personalized recommendation engine + feedback loop + advanced integrations.

## Technology stack

Python 3.10+, Streamlit, Pandas, NumPy, scikit-learn (reusable future-feature preprocessing), Plotly, and SQLite.

## Project structure

```text
AI-Based Sustainable Lifestyle Recommendation Platform/  (workspace root)
├── app.py
├── database/
│   ├── __init__.py
│   ├── database.py
│   └── sustainable.db             # initialized automatically; local runtime data
├── data/
│   ├── emission_factors.csv
│   └── sample_users.csv
├── modules/
│   ├── __init__.py
│   ├── carbon_calculator.py
│   ├── preprocessing.py
│   └── scoring.py
├── pages/
│   ├── 1_Lifestyle_Assessment.py
│   ├── 2_Dashboard.py
│   └── 3_History.py
├── tests/
│   └── test_core.py
├── utils/
│   ├── __init__.py
│   └── validation.py
├── ml/
│   └── README.md
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

Use Python 3.10 or newer. From the workspace root, create and activate a virtual environment, then install the dependencies:

```powershell
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

For Python 3.11 or 3.12, replace `-3.10` with the installed version (or use `python -m venv .venv`).

## Run the application

```powershell
streamlit run app.py
```

SQLite is initialized automatically in `database/sustainable.db`. The first run opens the local Streamlit app in a browser.

## Sample workflow

1. Open **Lifestyle Assessment**, enter a name/email and answer the short questionnaire.
2. Submit. Inputs are validated, converted to a clean feature record, and emissions are calculated using the local factor CSV.
3. The assessment and category results are saved to SQLite; the app opens the Dashboard.
4. Review total annual kg CO₂e, the project indicator, the highest-impact category, and category charts.
5. Open **History** to view and compare saved assessments for the entered email.

The calculation estimates annual footprint. Travel uses the weekly commute distance annualized to 52 weeks and annual flight hours; electricity uses monthly kWh annualized to 12 months and apportioned by household size. These are simplifying assumptions, not measured emissions.

## Emission factors and score

`data/emission_factors.csv` documents each factor's category, activity, value, unit, reference context, and limitations. Values are explicitly labeled as **prototype placeholders**, qualitatively informed by benchmark categories associated with DEFRA/DESNZ, EPA, and food-climate metrics. They are not claimed to be official values from those sources. Replace them with region- and year-appropriate sourced factors before drawing real-world conclusions.

The project-generated sustainability indicator compares the annual estimate with a documented prototype baseline of 8,000 kg CO₂e/person/year and clamps the result to 0–100. It is not an officially recognized environmental standard and should not be compared as one.

## Tests

Run the standard-library test suite from the project root:

```powershell
python -m unittest discover -s tests -v
```

The tests cover valid and invalid/missing lifestyle inputs, carbon category and total calculations, score boundaries, and SQLite insertion/retrieval. For a UI smoke test, run Streamlit and submit one valid assessment, then confirm it appears on Dashboard and History.

## Current limitations

- Factors, conversion assumptions, and the comparison baseline are illustrative prototype values, not regional or official estimates.
- Results depend on self-reported inputs and simplified categories; uncertainty is not modeled.
- The app does not provide authenticated accounts; email is used as a local history key, not verified identity.
- No AI personalization, recommendations, reinforcement learning, IoT, OCR, mobile app, or external API is implemented.
- Appliance rating is reserved as a future ML feature and is not collected in this short questionnaire.
- `database/sustainable.db` is local, unencrypted prototype storage and should not be used for sensitive production data.

## Next phase

After validating the factor sources and collecting an appropriately governed dataset, the next phase can add a documented K-Means behavioral-clustering pipeline, recommendation ranking, feedback/longitudinal evaluation, and eventually a separate API/frontend architecture. Those features are not part of this prototype.

