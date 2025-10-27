import streamlit as st
import pandas as pd

st.title("🕒 Data Entry")

if "events" not in st.session_state:
    st.session_state.events = pd.DataFrame(columns=["Time", "Team", "Event", "Subevent", "Outcome", "Player"])

uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file is not None:
    st.session_state.events = pd.read_csv(uploaded_file)

event_input = st.selectbox("Event", ["6v6", "6v5", "Penalty", "Counter"])

with st.form("Add Event"):
    time_input = st.text_input("Time (mm:ss)")
    period_input = st.selectbox("Period", ["1st", "2nd", "3rd", "4th", "OT"])
    match_input = st.text_input("Match (Home Team vs Away Team)")
    team_input = st.selectbox("Team", ["Home", "Away"])
    submitted = st.form_submit_button("Add Event")


if event_input == "6v6":
    with st.form("Add Subevent"):
        subevent6v6_input = st.selectbox("6v6 Subevent", ["Press", "Zone 1-2", "Zone 4-5", "M-Zone"])
        subeventcounter_input = st.selectbox("Counter Subevent", ["1-2", "Center", "4-5"])
        result_input = st.selectbox("Outcome", ["Goal", "Miss", "Save", "Block", "Turnover", "Exclusion"])
        turnover_input = st.selectbox("Turnover Type", ["Steal", "Bad Pass", "Offensive Foul", "Shot Clock Violation"])
        shot_input = st.selectbox("Shot Type", ["Skip Shot", "Lob Shot"])
        player_input = st.selectbox("Player committing", [f"Player {i}" for i in range(1, 14)])
        player_input2 = st.selectbox("Player affected (if applicable)", [f"Player {i}" for i in range(1, 14)] + ["N/A"])
        submitted = st.form_submit_button("Add Event")

if event_input == "6v5":
    with st.form("Add Subevent"):
        subevent6v5_input = st.selectbox("6v5 Subevent", ["1-2", "Center", "4-5"])
        result_input = st.selectbox("Outcome", ["Goal", "Miss", "Save", "Block", "Turnover", "Exclusion"])
        turnover_input = st.selectbox("Turnover Type", ["Steal", "Bad Pass", "Offensive Foul", "Shot Clock Violation"])
        shot_input = st.selectbox("Shot Type", ["Skip Shot", "Lob Shot"])
        player_input = st.selectbox("Player committing", [f"Player {i}" for i in range(1, 14)])
        player_input2 = st.selectbox("Player affected (if applicable)", [f"Player {i}" for i in range(1, 14)] + ["N/A"])
        submitted = st.form_submit_button("Add Event")

if event_input == "Counter":
    with st.form("Add Subevent"):
        subeventcounter_input = st.selectbox("Counter Subevent", ["1-2", "Center", "4-5"])
        result_input = st.selectbox("Outcome", ["Goal", "Miss", "Save", "Block", "Turnover", "Exclusion"])
        turnover_input = st.selectbox("Turnover Type", ["Steal", "Bad Pass", "Offensive Foul", "Shot Clock Violation"])
        shot_input = st.selectbox("Shot Type", ["Skip Shot", "Lob Shot"])
        player_input = st.selectbox("Player committing", [f"Player {i}" for i in range(1, 14)])
        player_input2 = st.selectbox("Player affected (if applicable)", [f"Player {i}" for i in range(1, 14)] + ["N/A"])
        submitted = st.form_submit_button("Add Event")

if event_input == "Penalty":
    with st.form("Add Subevent"):
        turnover_input = st.selectbox("Turnover Type", ["Steal", "Bad Pass", "Offensive Foul", "Shot Clock Violation"])
        result_input = st.selectbox("Outcome", ["Goal", "Miss", "Save"])
        shot_input = st.selectbox("Shot Type", ["Skip Shot", "Lob Shot"])
        player_input = st.selectbox("Player committing", [f"Player {i}" for i in range(1, 14)])
        player_input2 = st.selectbox("Player affected (if applicable)", [f"Player {i}" for i in range(1, 14)] + ["N/A"])
        submitted = st.form_submit_button("Add Event")
    
  
    
if submitted:
        new_row = pd.DataFrame([{
            "Time": time_input,
            "Match": match_input,
            "Team": team_input,
            "Event": event_input,
            "Player committing": player_input,
            "Player affected": player_input2,
            "Outcome": result_input,
            "Turnover Type": turnover_input if event_input != "Penalty" else "N/A",
            "Shot Type": shot_input,
            "Subevent": subevent6v6_input if event_input == "6v6"
            else subevent6v5_input if event_input == "6v5"
            else subeventcounter_input if event_input == "Counter"
            else "N/A",
        }])
        st.session_state.events = pd.concat(
            [st.session_state.events, new_row]
        ).drop_duplicates().reset_index(drop=True)

if len(st.session_state.events) == 0:
    st.info("No events yet.")
else:
    st.dataframe(st.session_state.events.sort_values("Time", ascending=True), use_container_width=True)

csv = st.session_state.events.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Export Events as CSV",
    data=csv,
    file_name="water_polo_events.csv",
    mime="text/csv"
)