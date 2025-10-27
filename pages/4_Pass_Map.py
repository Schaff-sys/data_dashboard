import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

st.title("🏐 Interactive Pass Map")

if "pass_map" not in st.session_state:
    st.session_state.pass_map = pd.DataFrame(columns=["From_X","From_Y","To_X","To_Y","From_Player","To_Player"])
if "temp_click" not in st.session_state:
    st.session_state.temp_click = []

col1, col2 = st.columns(2)
from_player = col1.selectbox("From Player", [f"Player {i}" for i in range(1,14)])
to_player = col2.selectbox("To Player", [f"Player {i}" for i in range(1,14)])

fig = go.Figure()
fig.update_layout(
    xaxis=dict(range=[0,10], visible=False),
    yaxis=dict(range=[0,5], visible=False, scaleanchor="x"),
    height=500,
    title="Click once for pass origin, once for destination",
)

for _, row in st.session_state.pass_map.iterrows():
    fig.add_trace(go.Scatter(
        x=[row["From_X"], row["To_X"]],
        y=[row["From_Y"], row["To_Y"]],
        mode="lines+markers",
        line=dict(width=2, color="blue"),
        marker=dict(size=8, color="blue"),
        text=[row["From_Player"], row["To_Player"]],
        hoverinfo="text"
    ))

clicked_points = plotly_events(fig, click_event=True, hover_event=False, select_event=False)

if clicked_points:
    x = clicked_points[0]["x"]
    y = clicked_points[0]["y"]
    st.session_state.temp_click.append((x,y))

    if len(st.session_state.temp_click) == 2:
        (x1, y1), (x2, y2) = st.session_state.temp_click
        new_pass = pd.DataFrame([{
            "From_X": x1,
            "From_Y": y1,
            "To_X": x2,
            "To_Y": y2,
            "From_Player": from_player,
            "To_Player": to_player
        }])
        st.session_state.pass_map = pd.concat([st.session_state.pass_map, new_pass]).reset_index(drop=True)
        st.session_state.temp_click = []
        st.success(f"Pass added: {from_player} → {to_player}")

st.dataframe(st.session_state.pass_map)
