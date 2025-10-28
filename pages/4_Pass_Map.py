import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from PIL import Image

st.title("🥅 Goal Shot Map")

# Initialize session state
if "shots" not in st.session_state:
    st.session_state.shots = pd.DataFrame(columns=["x_shot", "y_shot", "x_location", "y_location", "Outcome"])

# Inputs
col1, col2 = st.columns(2)
with col1:
    shot_outcome = st.selectbox("Outcome", ["Goal", "Save", "Miss", "Block"])

if shot_outcome == "Goal" or shot_outcome == "Save" or shot_outcome == "Miss":
    st.markdown("### Click where the ball went on the goal")

    bg_image = Image.open("goal2.jpg")

    canvas_result1 = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",  # Click marker color
        stroke_width=2,
        stroke_color="red",
        background_color="#0D3B66",
        background_image=bg_image,
        update_streamlit=True,
        height=300,
        width=800,
        drawing_mode="point",  # Clicks only
        key="goal_canvas",
    )

    st.markdown("### Click where the ball went on the pitch")

    bg_image_pitch = Image.open("Pool-Location-Screen-1500x1744.png.webp")

    canvas_result2 = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",  # Click marker color
        stroke_width=2,
        stroke_color="red",
        background_color="#e6f7ff",
        background_image=bg_image_pitch,
        height=800,
        width=800,
        update_streamlit=True,
        drawing_mode="point",  # Clicks only
        key="pitch_canvas",
    )

    # Add shots when user clicks
    if canvas_result1.json_data is not None:
        for obj in canvas_result1.json_data["objects"]:
            x_shot, y_shot = obj["left"], obj["top"]
            # Only add new clicks (avoid duplicates)
            if not any((st.session_state.shots["x_shot"] == x_shot) & (st.session_state.shots["y_shot"] == y_shot)):
                new_shot = pd.DataFrame([{"x_shot": x_shot, "y_shot": y_shot, "Outcome": shot_outcome}])
                st.session_state.shots = pd.concat([st.session_state.shots, new_shot], ignore_index=True)

    if canvas_result2.json_data is not None:
        for obj in canvas_result2.json_data["objects"]:
            x_location, y_location = obj["left"], obj["top"]
            # Match with existing shots without location
            if not any((st.session_state.shots["x_location"] == x_location) & (st.session_state.shots["y_location"] == y_location)):
                mask = st.session_state.shots["x_location"].isnull() & st.session_state.shots["y_location"].isnull()
                st.session_state.shots.loc[mask, "x_location"] = x_location
                st.session_state.shots.loc[mask, "y_location"] = y_location

    # Show data
    st.dataframe(st.session_state.shots)

if shot_outcome == "Block":
    st.info("Block outcome selected. No shot location needed.")

    st.markdown("### Click where the ball went on the pitch")

    bg_image_pitch = Image.open("Pool-Location-Screen-1500x1744.png.webp")

    canvas_result2 = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",  # Click marker color
        stroke_width=2,
        stroke_color="red",
        background_color="#e6f7ff",
        background_image=bg_image_pitch,
        height=800,
        width=800,
        update_streamlit=True,
        drawing_mode="point",  # Clicks only
        key="pitch_canvas",
    )


    if canvas_result2.json_data is not None:
        for obj in canvas_result2.json_data["objects"]:
            x_shot, y_shot = None, None
            x_location, y_location = obj["left"], obj["top"]
            # Match with existing shots without location
            if not any((st.session_state.shots["x_location"] == x_location) & (st.session_state.shots["y_location"] == y_location)):
                new_shot = pd.DataFrame([{"x_location": x_location, "y_location": y_location, "Outcome": shot_outcome}])
                st.session_state.shots = pd.concat([st.session_state.shots, new_shot], ignore_index=True)

    # Show data
    st.dataframe(st.session_state.shots)

import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
import math

st.title("🏐 Pass Map")

# Initialize session state
if "pass_map" not in st.session_state:
    st.session_state.pass_map = pd.DataFrame(columns=["From_X","From_Y","To_X","To_Y","From_Player","To_Player"])

if "temp_click" not in st.session_state:
    st.session_state.temp_click = []  # store start/end clicks

# Player positions in an arc (7 players)
player_positions = {
    f"Player {i+1}": (200 + 150*math.cos(math.pi*(i-3)/6), 400 - 150*math.sin(math.pi*(i-3)/6))
    for i in range(7)
}

st.write("Click start and end positions of passes")

bg_image_pitch = Image.open("players.webp")

# Draw the pool/field
canvas_result = st_canvas(
    fill_color="rgba(0,0,0,0)",  # no fill
    stroke_width=2,
    stroke_color="blue",
    background_color="#cceeff",
    update_streamlit=True,
    height=500,
    width=600,
    drawing_mode="line",  # for clicks
    key="pass_canvas",
)

if canvas_result.json_data is not None:
    objects = canvas_result.json_data.get("objects", [])
    if objects:
        for obj in objects:
            x1 = obj['left'] + obj['x1']
            y1 = obj['top'] + obj['y1']
            x2 = obj['left'] + obj['x2']
            y2 = obj['top'] + obj['y2']
            st.session_state.temp_click = pd.DataFrame(
                [[x1, y1, x2, y2]],
                columns=["From_X", "From_Y", "To_X", "To_Y"]
            )
            if not ((st.session_state.pass_map[['From_X','From_Y','To_X','To_Y']]
                == st.session_state.temp_click.iloc[0]).all(axis=1).any()):
                st.session_state.pass_map = pd.concat(
                    [st.session_state.pass_map, st.session_state.temp_click],
                    ignore_index=True
                )


st.dataframe(st.session_state.pass_map)

if "team_lineup" not in st.session_state:
    st.session_state.team_lineup = pd.DataFrame(columns=["Match", "Position 1", "Position 2", "Position 3", "Position 4", "Position 5", "Position 6", "Centre", "Goalkeeper"])


st.write ("### Player Positions")

st.write("Input player positions for home team")

with st.form("Add Home Substitution"):
    position1 = st.selectbox("Position 1", [f"Player {i}" for i in range(1, 14)])
    position2 = st.selectbox("Position 2", [f"Player {i}" for i in range(1, 14)])
    position3 = st.selectbox("Position 3", [f"Player {i}" for i in range(1, 14)])
    position4 = st.selectbox("Position 4", [f"Player {i}" for i in range(1, 14)])
    position5 = st.selectbox("Position 5", [f"Player {i}" for i in range(1, 14)])
    position6 = st.selectbox("Position 6", [f"Player {i}" for i in range(1, 14)])
    position7 = st.selectbox("Centre", [f"Player {i}" for i in range(1, 14)])
    Goalkeeper = st.selectbox("Goalkeeper", [f"Player {i}" for i in range(1, 14)])
    submitted = st.form_submit_button("Add Event")

st.write ("Input player positions for away team")

with st.form("Add Away Substitution"):
    match_input = st.text_input("Match (e.g., Team A vs Team B)")
    position1 = st.selectbox("Position 1", [f"Player {i}" for i in range(1, 14)])
    position2 = st.selectbox("Position 2", [f"Player {i}" for i in range(1, 14)])
    position3 = st.selectbox("Position 3", [f"Player {i}" for i in range(1, 14)])
    position4 = st.selectbox("Position 4", [f"Player {i}" for i in range(1, 14)])
    position5 = st.selectbox("Position 5", [f"Player {i}" for i in range(1, 14)])
    position6 = st.selectbox("Position 6", [f"Player {i}" for i in range(1, 14)])
    position7 = st.selectbox("Centre", [f"Player {i}" for i in range(1, 14)])
    Goalkeeper = st.selectbox("Goalkeeper", [f"Player {i}" for i in range(1, 14)])
    submitted = st.form_submit_button("Add Event")

if submitted:
    new_row = pd.DataFrame([{
        "Match": match_input,
        "Position 1": position1,
        "Position 2": position2,
        "Position 3": position3,
        "Position 4": position4,
        "Position 5": position5,
        "Position 6": position6,
        "Centre": position7,
        "Goalkeeper": Goalkeeper,
    }])
    st.session_state.team_lineup = pd.concat(
        [st.session_state.team_lineup, new_row]
    ).drop_duplicates().reset_index(drop=True)

st.dataframe(st.session_state.team_lineup)

st.write("### Substitutions")

if "substitutions" not in st.session_state:
    st.session_state.substitutions = pd.DataFrame(columns=["Time", "Match", "Team", "Player substituted", "Player coming on"])

with st.form("Add Subsitution"):
    time_input = st.text_input("Time (e.g., 12:34)")
    match_input = st.text_input("Match (e.g., Team A vs Team B)")
    team_input = st.selectbox("Team", ["Team A", "Team B"])
    player_input = st.selectbox("Player substituted", [f"Player {i}" for i in range(1, 14)])
    player_input2 = st.selectbox("Player coming on", [f"Player {i}" for i in range(1, 14)] + ["N/A"])
    submitted = st.form_submit_button("Add Event")

    
  
    
if submitted:
        new_row = pd.DataFrame([{
            "Time": time_input,
            "Match": match_input,
            "Team": team_input,
            "Player substituted": player_input,
            "Player coming on": player_input2,
        }])
        st.session_state.substitutions = pd.concat(
            [st.session_state.substitutions, new_row]
        ).drop_duplicates().reset_index(drop=True)

if len(st.session_state.substitutions) == 0:
    st.info("No events yet.")
else:
    st.dataframe(st.session_state.substitutions.sort_values("Time", ascending=True), use_container_width=True)

csv = st.session_state.substitutions.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Export Events as CSV",
    data=csv,
    file_name="water_polo_events.csv",
    mime="text/csv"
)