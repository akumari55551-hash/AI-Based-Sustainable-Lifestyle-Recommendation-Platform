"""Entry point and landing page for the Streamlit prototype."""

import streamlit as st

from database.database import initialize_database


st.set_page_config(
    page_title="Sustainable Lifestyle Platform",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)
initialize_database()

st.title("AI-Based Sustainable Lifestyle Recommendation Platform")
st.caption("30% prototype · transparent carbon assessment · local history")

st.markdown(
    """
    This prototype estimates an annual lifestyle footprint across transportation,
    domestic energy, diet, shopping, and waste. Emissions are calculated with
    documented placeholder factors—not by an AI model. The sustainability score
    is a project-generated indicator, not an official environmental standard.
    """
)

col_assess, col_dashboard, col_history = st.columns(3)
with col_assess:
    st.page_link("pages/1_Lifestyle_Assessment.py", label="Start an assessment", icon="📝")
with col_dashboard:
    st.page_link("pages/2_Dashboard.py", label="Open dashboard", icon="📊")
with col_history:
    st.page_link("pages/3_History.py", label="View history", icon="🗂️")

st.info(
    "Enter the same email on later assessments to group your local history. "
    "This prototype does not verify email addresses or provide account authentication."
)