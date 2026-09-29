"""Longitudinal view of saved SQLite assessments."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from database.database import get_assessment_history


st.title("Assessment History")
st.write("Review how your estimated annual footprint changes across saved assessments.")

default_email = st.session_state.get("current_email", "")
email = st.text_input("Email used for your assessments", value=default_email)

if email.strip():
    records = get_assessment_history(email)
    if not records:
        st.info("No saved assessments were found for that email.")
    else:
        history = pd.DataFrame(records)
        history["Date"] = pd.to_datetime(history["assessment_date"], utc=True).dt.tz_convert(None)
        st.dataframe(
            history[["Date", "total_co2", "sustainability_score"]]
            .rename(
                columns={
                    "total_co2": "Total CO₂e (kg/year)",
                    "sustainability_score": "Sustainability Score / 100",
                }
            )
            .sort_values("Date", ascending=False),
            width="stretch",
            hide_index=True,
        )
        if len(history) > 1:
            trend = px.line(
                history.sort_values("Date"),
                x="Date",
                y="total_co2",
                markers=True,
                title="Estimated footprint over time",
                labels={"total_co2": "kg CO₂e/year", "Date": "Assessment date"},
            )
            trend.update_layout(yaxis_title="kg CO₂e/year")
            st.plotly_chart(trend, width="stretch")
        else:
            st.caption("A trend line will appear after you save another assessment.")
else:
    st.info("Enter the email used during assessment to view saved history.")