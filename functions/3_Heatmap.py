import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import plotly.graph_objects as go
import os

# -----------------------------
# Load Data
# -----------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
current_file = os.path.join(current_dir, '4.Cleaned_data.csv')
datos = pd.read_csv(current_file)

# -----------------------------
# Helper Functions
# -----------------------------
def value_for_other_team(row):
    if row['homeTeamId'] == row['teamId']:
        return row['awayTeamId']
    elif row['awayTeamId'] == row['teamId']:
        return row['homeTeamId']
    else:
        return None  

datos['other_team'] = datos.apply(value_for_other_team, axis=1)
datos['shot_teamId'] = datos['teamId']

# Define teams and matches
teams = {
    'Jadran M:tel HN': 2,
    'VK Novi Beograd': 1240,
    'FTC-Telekom': 38,
    'Rari Nantes Savona': 4718,
    'CSM Oradea': 13,
    'Vasas Plaket': 4697,
    'VPK Primorac': 9,
    'CSA Steaua': 68,
    'Dinamo Tbilisi': 40,
    'Jadran Split': 3,
    'Radnički Kragujevac': 73,
    'Olympiacos Piraeus': 34,
    'KEIO CN Sabadell': 3092,
    'Zodiac CNAB': 36,
    'Hannover 1898': 39,
    'CN Marseille': 41
}

match_dict = {
    'VK Novi Beograd vs CSA Steaua': 10629,
    'Hannover 1898 vs CSM Oradea': 10630,
    'FTC-Telekom  vs Dinamo Tbilisi': 10631,
    'Jadran Split vs Radnički Kragujevac': 10632,
    # ... (add all your matches here)
}

# Define filters
filters = {
    'Goals Scored': lambda team_id: datos[(datos['shot_isGoal'] == 1) & (datos['shot_type'] != 'Penalty') & (datos['shot_teamId'] == team_id)],
    'Goals Conceded': lambda team_id: datos[(datos['shot_isGoal'] == 1) & (datos['shot_type'] != 'Penalty') & (datos['other_team'] == team_id)],
    'Exclusions Drawn': lambda team_id: datos[(datos['exclusion_byId'] > 0) & (datos['shot_teamId'] == team_id)],
    'Blocks Made': lambda team_id: datos[(datos['shot_blockedById'] > 0) & (datos['shot_teamId'] == team_id)],
    'Goals Direct From Foul': lambda team_id: datos[(datos['shot_isDirectFromFoul'] == 1) & (datos['shot_teamId'] == team_id)],
    'Missed Shots': lambda team_id: datos[(datos['shot_isGoal'] == 0) & (datos['shot_teamId'] == team_id)],
    'Power Play Goals Scored': lambda team_id: datos[(datos['shot_type'] == 'Power_Play') & (datos['shot_isGoal'] == 1) & (datos['shot_teamId'] == team_id)],
    'Power Play Goals Conceded': lambda team_id: datos[(datos['shot_type'] == 'Power_Play') & (datos['shot_isGoal'] == 1) & (datos['other_team'] == team_id)],
    'Regular Attack Goals Scored': lambda team_id: datos[(datos['shot_type'] == 'Regular_Attack') & (datos['shot_isGoal'] == 1) & (datos['shot_teamId'] == team_id)],
    'Regular Attack Goals Conceded': lambda team_id: datos[(datos['shot_type'] == 'Regular_Attack') & (datos['shot_isGoal'] == 1) & (datos['other_team'] == team_id)],
}

# -----------------------------
# Functions for Heatmap
# -----------------------------
def filter_for_match_values(datos, match_id):
    if match_id != 0:
        return datos[datos['matchId'] == match_id]
    return datos

def shot_map_create(team_id, value, match_id):
    goals_df = filters[value](team_id)
    x_shots = filter_for_match_values(goals_df, match_id)['locationX'].fillna(0).replace(np.inf, 0)
    y_shots = filter_for_match_values(goals_df, match_id)['locationY'].fillna(0).replace(np.inf, 0)

    if len(x_shots) < 1 or len(y_shots) < 1 or (x_shots.sum() == 0 and y_shots.sum() == 0):
        return None, None, None

    xy = np.vstack([x_shots, y_shots])
    try:
        bw_method = 0.6 if len(x_shots) < 50 else 0.3
        kde = gaussian_kde(xy, bw_method=bw_method)
    except ValueError:
        return None, None, None

    x_grid = np.linspace(0, 1, 300)
    y_grid = np.linspace(0, 1, 300)
    X, Y = np.meshgrid(x_grid, y_grid)
    positions = np.vstack([X.ravel(), Y.ravel()])
    Z = np.reshape(kde(positions).T, X.shape)
    return x_grid, y_grid, Z

def get_shot_map(x_grid, y_grid, Z, selected_value):
    fig = go.Figure()
    if Z is None or x_grid is None or y_grid is None:
        fig.add_annotation(
            text="Values are not sufficient, please enter new ones!",
            x=0.5, y=0.5, xref='paper', yref='paper', showarrow=False
        )
        return fig

    custom_colorscale = [
        [0.0, 'lightblue'],
        [0.09, 'lightblue'],
        [0.1, 'rgb(26,152,80)'],
        [0.3, 'rgb(166,217,106)'],
        [0.5, 'rgb(255,255,191)'],
        [0.7, 'rgb(253,174,97)'],
        [0.9, 'rgb(244,109,67)'],
        [1.0, 'rgb(165,0,38)']
    ]

    fig.add_trace(go.Contour(
        x=x_grid, y=y_grid, z=Z,
        colorscale=custom_colorscale, ncontours=100,
        contours_coloring='fill', opacity=1,
        zmin=0, zmax=max(12, Z.max()),
        showscale=True
    ))

    # Field border
    fig.add_shape(type="rect", x0=0, x1=1, y0=0, y1=1, line=dict(color="black"))
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0,1]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0,1], scaleanchor="x"),
        plot_bgcolor='lightblue', paper_bgcolor='lightblue',
        width=1000, height=600, margin=dict(l=0, r=0, t=40, b=40)
    )
    return fig

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Water Polo Champions League Heatmap")

selected_team = st.selectbox("Select Team", list(teams.keys()))
selected_value = st.selectbox("Select Value", list(filters.keys()))
selected_match = st.selectbox("Select Match", list(match_dict.keys()))

team_id = teams[selected_team]
match_id = match_dict[selected_match]

x_grid, y_grid, Z = shot_map_create(team_id, selected_value, match_id)
fig = get_shot_map(x_grid, y_grid, Z, selected_value)

st.plotly_chart(fig, use_container_width=True)
