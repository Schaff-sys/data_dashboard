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
    background_image=bg_image_pitch,
    update_streamlit=True,
    height=500,
    width=600,
    drawing_mode="point",  # for clicks
    key="pass_canvas",
)

# Plot players as points on canvas
for player, (x, y) in player_positions.items():
    st.write(f"{player}: ({int(x)},{int(y)})")  # can replace with markers if using matplotlib/plotly

# Capture clicks
if canvas_result.json_data is not None:
    for obj in canvas_result.json_data["objects"]:
        x, y = obj["left"], obj["top"]
        st.session_state.temp_click.append((x, y))
        if len(st.session_state.temp_click) == 2:
            (x1, y1), (x2, y2) = st.session_state.temp_click
            from_player = min(player_positions.keys(), key=lambda p: math.hypot(player_positions[p][0]-x1, player_positions[p][1]-y1))
            to_player = min(player_positions.keys(), key=lambda p: math.hypot(player_positions[p][0]-x2, player_positions[p][1]-y2))
            new_pass = pd.DataFrame([{
                "From_X": x1, "From_Y": y1,
                "To_X": x2, "To_Y": y2,
                "From_Player": from_player,
                "To_Player": to_player
            }])
            st.session_state.pass_map = pd.concat([st.session_state.pass_map, new_pass]).reset_index(drop=True)
            st.session_state.temp_click = []

st.dataframe(st.session_state.pass_map)
