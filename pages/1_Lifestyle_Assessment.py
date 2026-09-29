"""Short lifestyle questionnaire and end-to-end assessment submission."""

from __future__ import annotations

import sqlite3

import streamlit as st

from database.database import save_assessment
from modules.carbon_calculator import calculate_carbon_footprint
from modules.preprocessing import prepare_feature_frame
from modules.scoring import calculate_sustainability_score
from utils.validation import validate_lifestyle_data


st.title("Lifestyle Assessment")
st.write("Answer the short questionnaire to estimate an annual footprint by category.")
st.caption("Typical completion time: about 5 minutes. All factor values are prototype placeholders.")

with st.form("lifestyle_assessment"):
    st.subheader("About you")
    personal_col1, personal_col2 = st.columns(2)
    with personal_col1:
        name = st.text_input("Name", max_chars=100)
    with personal_col2:
        email = st.text_input("Email (used to group your local assessment history)", max_chars=254)

    st.divider()
    st.subheader("Transportation")
    transport_col1, transport_col2 = st.columns(2)
    with transport_col1:
        transport_mode = st.selectbox(
            "Main weekly travel mode",
            ["car", "motorcycle", "public_bus", "rail", "active"],
            format_func=lambda value: {
                "car": "Car",
                "motorcycle": "Motorcycle",
                "public_bus": "Public bus",
                "rail": "Rail/train",
                "active": "Walking/cycling",
            }[value],
        )
        fuel_type = st.selectbox(
            "Vehicle/fuel type",
            ["petrol", "diesel", "hybrid", "electric"] if transport_mode == "car" else ["na"],
            format_func=lambda value: "Not applicable" if value == "na" else value.title(),
        )
    with transport_col2:
        commute_km_week = st.number_input(
            "Total distance travelled per week (km)", min_value=0.0, max_value=2000.0, value=50.0, step=5.0
        )
        public_transport_km_week = st.number_input(
            "Of that, distance by public bus per week (km)",
            min_value=0.0,
            max_value=2000.0,
            value=0.0,
            step=5.0,
            help="This distance is counted as bus travel rather than the main travel mode.",
        )
        flight_hours_year = st.number_input(
            "Flight hours per year", min_value=0.0, max_value=5000.0, value=0.0, step=1.0
        )

    st.divider()
    st.subheader("Domestic energy")
    energy_col1, energy_col2 = st.columns(2)
    with energy_col1:
        monthly_kwh = st.number_input(
            "Monthly household electricity consumption (kWh)",
            min_value=0.1,
            max_value=100000.0,
            value=180.0,
            step=10.0,
        )
    with energy_col2:
        include_household_size = st.checkbox("Provide household size", value=True)
        household_size = (
            st.number_input("People in household", min_value=1, max_value=20, value=2, step=1)
            if include_household_size
            else None
        )

    st.divider()
    st.subheader("Diet")
    diet_col1, diet_col2 = st.columns(2)
    with diet_col1:
        diet_type = st.selectbox(
            "Major dietary pattern", ["omnivore", "pescatarian", "vegetarian", "vegan"]
        )
    with diet_col2:
        meat_frequency = st.selectbox(
            "Meat consumption frequency",
            ["none", "rarely", "weekly", "daily"],
            index=0 if diet_type in {"vegan", "vegetarian"} else 2,
            format_func=lambda value: {
                "none": "No meat",
                "rarely": "Rarely",
                "weekly": "1–3 times per week",
                "daily": "Daily",
            }[value],
        )

    st.divider()
    st.subheader("Shopping and consumption")
    shopping_col1, shopping_col2 = st.columns(2)
    with shopping_col1:
        shopping_frequency = st.selectbox(
            "General shopping/consumption frequency", ["low", "moderate", "high"], index=1
        )
    with shopping_col2:
        secondary_consumption_score = st.slider(
            "Secondary consumption score", min_value=0, max_value=10, value=4,
            help="Self-rating: 0 = very low additional consumption; 10 = very high.",
        )

    st.divider()
    st.subheader("Waste")
    waste_col1, waste_col2 = st.columns(2)
    with waste_col1:
        waste_generation_level = st.select_slider(
            "Typical waste generation level", options=["low", "moderate", "high"], value="moderate"
        )
    with waste_col2:
        waste_recycle_level = st.select_slider(
            "Recycling frequency", options=["low", "medium", "high"], value="medium"
        )

    submitted = st.form_submit_button("Calculate my assessment", type="primary", width="stretch")

if submitted:
    lifestyle_data = {
        "name": name.strip(),
        "email": email.strip().lower(),
        "transport_mode": transport_mode,
        "fuel_type": fuel_type,
        "commute_km_week": commute_km_week,
        "public_transport_km_week": public_transport_km_week,
        "flight_hours_year": flight_hours_year,
        "monthly_kwh": monthly_kwh,
        "household_size": household_size,
        "diet_type": diet_type,
        "meat_frequency": meat_frequency,
        "shopping_frequency": shopping_frequency,
        "secondary_consumption_score": secondary_consumption_score,
        "waste_generation_level": waste_generation_level,
        "waste_recycle_level": waste_recycle_level,
        "appliance_rating_avg": None,
    }
    validation_errors = validate_lifestyle_data(lifestyle_data)
    if validation_errors:
        st.error("Please correct the following before calculating:")
        for error in validation_errors:
            st.write(f"- {error}")
    else:
        try:
            # Establish a stable raw feature schema for the calculation/data pipeline.
            feature_frame = prepare_feature_frame(lifestyle_data)
            if feature_frame.empty:
                raise ValueError("No lifestyle features were available to process.")
            carbon_results = calculate_carbon_footprint(lifestyle_data)
            score = calculate_sustainability_score(carbon_results["total"])
            assessment_id, assessment_date = save_assessment(
                name=name,
                email=email,
                lifestyle_data={key: value for key, value in lifestyle_data.items() if key not in {"name", "email"}},
                carbon_results=carbon_results,
                sustainability_score=score,
            )
            st.session_state["current_email"] = email.strip().lower()
            st.session_state["latest_assessment"] = {
                "assessment_id": assessment_id,
                "assessment_date": assessment_date,
                "carbon_results": carbon_results,
                "sustainability_score": score,
            }
            st.success("Assessment saved successfully. Opening your dashboard…")
            st.switch_page("pages/2_Dashboard.py")
        except (ValueError, KeyError, OSError, sqlite3.Error) as error:
            st.error(f"The assessment could not be completed: {error}")