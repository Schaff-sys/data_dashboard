import streamlit as st
import pandas as pd

st.title("🕒 Event Timeline")

if "events" not in st.session_state:
    st.session_state.events = pd.DataFrame(columns=["Time", "Team", "Event", "Subevent", "Outcome", "Player"])

uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file is not None:
    st.session_state.events = pd.read_csv(uploaded_file)

with st.form("Add Event"):
    time_input = st.text_input("Time (mm:ss)")
    team_input = st.selectbox("Team", ["A", "B"])
    event_input1 = st.empty()
    event_input = event_input1.selectbox("Event", ["Goal", "Exclusion", "Turnover"])

    placeholder = st.empty()
    if event_input == "Goal":
        subevent_input = placeholder.selectbox("Subevent", ['Rebound', 'Goal'])
    elif event_input == "Exclusion":
        subevent_input = placeholder.selectbox("Subevent2", ['Turnover','Lost Ball'])
    else:
        placeholder.empty()
        subevent_input = None

    
    player_input = st.selectbox("Player", [f"Player {i}" for i in range(1, 14)])
    submitted = st.form_submit_button("Add Event")


  

    
if submitted:
        new_row = pd.DataFrame([{
            "Time": time_input,
            "Team": team_input,
            "Event": event_input,
            "Player": player_input
        }])
        st.session_state.events = pd.concat(
            [st.session_state.events, new_row]
        ).drop_duplicates().reset_index(drop=True)

if len(st.session_state.events) == 0:
    st.info("No events yet.")
else:
    st.dataframe(st.session_state.events.sort_values("Time", ascending=False), use_container_width=True)
