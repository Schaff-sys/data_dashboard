import streamlit as st
import plotly.express as px
import random

st.title("🎯 Shot Map")

if "shot_data" not in st.session_state:
    st.session_state.shot_data = {
        "x": [random.uniform(0, 10) for _ in range(15)],
        "y": [random.uniform(0, 5) for _ in range(15)],
        "outcomes": [random.choice(["Goal", "Miss", "Save"]) for _ in range(15)],
    }

data = st.session_state.shot_data
fig = px.scatter(
    x=data["x"],
    y=data["y"],
    color=data["outcomes"],
    title="Shot Map",
    labels={"x": "Goal Width", "y": "Goal Height"},
)
fig.update_yaxes(scaleanchor="x", scaleratio=0.5)
st.plotly_chart(fig, use_container_width=True)
