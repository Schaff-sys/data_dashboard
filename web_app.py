import streamlit as st
import pandas as pd
import plotly.express as px
import random
import time

# ---------------------
# PAGE SETUP
# ---------------------
st.set_page_config(page_title="Water Polo Live Match", layout='wide')
st.title("🏐 Live Water Polo Match Dashboard")


# Simulate match state
if "minute" not in st.session_state:
    st.session_state.minute = 0
    st.session_state.team_a_score = 0
    st.session_state.team_b_score = 0
    st.session_state.events = []


# --- CSV Upload Section ---
uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file is not None:
    new_data = pd.read_csv(uploaded_file)
    # Merge or append CSV data
    st.session_state.events = pd.concat([st.session_state.events, new_data]).drop_duplicates().reset_index(drop=True)

# --- In-app input form ---
with st.form("Add Event"):
    time_input = st.text_input("Time (mm:ss)")
    team_input = st.selectbox("Team", ["A", "B"])
    event_input = st.selectbox("Event", ["Goal", "Exclusion", "Save"])
    player_input = st.text_input("Player Name")
    submitted = st.form_submit_button("Add Event")
    
    if submitted:
        new_row = pd.DataFrame([{
            "Time": time_input,
            "Team": team_input,
            "Event": event_input,
            "Player": player_input
        }])
        st.session_state.events = pd.concat([st.session_state.events, new_row]).reset_index(drop=True)

# --- Display current data ---
st.subheader("Current Match Events")
st.dataframe(st.session_state.events)

# Increment minute & randomly simulate events
if st.session_state.minute < 32:  # 4x8min quarters
    st.session_state.minute += 1
    if random.random() < 0.3:  # 30% chance of event
        team = random.choice(["A", "B"])
        event_type = random.choice(["Goal", "Exclusion", "Save"])
        st.session_state.events.append({
            "Time": f"{st.session_state.minute:02d}:00",
            "Team": team,
            "Event": event_type,
            "Player": f"Player {random.randint(1, 13)}"
        })
        if event_type == "Goal":
            if team == "A":
                st.session_state.team_a_score += 1
            else:
                st.session_state.team_b_score += 1

# ---------------------
# HEADER
# ---------------------
# Example: actual vs predicted
team_a_actual = st.session_state.team_a_score
team_b_actual = st.session_state.team_b_score

team_a_pred = 8  # replace with your predicted value
team_b_pred = 6  # replace with your predicted value

col1, col2, col3 = st.columns([2, 1, 2])
col1.metric("Team A", team_a_actual, delta=f"Pred: {team_a_pred}")
col2.markdown(f"**Time:** {st.session_state.minute}′")
col3.metric("Team B", team_b_actual, delta=f"Pred: {team_b_pred}")


st.divider()

# ---------------------
# TABS
# ---------------------
tabs = st.tabs(["Match Stats", "Events", "Shot Map"])

# ---- MATCH STATS ----
with tabs[0]:
    st.subheader("📊 Team Stats (Simulated)")
    stats = {
        "Shots": [random.randint(5, 20), random.randint(5, 20)],
        "Exclusions": [random.randint(0, 5), random.randint(0, 5)],
        "Saves": [random.randint(5, 15), random.randint(5, 15)],

    }
    df = pd.DataFrame(stats, index=["Team A", "Team B"])
    st.dataframe(df)

    fig = px.bar(df.T, barmode="group", title="Stat Comparison")
    st.plotly_chart(fig, use_container_width=True)

# ---- EVENTS ----
with tabs[1]:
    st.subheader("🕒 Event Timeline")
    if len(st.session_state.events) == 0:
        st.info("No events yet.")
    else:
        events_df = pd.DataFrame(st.session_state.events)
        st.dataframe(events_df.sort_values("Time", ascending=False), use_container_width=True)

# ---- SHOT MAP ----
with tabs[2]:
    st.subheader("🎯 Shot Map (Randomized)")
    x = [random.uniform(0, 10) for _ in range(15)]
    y = [random.uniform(0, 5) for _ in range(15)]
    outcomes = [random.choice(["Goal", "Miss", "Save"]) for _ in range(15)]
    fig = px.scatter(x=x, y=y, color=outcomes, title="Shot Map", labels={"x": "Goal Width", "y": "Goal Height"})
    fig.update_yaxes(scaleanchor="x", scaleratio=0.5)
    st.plotly_chart(fig, use_container_width=True)


