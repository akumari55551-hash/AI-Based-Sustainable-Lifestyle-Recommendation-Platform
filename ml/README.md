# Future ML preparation (not implemented as a model)

This prototype does **not** train K-Means, generate recommendations, or claim AI personalization. `data/sample_users.csv` contains small, clearly synthetic example records only; it is not suitable for fitting or validating a real model.

## Planned feature schema

The stable raw schema in `modules/preprocessing.py` includes the future clustering features:

- `monthly_kwh`
- `commute_km_week`
- `fuel_type`
- `diet_type`
- `meat_frequency`
- `flight_hours_year`
- `waste_recycle_level`
- `appliance_rating_avg`
- `secondary_consumption_score`

Additional current assessment fields are retained in the same frame for transport mode, public transit distance, household size, shopping frequency, and waste generation level. The current short questionnaire does not collect appliance ratings, so actual assessment records leave `appliance_rating_avg` missing; future training preprocessing can impute it only after a suitable dataset is assembled.

## Future pipeline outline

1. Obtain consented, representative, sufficiently sized lifestyle data with documented provenance and a consistent feature definition.
2. Review missingness, validate ranges, and separate personally identifying data from model features.
3. Use `prepare_feature_frame()` to apply the stable schema; fit `build_preprocessing_pipeline()` on training data only for numeric median imputation/scaling and categorical imputation/one-hot encoding.
4. Evaluate K-Means cluster counts and stability with appropriate unsupervised metrics and domain review; avoid presenting clusters as ground truth.
5. Develop and evaluate a transparent recommendation-ranking layer, then collect feedback for a separately governed feedback loop.

Do not fit on the included synthetic examples and do not use the preprocessing pipeline on held-out data with `fit`; pass the training-fitted transformer to `preprocess_lifestyle_data()` for inference.