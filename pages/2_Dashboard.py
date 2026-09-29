"""Interactive result dashboard for the latest saved assessment."""

from __future__ import annotations

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from database.database import get_latest_assessment
from modules.scoring import PROTOTYPE_BASELINE_KG_CO2E


st.title("Your Sustainability Dashboard")
st.caption("Annual estimates in kg CO₂e · project-generated indicator · not an official rating")

email = st.session_state.get("current_email", "")
if not email:
    email = st.text_input("Enter the email used for your assessment")

record = get_latest_assessment(email) if email else None
if record is None:
    st.info("No assessment found for this email. Complete a Lifestyle Assessment to see your results.")
    st.page_link("pages/1_Lifestyle_Assessment.py", label="Start an assessment", icon="📝")
else:
    results = {
        "Transportation": float(record["transport_co2"]),
        "Energy": float(record["energy_co2"]),
        "Diet": float(record["diet_co2"]),
        "Shopping": float(record["shopping_co2"]),
        "Waste": float(record["waste_co2"]),
    }
    total = float(record["total_co2"])
    score = float(record["sustainability_score"])
    highest_category, highest_value = max(results.items(), key=lambda item: item[1])
    contribution = highest_value / total * 100 if total else 0.0
    assessment_date = pd.to_datetime(record["assessment_date"], utc=True).strftime("%Y-%m-%d %H:%M UTC")

    st.subheader("Assessment summary")
    summary_cols = st.columns(4)
    summary_cols[0].metric("Total Carbon Footprint", f"{total:,.0f} kg CO₂e/year")
    summary_cols[1].metric("Sustainability Score", f"{score:.1f} / 100")
    summary_cols[2].metric("Highest Impact Category", highest_category)
    summary_cols[3].metric("Assessment Date", assessment_date)
    st.caption(
        f"Project indicator compares this estimate with a prototype baseline of "
        f"{PROTOTYPE_BASELINE_KG_CO2E:,.0f} kg CO₂e/person/year. It is not an official standard."
    )

    st.subheader("YOUR HIGHEST IMPACT AREA")
    st.info(
        f"**{highest_category} — {contribution:.1f}%** contributes the largest share of your "
        "estimated annual footprint. This is a category-level result, not an AI recommendation."
    )

    chart_data = pd.DataFrame({"Category": list(results), "Estimated CO₂e (kg/year)": list(results.values())})
    pie_col, bar_col = st.columns(2)
    with pie_col:
        pie = px.pie(
            chart_data,
            names="Category",
            values="Estimated CO₂e (kg/year)",
            hole=0.52,
            title="Category-wise carbon contribution",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        pie.update_traces(hovertemplate="%{label}<br>%{value:,.1f} kg CO₂e/year<br>%{percent}<extra></extra>")
        st.plotly_chart(pie, width="stretch")
    with bar_col:
        bar = px.bar(
            chart_data,
            x="Category",
            y="Estimated CO₂e (kg/year)",
            title="Annual emissions by category",
            color="Category",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        bar.update_layout(showlegend=False, yaxis_title="kg CO₂e/year")
        st.plotly_chart(bar, width="stretch")

    comparison = pd.DataFrame(
        {"Measure": ["Your estimate", "Project baseline"], "kg CO₂e/year": [total, PROTOTYPE_BASELINE_KG_CO2E]}
    )
    comparison_chart = px.bar(
        comparison,
        x="Measure",
        y="kg CO₂e/year",
        color="Measure",
        title="Estimate compared with the prototype baseline",
        color_discrete_sequence=["#279c72", "#b8c9c2"],
    )
    st.plotly_chart(comparison_chart, width="stretch")

    with st.expander("Calculation and factor limitations"):
        lifestyle = json.loads(record["lifestyle_data_json"])
        st.write(
            "The assessment applies activity × factor using documented placeholder factors. "
            "Commute uses 52 weeks/year; flight time is converted at 800 km/hour; electricity "
            "is apportioned by household size. Factor values and the score baseline are not official."
        )
        st.json(lifestyle)