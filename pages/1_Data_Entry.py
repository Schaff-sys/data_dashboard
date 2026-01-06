import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
import math
from PIL import Image
from pathlib import Path
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
print("Loading environment variables from:", env_path)
load_dotenv(dotenv_path=env_path, override=True)

db_user = os.getenv("db_user")
db_password = os.getenv("db_password")
db_host = os.getenv("db_host")
db_port = os.getenv("db_port")
db_name = os.getenv("db_name")

if not all([db_user, db_password, db_host, db_port, db_name]):
    raise ValueError("Variables de entorno incompletas.")

engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")


@st.cache_data
def get_competitions():
    query = """
        SELECT DISTINCT "match_competitionId", "match_competitionDisplayName"
        FROM public.mergeddatabasesall
        ORDER BY "match_competitionId"
    """
    return pd.read_sql(query, con=engine)

df = get_competitions()

competition_options = list(df["match_competitionId"]) + ["Add new..."]

selected_competition = st.selectbox(
    "Select competition",
    competition_options,
    format_func=lambda x: f"{x} – {df.loc[df.match_competitionId==x, 'match_competitionDisplayName'].iloc[0]}"
                 if x != "Add new..." else x
)

# If user wants to add a new competition
if selected_competition == "Add new...":
    new_id = st.text_input("Enter new competition ID")
    new_name = st.text_input("Enter new competition name")
    if st.button("Add competition"):
        if new_id and new_name:
            # Insert into database
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO public.mergeddatabasesall ("match_competitionId", "match_competitionDisplayName")
                        VALUES (:id, :name)
                        ON CONFLICT DO NOTHING
                    """),
                    {"id": new_id, "name": new_name}
                )
            st.success(f"Competition {new_name} added!")
            st.cache_data.clear()
            st.experimental_rerun()  # refresh the page to show new competition
        else:
            st.error("Please enter both ID and name")

@st.cache_data

def get_matches(comp_id):
        query = """
            SELECT DISTINCT "matchId", "team_name" FROM public.mergeddatabasesall
            WHERE "match_competitionId" = %s
            ORDER BY "matchId"
        """
        return pd.read_sql(query, con=engine, params=(comp_id, ))

if selected_competition != "Add new...":

    df = get_matches(selected_competition)

    df_clean = df.dropna()

    matches_options = list(df_clean["matchId"].unique()) + ["Add new..."]

    def match_label(x):
        if x != "Add new...":
            teams = df_clean.loc[df_clean.matchId==x, 'team_name'].dropna().unique()
            team_name_str = " vs ".join(teams)
            return f"{x} – {team_name_str}"

    selected_matches = st.selectbox(
        "Select match",
        matches_options,
        format_func=match_label
    )

# If user wants to add a new match
    if selected_matches == "Add new...":
        new_id = st.text_input("Enter new match ID")
        new_name = st.text_input("Enter new match name")
        if st.button("Add match"):
            if new_id and new_name:
                # Insert into database
                with engine.begin() as conn:
                    conn.execute(
                        text("""
                            INSERT INTO public.mergeddatabasesall ("match_competitionId", "match_competitionDisplayName")
                            VALUES (:id, :name)
                            ON CONFLICT DO NOTHING
                        """),
                        {"id": new_id, "name": new_name}
                    )
                st.success(f"Competition {new_name} added!")
                st.cache_data.clear()
                st.experimental_rerun()  # refresh the page to show new competition
        else:
         st.error("Please enter both ID and name")



st.title("🕒 Data Entry")

with st.form("Add Match Id"):
    match_input = st.text_input("Match Id")
    period_input = st.selectbox("Period", ["1st", "2nd", "3rd", "4th", "OT"])
    submitted = st.form_submit_button("Add Match and Period")
        

with st.expander("Events"):

    event_input = st.selectbox("Event", ["6v6", "6v5", "Penalty", "Counter"])
    result_input = st.selectbox("Outcome", ["Goal", "Miss", "Save", "Block", "Turnover", "Exclusion"])

    if "events" not in st.session_state:
        st.session_state.events = pd.DataFrame(columns=["time", "team", "event", "subevent", "outcome", "type"])

    def shot_field():
        return st.selectbox("Shot Type", ["Skip Shot", "Lob Shot", "Normal Shot", "None"])
    
    def turnover_field():
        return st.selectbox("Turnover Type", ["Steal", "Bad Pass", "Offensive Foul", "Shot Clock Violation"])


    if event_input == "6v6" and result_input:
        with st.form("Add Subevent"):
            subevent6v6_input = st.selectbox("6v6 Subevent", ["Press", "Zone 1-2", "Zone 4-5", "M-Zone"])
            time_input = st.text_input("Time (e.g., 12:34)")
            team_input = st.selectbox("Team", ["Home", "Away"])

            if result_input in ["Goal", "Miss", "Save"]:
                shot_input = shot_field()
            elif result_input == "Turnover":
                turnover_input = turnover_field()
            
            player_input = st.selectbox("Player committing", [f"W{i}" for i in range(1, 15)] + [f"B{i}" for i in range(1, 15)])
            player_input2 = st.selectbox("Player affected (if applicable)", [f"W{i}" for i in range(1, 15)] + [f"B{i}" for i in range(1, 15)] + ["N/A"])
            submitted = st.form_submit_button("Add Event")

    if event_input == "6v5":
        with st.form("Add Subevent"):
            subevent6v5_input = st.selectbox("6v5 Subevent", ["1 step", "5 step", "N/A"])
            time_input = st.text_input("Time (e.g., 12:34)")
            team_input = st.selectbox("Team", ["Home", "Away"])

            if result_input in ["Goal", "Miss", "Save"]:
                shot_input = shot_field()
            elif result_input == "Turnover":
                turnover_input = turnover_field()

            player_input = st.selectbox("Player committing", [f"W{i}" for i in range(1, 15)] + [f"B{i}" for i in range(1, 15)])
            player_input2 = st.selectbox("Player affected (if applicable)", [f"W{i}" for i in range(1, 15)] + [f"B{i}" for i in range(1, 15)] + ["N/A"])
            submitted = st.form_submit_button("Add Event")

    if event_input == "Counter":
        with st.form("Add Subevent"):
            subeventcounter_input = st.selectbox("Counter Subevent", ["1-2", "Center", "4-5"])
            time_input = st.text_input("Time (e.g., 12:34)")
            team_input = st.selectbox("Team", ["Home", "Away"])

            if result_input in ["Goal", "Miss", "Save"]:
                shot_input = shot_field()
            elif result_input == "Turnover":
                turnover_input = turnover_field()

            player_input = st.selectbox("Player committing", [f"W{i}" for i in range(1, 15)] + [f"B{i}" for i in range(1, 15)])
            player_input2 = st.selectbox("Player affected (if applicable)", [f"W{i}" for i in range(1, 15)] + [f"B{i}" for i in range(1, 15)] + ["N/A"])
            submitted = st.form_submit_button("Add Event")

    if event_input == "Penalty":
        with st.form("Add Subevent"):
            time_input = st.text_input("Time (e.g., 12:34)")
            team_input = st.selectbox("Team", ["Home", "Away"])
            shot_input = st.selectbox("Shot Type", ["Skip Shot", "Lob Shot", "None"])
            player_input = st.selectbox("Player committing", [f"W{i}" for i in range(1, 15)] + [f"B{i}" for i in range(1, 15)])
            player_input2 = st.selectbox("Player affected (if applicable)", [f"W{i}" for i in range(1, 15)] + [f"B{i}" for i in range(1, 15)] + ["N/A"])
            submitted = st.form_submit_button("Add Event")
        

    csv = st.session_state.events.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📥 Export events as CSV",
        data=csv,
        file_name="water_polo_events.csv",
        mime="text/csv"
)


with st.expander("Shots"):

    st.title("🥅 Goal Shot Map")


    
    # Initialize session state
    if "shots" not in st.session_state:
        st.session_state.shots = pd.DataFrame(columns=["x_shot", "y_shot", "x_location", "y_location", "outcome", "type", "team"])

    # Inputs
    col1, col2 = st.columns(2)
    with col1:
        shot_outcome = st.selectbox("Outcome", ["Goal", "Save", "Miss", "Block"])
        team = st.selectbox("Team", ["Home", "Away"])
    

    if shot_outcome == "Goal" or shot_outcome == "Save" or shot_outcome == "Miss":
        st.markdown("### Click where the ball went on the goal")

        bg_image = Image.open("goal.jpg")

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
            key="goal_canvas_{match_input}_{period_input}",
        )

        st.markdown("### Click where the ball went on the pitch")

        bg_image_pitch = Image.open("pitch.jpg")

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
            key="pitch_canvas_{match_input}_{period_input}",
        )

        # Add shots when user clicks
        if canvas_result1.json_data is not None:
            for obj in canvas_result1.json_data["objects"]:
                x_shot, y_shot = obj["left"], obj["top"]
                # Only add new clicks (avoid duplicates)
                if not any((st.session_state.shots["x_shot"] == x_shot) & (st.session_state.shots["y_shot"] == y_shot)):
                    new_shot = pd.DataFrame([{"x_shot": x_shot, "y_shot": y_shot, "outcome": shot_outcome, "type": "shot_input", "team": team}])
                    st.session_state.shots = pd.concat([st.session_state.shots, new_shot], ignore_index=True)

        if canvas_result2.json_data is not None:
            for obj in canvas_result2.json_data["objects"]:
                x_location, y_location = obj["left"], obj["top"]
                # Match with existing shots without location
                if not any((st.session_state.shots["x_location"] == x_location) & (st.session_state.shots["y_location"] == y_location)):
                    mask = st.session_state.shots["x_location"].isnull() & st.session_state.shots["y_location"].isnull()
                    st.session_state.shots.loc[mask, "x_location"] = x_location
                    st.session_state.shots.loc[mask, "y_location"] = y_location

    if shot_outcome == "Block":
        st.info("Block outcome selected. No shot location needed.")

        st.markdown("### Click where the ball went on the pitch")

        bg_image_pitch = Image.open("pitch.jpg")

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
            key="pitch_canvas_block_{match_input}_{period_input}",
        )


        if canvas_result2.json_data is not None:
            for obj in canvas_result2.json_data["objects"]:
                x_shot, y_shot = None, None
                x_location, y_location = obj["left"], obj["top"]
                # Match with existing shots without location
                if not any((st.session_state.shots["x_location"] == x_location) & (st.session_state.shots["y_location"] == y_location)):
                    new_shot = pd.DataFrame([{"x_location": x_location, "y_location": y_location, "outcome": shot_outcome, "type": "shot_input", "team": team}])
                    st.session_state.shots = pd.concat([st.session_state.shots, new_shot], ignore_index=True)

    csv = st.session_state.shots.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📥 Export shots as CSV",
        data=csv,
        file_name="water_polo_shots.csv",
        mime="text/csv")


with st.expander("Passes"):
    st.title("🏐 Pass Map")

    # Initialize session state
    if "pass_map" not in st.session_state:
        st.session_state.pass_map = pd.DataFrame(columns=["from_x","from_y","to_x","to_y","from_player","to_player", "play_number", "type", "type_of_play"])

    if "current_play" not in st.session_state:
        st.session_state.current_play = 0

    if "temp_click" not in st.session_state:
        st.session_state.temp_click = []  # store start/end clicks

    type_of_play = st.selectbox("Type of Play", ["Regular", "Power Play"])

    # ---- Buttons ----
    col1, col2 = st.columns([1, 3])
    new_play = col1.button("🎬 New Play")

    # When user clicks "New Play", increment play number and clear canvas
    if new_play:
        st.session_state.current_play += 1
        st.session_state.temp_click = []  # clear temporary clicks
        st.session_state.pass_map = st.session_state.pass_map  # optional reassign to trigger refresh
        st.toast(f"Starting play #{st.session_state.current_play}")

        st.write("Click start and end positions of passes")

    if type_of_play == "Power Play":
        bg_image_pitch = Image.open("6v5.jpg")

        # Draw the pool/field
        canvas_result = st_canvas(
            fill_color="rgba(0,0,0,0)",  # no fill
            stroke_width=2,
            stroke_color="red",
            background_color="#cceeff",
            background_image=bg_image_pitch,
            update_streamlit=True,
            height=600,
            width=1000,
            drawing_mode="line",  # for clicks
            key=f"pass_canvas_{st.session_state.current_play}",
        )

        if canvas_result.json_data is not None:
            objects = canvas_result.json_data.get("objects", [])
            for obj in objects:
                x1 = obj["left"] + obj["x1"]
                y1 = obj["top"] + obj["y1"]
                x2 = obj["left"] + obj["x2"]
                y2 = obj["top"] + obj["y2"]

                player_position_values_6v5 = {
                    'player1': (150, 150),
                    'player2': (350, 450),
                    'player4': (600, 450),
                    'player5': (850, 150),
                    'post1': (600, 150),
                    'post2': (350, 150),
                }

                def closest_player(x,y):
                    return min(
                        player_position_values_6v5,
                        key = lambda player: (player_position_values_6v5[player][0] -x)**2 + (player_position_values_6v5[player][1]-y)**2
                    )

                From_Player = closest_player(x1,y1)
        

                To_Player = closest_player(x2,y2)

                temp = pd.DataFrame(
                    [[x1, y1, x2, y2, From_Player, To_Player, st.session_state.current_play, "pass_input", type_of_play]],
                    columns=["from_x", "from_y", "to_x", "to_y", "from_player", "to_player", "play_number", "type", "type_of_play"]
                )

                # Avoid duplicate entries
                if not ((st.session_state.pass_map[["from_x", "from_y", "to_x", "to_y"]] == temp.iloc[0][["from_x", "from_y", "to_x", "to_y"]]).all(axis=1).any()):
                    st.session_state.pass_map = pd.concat([st.session_state.pass_map, temp], ignore_index=True)

    if type_of_play == "Regular":
        bg_image_pitch = Image.open("6v6.jpg")

        # Draw the pool/field
        canvas_result = st_canvas(
            fill_color="rgba(0,0,0,0)",  # no fill
            stroke_width=2,
            stroke_color="red",
            background_color="#cceeff",
            background_image=bg_image_pitch,
            update_streamlit=True,
            height=600,
            width=1000,
            drawing_mode="line",  # for clicks
            key=f"pass_canvas_{st.session_state.current_play}",
        )

        # ---- Record passes ----
    if canvas_result.json_data is not None:
        objects = canvas_result.json_data.get("objects", [])
        for obj in objects:
            x1 = obj["left"] + obj["x1"]
            y1 = obj["top"] + obj["y1"]
            x2 = obj["left"] + obj["x2"]
            y2 = obj["top"] + obj["y2"]

            player_position_values_6v6 = {
                'player1': (150, 150),
                'player2': (300, 400),
                'player3': (500, 490),
                'player4': (700, 400),
                'player5': (850, 150),
                'player6': (500, 150),
            }

            def closest_player(x,y):
                return min(
                    player_position_values_6v6,
                    key = lambda player: (player_position_values_6v6[player][0] -x)**2 + (player_position_values_6v6[player][1]-y)**2
                )

            From_Player = closest_player(x1,y1)
    

            To_Player = closest_player(x2,y2)

            temp = pd.DataFrame(
                [[x1, y1, x2, y2, From_Player, To_Player, st.session_state.current_play, "pass_input", type_of_play]],
                columns=["from_x", "from_y", "to_x", "to_y", "from_player", "to_player", "play_number", "type", "type_of_play"]
            )

            # Avoid duplicate entries
            if not ((st.session_state.pass_map[["from_x", "from_y", "to_x", "to_y"]] == temp.iloc[0][["from_x", "from_y", "to_x", "to_y"]]).all(axis=1).any()):
                st.session_state.pass_map = pd.concat([st.session_state.pass_map, temp], ignore_index=True)


    csv = st.session_state.pass_map.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📥 Export passes as CSV",
        data=csv,
        file_name="water_polo_passes.csv",
        mime="text/csv")
    
with st.expander("Positions"):
    if "team_lineup" not in st.session_state:
        st.session_state.team_lineup = pd.DataFrame(columns=["match", "position_1", "position_2", "position_3", "position_4", "position_5", "position_6", "centre", "goalkeeper", "type"])
    

    st.write ("### Player Positions")

    st.write("Input starting player positions")

    with st.form("Add line-ups"):
        match_input = st.text_input("Match Id")
        team_input = st.selectbox("Team", ["Home", "Away"])
        position1 = st.selectbox("Position 1", [f"W{i}" for i in range(1, 15)])
        position2 = st.selectbox("Position 2", [f"W{i}" for i in range(1, 15)])
        position3 = st.selectbox("Position 3", [f"W{i}" for i in range(1, 15)])
        position4 = st.selectbox("Position 4", [f"W{i}" for i in range(1, 15)])
        position5 = st.selectbox("Position 5", [f"W{i}" for i in range(1, 15)])
        position6 = st.selectbox("Position 6", [f"W{i}" for i in range(1, 15)])
        position7 = st.selectbox("Centre", [f"W{i}" for i in range(1, 15)])
        goalkeeper = st.selectbox("Goalkeeper", [f"W{i}" for i in range(1, 15)])
        submitted = st.form_submit_button("Add Line-up")

        if submitted:
            new_row = pd.DataFrame([{
                "match": match_input,
                "position_1": position1,
                "position_2": position2,
                "position_3": position3,
                "position_4": position4,
                "position_5": position5,
                "position_6": position6,
                "centre": position7,
                "goalkeeper": goalkeeper,
                "team": team_input,
                "type": "lineup_input",
            }])
            st.session_state.team_lineup = pd.concat(
                [st.session_state.team_lineup, new_row]
            ).drop_duplicates().reset_index(drop=True)


    csv = st.session_state.team_lineup.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export player positions as CSV",
        data=csv,
        file_name="water_polo_player_positions.csv",
        mime="text/csv")

    st.write("### Substitutions")



    if "substitutions" not in st.session_state:
        st.session_state.substitutions = pd.DataFrame(columns=["time", "match", "team", "player_substituted", "player_coming_on", "type"])
        
    
    with st.form("Add Subsitution"):
        time_input = st.text_input("Time (e.g., 12:34)")
        match_input = st.text_input("Match Id")
        team_input = st.selectbox("Team", ["Home", "Away"])
        player_input = st.selectbox("Player substituted", [f"W{i}" for i in range(1, 15)] + [f"B{i}" for i in range(1, 15)])
        player_input2 = st.selectbox("Player coming on", [f"W{i}" for i in range(1, 15)] + [f"B{i}" for i in range(1, 15)] + ["N/A"])
        submitted = st.form_submit_button("Add Substitution")

        
        
    if submitted:
            new_row = pd.DataFrame([{
                "time": time_input,
                "match": match_input,
                "team": team_input,
                "player_substituted": player_input,
                "player_coming_on": player_input2,
                "type": "substitution_input"
            }])
            st.session_state.substitutions = pd.concat(
                [st.session_state.substitutions, new_row]
            ).drop_duplicates().reset_index(drop=True)

    
    csv = st.session_state.substitutions.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export substitutions as CSV",
        data=csv,
        file_name="water_polo_substitutions.csv",
        mime="text/csv")

st.session_state.all = pd.concat([
    st.session_state.events,
    st.session_state.shots,
    st.session_state.pass_map,
    st.session_state.team_lineup,
    st.session_state.substitutions
], ignore_index=True)

csv = st.session_state.all.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Export all as CSV",
    data=csv,
    file_name="water_polo_events.csv",
    mime="text/csv"
)