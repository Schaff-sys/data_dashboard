import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go 
st.title("📊 Team Stats")

st.title("Upload and store CSV")

# 1️⃣ File uploader
uploaded_file = st.file_uploader("Upload a CSV", type=["csv"])

if "all" not in st.session_state:
        st.session_state.all = pd.DataFrame(columns=["time", "team", "event", "subevent", "outcome", "type", "period"])

# 2️⃣ If file uploaded, load and store in session_state
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.session_state.my_data = df 

## 
## Header metrics
##

# Usa los datos existentes si no se subió nada nuevo
if "my_data" in st.session_state:
    df = st.session_state.my_data
else:
    df = st.session_state.all


if "minute" not in st.session_state.all:
    st.session_state.minute = 0
    st.session_state.team_a_score = 0
    st.session_state.team_b_score = 0

home_team_score = (
     ((df['team']=='Home') & (df['type']=='event_input') & (df['outcome']=='Goal')).sum()
     
)

away_team_score = (
     ((df['team']=='Away') & (df['type']=='event_input') & (df['outcome']=='Goal')).sum()
)

if df is not None:
    df.sort_values(by=['time', 'period'], ascending=[False, False])

def get_latest_minute(df):
    if not df.empty:
        ultimo_minuto = df['time'].iloc[-1]
        return ultimo_minuto
    return 0

def get_current_period(df):
    if not df.empty:
        periodo_actual = df['period'].iloc[-1]
        return periodo_actual 
    return 0

col1, col2, col3 = st.columns([2, 2, 2])
col1.metric("Home Team", home_team_score, delta="Pred: 8")
col2.metric("Time", get_latest_minute(df), delta=f"Period: {get_current_period(df)}")
col3.metric("Away Team", away_team_score, delta="Pred: 6")

st.divider()

 # Period filter in sidebar
period = st.selectbox(
        "Select period",
        ['1st', '2nd', '3rd', '4th', "OT"]
    )

    # Filter dataframe
if period != "All":
        df_filtered = df[df["period"] == period]
else:
    df_filtered = df
##
## Event graphs
##

with st.expander('Events'):

    df_counts = df_filtered.groupby(['event', 'team']).size().reset_index(name='count')

    df_counts['count'] = pd.to_numeric(df_counts['count'], errors='coerce')

    # Asegurarte de que 'event' y 'team' sean strings
    df_counts['event'] = df_counts['event'].astype(str)

    # Matplotlib + Streamlit
    fig1 = px.bar(
        df_counts,
        x = 'event',
        y = 'count',
        color = 'team',
        barmode = 'group',
        title="Events by Team",
        labels={"count": "Number of Events",
                "event": "Event Type",
                "team": "Team"}
    )

    fig1.update_layout(height=700)

    ## Event success graphs 

    df_counts = df_filtered.groupby(['event', 'team', 'outcome']).size().reset_index(name='count')

    # Filtrado 6v5 y proporciones
    df_6v5 = df_filtered[df_filtered['event'] == '6v5'].groupby(['team', 'outcome']).size().reset_index(name='count')
    df_6v5['proportion'] = df_6v5.groupby('team')['count'].transform(lambda x: x / x.sum())

    # Goals por team y subevent

    goals_scored = df_counts[(df_counts['outcome'] == 'Goal')].groupby(['team', 'event']).size().reset_index(name='goals_scored')

    exclusions_drawn = df_counts[(df_counts['outcome'] == 'Exclusion')].groupby(['team', 'event']).size().reset_index(name='exclusions_drawn')

    # Intentos por team y subevent (excluyendo 'Exclusion')
    attempts_made = (df_counts.groupby(['team', 'event'])['count'].sum().reset_index(name='attempts_made'))

    # Exclusion success rate por team
    exclusion_success_rate = df_6v5[df_6v5['outcome'] == 'Goal'][['team', 'proportion']]

    df_all = (goals_scored
            .merge(exclusions_drawn, on=['team', 'event'], how='outer')
            .merge(attempts_made, on=['team','event'], how='outer')
                .merge(exclusion_success_rate, on=['team'], how='outer')
    )

    df_all.fillna(0, inplace=True)

    df_all['success_rate'] = ((df_all['goals_scored'] + (df_all['exclusions_drawn'] * df_all['proportion'])) / df_all['attempts_made']) * 100 


    fig2 = px.bar(
        df_all,
        x = 'event',
        y = 'success_rate',
        color = 'team',
        barmode = 'group',
        title="Success Rate by Team",
        labels={"success_rate": "Success Rate (%)",
                "event": "Event Type",
                "team": "Team"}
    )

    fig2.update_layout(height=700)

    df_all.columns = ['Team', 'Event', 'Goals Scored', 'Exclusions Drawn', 'Attempts Made', 'Goal Proportion', 'Success Rate']

    st.dataframe(df_all)

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.plotly_chart(fig2, use_container_width=True)

##
## Subevent graphs
##

with st.expander('Subevents'):

    df_subcounts = df_filtered.groupby(['subevent', 'team']).size().reset_index(name='count')


    df_subcounts['count'] = pd.to_numeric(df_subcounts['count'], errors='coerce')

    # Asegurarte de que 'event' y 'team' sean strings
    df_subcounts['subevent'] = df_subcounts['subevent'].astype(str)



    # Matplotlib + Streamlit
    fig1 = px.bar(
        df_subcounts,
        x = 'subevent',
        y = 'count',
        color = 'team',
        barmode = 'group',
        title="Event Counts by Team",
        labels={"count": "Number of Events",
                "subevent": "Subevent Type",
                "team": "Team"}
    )


    # Conteo y proporciones generales
    df_counts = df_filtered.groupby(['event', 'subevent', 'team', 'outcome']).size().reset_index(name='count')


    # Filtrado 6v5 y proporciones
    df_6v5 = df_filtered[df_filtered['event'] == '6v5'].groupby(['team', 'outcome']).size().reset_index(name='count')
    df_6v5['proportion'] = df_6v5.groupby('team')['count'].transform(lambda x: x / x.sum())


    # Goals por team y subevent

    goals_scored = df_counts[(df_counts['outcome'] == 'Goal')].groupby(['team', 'subevent']).size().reset_index(name='goals_scored')

    exclusions_drawn = df_counts[(df_counts['outcome'] == 'Exclusion')].groupby(['team', 'subevent']).size().reset_index(name='exclusions_drawn')

    # Intentos por team y subevent (excluyendo 'Exclusion')
    attempts_made = (df_counts.groupby(['team', 'subevent'])['count'].sum().reset_index(name='attempts_made'))

    # Exclusion success rate por team
    exclusion_success_rate = df_6v5[df_6v5['outcome'] == 'Goal'][['team', 'proportion']]

    df_all = (goals_scored
            .merge(exclusions_drawn, on=['team', 'subevent'], how='outer')
            .merge(attempts_made, on=['team','subevent'], how='outer')
                .merge(exclusion_success_rate, on=['team'], how='outer')
    )

    df_all.fillna(0, inplace=True)

    df_all['success_rate'] = ((df_all['goals_scored'] + (df_all['exclusions_drawn'] * df_all['proportion'])) / df_all['attempts_made']) * 100 


    fig2 = px.bar(
        df_all,
        x = 'subevent',
        y = 'success_rate',
        color = 'team',
        barmode = 'group',
        title="Success Rate by Team",
        labels={"success_rate": "Success Rate (%)",
                    "subevent": "Subevent Type",
                    "team": "Team"}
    )

    df_all.columns = ['Team', 'Subevent', 'Goals Scored', 'Exclusions Drawn', 'Attempts Made', 'Goal Proportion', 'Success Rate']

    st.dataframe(df_all)

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.plotly_chart(fig2, use_container_width=True)

##
## Save graphs - Save number and percentage
##
with st.expander('Saves'):
    df_saves = df_filtered[(df_filtered['outcome'] == 'Save')].groupby(['team', 'event', 'subevent', 'player_affected']).size().reset_index(name='count')

    df_saves['team_player'] = df_saves['team'] + ' - ' + df_saves['player_affected']

    fig1 = px.bar(
        df_saves,
        x = 'subevent',
        y = 'count',
        color = 'team_player',
        barmode = 'group',
        title="Saves by Team and Subevent",
        labels={"count": "Number of Saves",
                "subevent": "Subevent Type",
                "team": "Team"}
    )


    shots_taken = df_filtered[(df_filtered['outcome'] == 'Save') | (df_filtered['outcome'] == 'Miss') | (df_filtered['outcome'] == 'Goal')].groupby(['team', 'event', 'subevent', 'player_affected']).size().reset_index(name='count')

    df_all = (df_saves            
              .merge(shots_taken, on=['team', 'event', 'subevent', 'player_affected'], how='outer', suffixes=('_saves', '_shots'))
    )

    df_all['save_success_rate'] = (df_all['count_saves'] / df_all['count_shots']) * 100

    
    fig2 = px.bar(
        df_all,
        x = 'subevent',
        y = 'save_success_rate',
        color = 'team_player',
        barmode = 'group',
        title="Saves by Team and Subevent",
        labels={"save_success_rate": "Save Percentage (%)",
                "subevent": "Subevent Type",
                "team": "Team"}
    )

    df_all.columns = ['Team', 'Event', 'Subevent', 'Player Affected', 'Saves', 'Team + Player', 'Attempts Made', 'Save Success Rate']
    st.dataframe(df_all)

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.plotly_chart(fig2, use_container_width=True)

##
## Shot type pie chart
##

with st.expander('Shot Types'):

    df_shots = df_filtered[(df_filtered['shot_type'] == 'Skip Shot') | (df_filtered['shot_type'] == 'Lob Shot') | (df_filtered['shot_type'] == 'Normal Shot')].groupby(['team', 'shot_type']).size().reset_index(name='count')


    df_shotshome = df_shots[(df_shots['team'] == 'Home')]
    df_shotsaway = df_shots[(df_shots['team'] == 'Away')]

    df_shotshome.columns = ['Team', 'Shot Type', 'Count']
    df_shotsaway.columns = ['Team', 'Shot Type', 'Count']

    st.dataframe(df_shotshome)
    st.dataframe(df_shotsaway)

    fig1 = px.pie(
        df_shotshome,
        values='Count',
        names='Shot Type',
        title='Home Shot Types'
    )

    fig2 = px.pie(
        df_shotsaway,
        values='Count',
        names='Shot Type',
        title='Away Shot Types'
    )   

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.plotly_chart(fig2, use_container_width=True)


    df_shots = df_filtered[(df_filtered['shot_type'] == 'Skip Shot') | (df_filtered['shot_type'] == 'Lob Shot') | (df_filtered['shot_type'] == 'Normal Shot')].groupby(['team', 'shot_type', 'outcome']).size().reset_index(name='count')

    df_goals = df_shots[df_shots['outcome'] == 'Goal'].groupby(['team', 'shot_type']).size().reset_index(name='count')


    df_shotshome = df_goals[(df_goals['team'] == 'Home')]
    df_shotsaway = df_goals[(df_goals['team'] == 'Away')]

    

    fig1 = px.pie(
        df_shotshome,
        values='count',
        names='shot_type',
        title='Home Shot Percentages'
    )

    fig2 = px.pie(
        df_shotsaway,
        values='count',
        names='shot_type',
        title='Away Shot Percentages'
    )   

    col1, col2 = st.columns(2)

    df_shotshome.columns = ['Team', 'Shot Type', 'Goal Count']
    df_shotsaway.columns = ['Team', 'Shot Type', 'Goal Count']

    st.dataframe(df_shotshome)
    st.dataframe(df_shotsaway)

    with col1:
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.plotly_chart(fig2, use_container_width=True)

##
## Player stats and rankings
##


##
## Blocks/Turnover/Exclusions
##
with st.expander('Blocks/Turnovers/Exclusions'):

    df_bte = df_filtered[df_filtered['outcome'].isin(['Block', 'Turnover', 'Exclusion'])]

    df_bte_counts = df_bte.groupby(['team', 'event', 'subevent']).size().reset_index(name='count')

    st.dataframe(df_bte_counts)


##
## Goals across time
##

##
## Heatmap
##

##
## Goal/Save/Miss map 
##

##
## Momentum chart 
##

##
## Passmap chart 
## 

st.dataframe(df_filtered)

if "my_data" in st.session_state and st.button("Clear data"):
    del st.session_state.my_data
    st.experimental_rerun()

