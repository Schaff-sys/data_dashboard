import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
import math
from PIL import Image
from pathlib import Path
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Resize function: Scales images to fit canvas max dimensions while preserving aspect ratio
def resize_for_canvas(img, max_w=800, max_h=500):
    w, h = img.size
    scale = min(max_w/w, max_h/h, 1.0)  # Never upscale, fit within bounds
    new_w, new_h = int(w*scale), int(h*scale)
    return img.resize((new_w, new_h), Image.Resampling.LANCZOS)

# FIRST LINE after imports - Set wide layout for canvas display
st.set_page_config(layout="wide")

# Custom CSS: Ensure canvases use full available width without overflow
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 1rem;
        max-width: 1400px;  /* Full browser width */
    }
    section[data-testid="stCanvas"] {
        width: 100% !important;
        max-width: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialise session state: Create empty events DataFrame with all required columns on first load
if "events" not in st.session_state:
        st.session_state.events = pd.DataFrame(columns=["match", "period", "event", 
                                                        "subevent", "result", "time", 
                                                        "team", "shot_type","turnover_type", 
                                                        "player_in_attack", "player_in_defence",
                                                        "x_shot", "y_shot", "x_location", 
                                                        "y_location", "passes", "drive_start_input", "drive_end_input"])
        
# Canvas versioning: Incremented to force canvas redraw/clear after form submission
if "canvas_version" not in st.session_state:
    st.session_state.canvas_version = 0

st.title("🕒 Data Entry")

# Basic event metadata inputs
match_input = st.text_input("Match Id")
period_input = st.radio('Period', ["1st", "2nd", "3rd", "4th", "OT"], horizontal=True)
event_input = st.radio('Event', ['6v6', '6v5', 'Penalty', 'Counter'], horizontal=True)

st.markdown("### Click where the ball went on the goal")

# Initialize shot/location coordinates to None (will be populated from canvas clicks)
x_shot = y_shot = None
x_location = y_location = None

# Pass coordinates (will be populated from pass map canvas)
x1 = y1 = x2 = y2 = None
From_Player = To_Player = None

# Goal canvas: Load and resize goal image, create point-drawing canvas
bg_image = Image.open("goal.jpg")
bg_image = resize_for_canvas(bg_image)
goal_width, goal_height = bg_image.size

goal_canvas = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",  # Click marker color
        stroke_width=2,
        stroke_color="red",
        background_color="#0D3B66",
        background_image=bg_image,
        update_streamlit=True,
        height=goal_height,
        width=goal_width,
        drawing_mode="point",  # Clicks only
        key=f"goal_canvas_{st.session_state.canvas_version}",  # Version forces redraw
    )

st.markdown("### Click where the ball went on the pitch")

# Pitch canvas: Load and resize pitch image, create point-drawing canvas
bg_image_pitch = Image.open("pitch.jpg")
bg_image_pitch = resize_for_canvas(bg_image_pitch)
pitch_width, pitch_height = bg_image_pitch.size
pitch_canvas = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",  # Click marker color
        stroke_width=2,
        stroke_color="red",
        background_color="#e6f7ff",
        background_image=bg_image_pitch,
        height=pitch_height,
        width=pitch_width,
        update_streamlit=True,
        drawing_mode="point",  # Clicks only
        key=f"pitch_canvas_{st.session_state.canvas_version}",
    )

# Extract shot coordinates from goal canvas (takes LAST point drawn - most recent click)
if goal_canvas.json_data is not None:
        for obj in goal_canvas.json_data["objects"]:
            x_shot, y_shot = obj["left"], obj["top"]  # Point coords = left/top

# Extract location coordinates from pitch canvas (takes LAST point drawn)
if pitch_canvas.json_data is not None:
        for obj in pitch_canvas.json_data["objects"]:
            x_location, y_location = obj["left"], obj["top"]

st.subheader("🏐 Pass Map")

# 6v5 Pass Map Logic
if event_input == "6v5":
    # Load and resize 6v5 pass map image
    bg_image_pass = Image.open("6v5.jpg")
    bg_image_pass = resize_for_canvas(bg_image_pass)
    pass_width, pass_height = bg_image_pass.size

    # Draw the pool/field - LINE drawing canvas for passes
    canvas_result3 = st_canvas(
        fill_color="rgba(0,0,0,0)",  # no fill
        stroke_width=2,
        stroke_color="red",
        background_color="#cceeff",
        background_image=bg_image_pass,
        update_streamlit=True,
        height=pass_height,
        width=pass_width,
        drawing_mode="line",  # for clicks
        key=f"pass_canvas_{st.session_state.canvas_version}",
    )

    # Initialize empty list to store all pass data
    all_passes = []

    # Parse all lines from 6v5 canvas
    if canvas_result3.json_data is not None:
        objects = canvas_result3.json_data.get("objects", [])
        for i, obj in enumerate(objects):
            if obj.get("type") == "line":
                # Extract absolute coordinates: bounding_box_position + relative_endpoints
                x1 = obj["left"] + obj["x1"]
                y1 = obj["top"] + obj["y1"]
                x2 = obj["left"] + obj["x2"]
                y2 = obj["top"] + obj["y2"]

            # 6v5 player/post positions (calibrated to resized canvas)
            player_position_values_6v5 = {
                'player1': (680, 120),
                'player2': (480, 320),
                'player4': (300, 315),
                'player5': (130, 120),
                'Second Post': (300, 120),
                'First Post': (480, 120),
            }

            # Find closest player/post to pass endpoints using Euclidean distance
            def closest_player(x,y):
                return min(
                    player_position_values_6v5,
                    key = lambda player: (player_position_values_6v5[player][0] -x)**2 + (player_position_values_6v5[player][1]-y)**2
                )

            from_player = closest_player(x1,y1)
            to_player = closest_player(x2,y2)

            # Store complete pass data
            all_passes.append({
                "pass_id": i,
                "from_x": x1, "from_y": y1, "from_player": from_player,
                "to_x": x2, "to_y": y2, "to_player": to_player
            })

# 6v6 Pass Map Logic  
if event_input == "6v6":
    # Load and resize 6v6 pass map image
    bg_image_pass1 = Image.open("6v6.jpg")
    bg_image_pass1 = resize_for_canvas(bg_image_pass1)
    pass1_width, pass1_height = bg_image_pass1.size

    # Draw the pool/field - LINE drawing canvas for passes
    canvas_result4 = st_canvas(
        fill_color="rgba(0,0,0,0)",  # no fill
        stroke_width=2,
        stroke_color="red",
        background_color="#cceeff",
        background_image=bg_image_pass1,
        update_streamlit=True,
        height=pass1_height,
        width=pass1_width,
        drawing_mode="line",  # for clicks
        key=f"6v6_canvas_{st.session_state.canvas_version}",
    )

    # Initialize empty list to store all pass data
    all_passes = []

    # Parse all lines from 6v6 canvas
    if canvas_result4.json_data is not None:
        objects = canvas_result4.json_data.get("objects", [])
        for i, obj in enumerate(objects):
            if obj.get("type") == "line":
                # Extract absolute coordinates: bounding_box_position + relative_endpoints
                x1 = obj["left"] + obj["x1"]
                y1 = obj["top"] + obj["y1"]
                x2 = obj["left"] + obj["x2"]
                y2 = obj["top"] + obj["y2"]

            # 6v6 player/pit positions (calibrated to resized canvas)
            player_position_values_6v6 = {
                'player1': (650, 120),
                'player2': (550, 310),
                'player3': (400, 375),
                'player4': (250, 310),
                'player5': (150, 120),
                'pit': (400, 120),
            }

            # Find closest player/pit to pass endpoints using Euclidean distance
            def closest_player(x,y):
                return min(
                    player_position_values_6v6,
                    key = lambda player: (player_position_values_6v6[player][0] -x)**2 + (player_position_values_6v6[player][1]-y)**2
                )

            from_player = closest_player(x1,y1)
            to_player = closest_player(x2,y2)

            # Store complete pass data
            all_passes.append({
                "pass_id": i,
                "from_x": x1, "from_y": y1, "from_player": from_player,
                "to_x": x2, "to_y": y2, "to_player": to_player
            })

# Event entry form with auto-clear on submit
with st.form('Quick Add', clear_on_submit=True):
    result_input = st.radio('Outcome', ["Goal", "Miss", "Save", "Block", "Turnover", "Exclusion"], horizontal=True)
    time_input = st.text_input("Time (e.g., 12:34)")
    team_input = st.radio('Team', ["Home", "Away"], horizontal=True)
    shot_input = st.radio("Shot Type", ["None", "Skip Shot", "Lob Shot", "Normal Shot"], horizontal=True)
    turnover_input = st.radio("Turnover Type", ["None", "Steal", "Bad Pass", "Offensive Foul", "Shot Clock Violation"], horizontal=True)
    subevent6v6_input = st.radio("6v6 Subevent", ["None", "Press", "Zone 1-2", "Zone 4-5", "M-Zone"], horizontal=True)   
    subevent6v5_input = st.radio("6v5 Subevent", ["None", "In 1-2", "In 4-5"], horizontal=True) 
    player_number = [i for i in range(1,15)]
    playerattack_input = st.radio("Player in attack", player_number, horizontal=True)
    playerdefence_input = st.radio("Player in defence", player_number, horizontal=True)
    drive_start_input = st.radio("Drive From", ["None", "1", "2", "3", "4", "5", "Multiple"] ,horizontal=True)
    drive_end_input = st.radio("Drive To", ["None", "1", "2", "3", "4", "5", "Pit", "Second Pit"] ,horizontal=True)

    submitted = st.form_submit_button('Add event')
    if submitted:
            # Create new event row with all canvas data and form inputs
            new_row = {
                "match": match_input,
                "event": event_input, 
                "period": period_input,
                "subevent": subevent6v5_input or subevent6v6_input,  # Prioritizes 6v5 if both selected
                "result": result_input,
                "time": time_input, 
                "team": team_input, 
                "shot_type": shot_input,
                "turnover_type": turnover_input, 
                "player_in_attack": playerattack_input, 
                "player_in_defence": playerdefence_input,
                "x_shot": x_shot,
                "y_shot": y_shot,
                "x_location": x_location,
                "y_location": y_location,
                "passes": all_passes,  # Complete list of all passes drawn
                "drive_start_input": drive_start_input,
                "drive_end_input": drive_end_input                                                                                                                                                                                                                                                                                                                                                                       
            }
            
            # Append new event to session state DataFrame
            st.session_state.events = pd.concat([st.session_state.events, pd.DataFrame([new_row])], ignore_index=True)
            st.success("Event added! Canvases cleared.")
            st.session_state.canvas_version += 1  # Force all canvases to clear/redraw
            st.rerun()  # Refresh app with cleared canvases and form

# Export all collected events as CSV
csv = st.session_state.events.to_csv(index=False).encode('utf-8')
st.download_button(
label="📥 Export all as CSV",
data=csv,
file_name="water_polo_events.csv",
mime="text/csv"
)
