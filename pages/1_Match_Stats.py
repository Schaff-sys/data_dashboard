import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Team Stats")

if "minute" not in st.session_state:
    st.session_state.minute = 0
    st.session_state.team_a_score = 0
    st.session_state.team_b_score = 0

stats = {
    "Shots": [15, 10],
    "Exclusions": [3, 5],
    "Saves": [5, 4],
}
df = pd.DataFrame(stats, index=["Team A", "Team B"])

col1, col2, col3 = st.columns([2, 1, 2])
col1.metric("Team A", st.session_state.team_a_score, delta="Pred: 8")
col2.metric("Time", f"{st.session_state.minute}′")
col3.metric("Team B", st.session_state.team_b_score, delta="Pred: 6")

st.divider()
st.dataframe(df)

fig = px.bar(df.T, barmode="group", title="Stat Comparison")
st.plotly_chart(fig, use_container_width=True)
