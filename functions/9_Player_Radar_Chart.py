

# Adjusting dataframe to keep only the player name and surname
columns_to_keep = ['player.name', 'player.surname']
df_new = df_detalles[columns_to_keep]

# Create a dataframe with full names as individual values 
df_new = df_new.copy()
df_new['full_name'] = df_new['player.name'] + ' ' + df_new['player.surname']

# Remove duplicates based on 'playerId' and keep the first occurrence only
df_unique = df_new.drop_duplicates(subset='full_name', keep='first')


# Function to calculate percentile rank of each player according to given statistics
def percentile_rank_general(data, column, name, conditions=None):
   
    # Drop NaNs in the target column to prevent nulls affecting calculation
    df_filtered = data.dropna(subset=[column])

    # Apply filtering conditions if provided
    if conditions:
        for cond_col, cond_val in conditions.items():
            df_filtered = df_filtered[df_filtered[cond_col] == cond_val]

    # Check if the player exists in the column
    if name not in df_filtered[column].values:
        return None

    # Get value counts for the column - outputs player names and number of times they appear in the column
    value_counts = df_filtered[column].value_counts()

    # Ensure the player has a value in value_counts 
    if name not in value_counts:
        return None

    # Output number of times the player appears in the column
    player_value = value_counts[name]
    
    # Calculate percentile rank
    percentile = stats.percentileofscore(value_counts.values, player_value, kind='rank')

    return float(percentile), int(player_value)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define a function to calculate the percentile rank for a player for different variables
def get_player_stats(player_name):

    radar_data = {
        'Exclusions': percentile_rank_general(df, 'exclusion_drawn_by', player_name) or (0,0),
        'Assists': percentile_rank_general(df, 'shot_assisted_by', player_name) or (0,0),
        'Shots': percentile_rank_general(df, 'shot_taken_by', player_name) or (0,0),
        'Exclusions Committed': percentile_rank_general(df, 'exclusion_committed_by', player_name) or (0,0),
        'Shots Blocked': percentile_rank_general(df, 'shot_blocked_by', player_name) or (0,0),
        'Turnover committed': percentile_rank_general(df, 'turned_over_by_x', player_name) or (0,0),
        'Turnover won': percentile_rank_general(df, 'turnover_won_by', player_name) or (0,0),
        'Fast Break Goals': percentile_rank_general(
            df, 'shot_taken_by', player_name, conditions={'shot.isGoal': True, 'shot.isFastBreak': True}
        ) or (0,0),
        'Direct From Foul': percentile_rank_general(
            df, 'shot_taken_by', player_name, conditions={'shot.isGoal': True, 'shot.isDirectFromFoul': True}
        )or (0,0),
        'Goals': percentile_rank_general(
            df, 'shot_taken_by', player_name, conditions={'shot.isGoal': True}
        ) or (0,0),
        'Penalty Goals': percentile_rank_general(
            df, 'shot_taken_by', player_name, conditions={'shot.isGoal': True, 'shot.type': 'Penalty'}
        ) or (0,0),
        'Powerplay Goals': percentile_rank_general(
            df, 'shot_taken_by', player_name, conditions={'shot.isGoal': True, 'shot.type': 'Power_Play'}
        ) or (0,0),
        'Regular Attack': percentile_rank_general(
            df, 'shot_taken_by', player_name, conditions={'shot.isGoal': True, 'shot.type': 'Regular_Attack'}
        ) or (0,0),
        'Offensive Foul': percentile_rank_general(
            df, 'turned_over_by_x', player_name, conditions={'turnover.type': 'Offensive_Foul'}
        ) or (0,0),
        'Lost Ball': percentile_rank_general(
            df, 'turned_over_by_x', player_name, conditions={'turnover.type': 'Lost_Ball' or 'Ball_Under'}
        ) or (0,0),
    }
    
    return radar_data
# Assign player names to a variable to call them alphabetically
player_names = sorted(df_unique['full_name'].unique())

# Define the layout of the app
app.layout = html.Div([
    html.H1("Radar Chart for Champions League Players - Season 2024/25"),
    
    # Dropdown for player selection - ordered alphabetically and with multi-select
    html.Div([
            dcc.Dropdown(
                id='player-dropdown',
                options=[{'label': name, 'value': name} for name in player_names],
                value=player_names[:2],  # Default value: first 2 alphabetically
                multi=True
                )
    ]), 

    # Dropdown for selecting radar chart categories
    html.Div([
        dcc.Dropdown(
            id='categories-dropdown',
            options=[
                {'label': 'Exclusions', 'value': 'Exclusions'},
                {'label': 'Assists', 'value': 'Assists'},
                {'label': 'Shots', 'value': 'Shots'},
                {'label': 'Exclusions Committed', 'value': 'Exclusions Committed'},
                {'label': 'Shots Blocked', 'value': 'Shots Blocked'},
                {'label': 'Turnover committed', 'value': 'Turnover committed'},
                {'label': 'Turnover won', 'value': 'Turnover won'},
                {'label': 'Fast Break Goals', 'value': 'Fast Break Goals'},
                {'label': 'Direct From Foul', 'value': 'Direct From Foul'},
                {'label': 'Goals', 'value': 'Goals'},
                {'label': 'Penalty Goals', 'value': 'Penalty Goals'},
                {'label': 'Powerplay Goals', 'value': 'Powerplay Goals'},
                {'label': 'Regular Attack', 'value': 'Regular Attack'},
                {'label': 'Offensive Foul', 'value': 'Offensive Foul'},
                {'label': 'Lost Ball', 'value': 'Lost Ball'}
            ],
            value=['Exclusions', 'Assists', 'Shots'],  # Default selected values
            multi=True
        )
    ]),

    # Display radar chart
    dcc.Graph(id='radar-chart'),

    html.Div(id='div-message')
])

# Define the callback to update the radar chart
@app.callback(
    [Output('radar-chart', 'figure'),
    Output('radar-chart', 'style'),
    Output('div-message', 'children')],
    [Input('player-dropdown', 'value'),
     Input('categories-dropdown', 'value')]
)


# Update the radar chart based on selected players and categories
def update_radar_chart_comparision(player_names, selected_categories):
    # Check if player names and selected categories are provided
    if not player_names or not selected_categories:
        return go.Figure(), {'display': 'none'}, html.H3("Please select a player and categories to display the radar chart...")
    
    player_stats_complete = []

    for player_name in player_names:
        try:
            jugador_stats = get_player_stats(player_name)
            if jugador_stats is None:   
                return go.Figure(), {'display': 'none'}, html.H3(f"Player {player_name} does not exist in the dataset. Please select another player.")
        except (KeyError, TypeError):
            return go.Figure(), {'display': 'none'}, html.H3(f"KeyError or TypeError when fetching stats for: {player_name}")

        try:
            player_stats = [jugador_stats.get(category) for category in selected_categories]
            if None in player_stats:                
                return go.Figure(), {'display': 'none'}, html.H3(f"{selected_categories} do not have values for {player_name}. Please select another category.")
        except KeyError:
            return go.Figure(), {'display': 'none'}, html.H3(f"KeyError when fetching stats for: {player_name}")
    
        player_stats_complete.append(player_stats)


    # Prepare data for the radar chart
    N = len(selected_categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)] # Create angles for each category
    angles += angles[:1]  # To close the radar loop

    fig = go.Figure()

    zipped = list(zip(player_names, player_stats_complete))  # Combine player names and stats
    for player in zipped:
        player_name = player[0]
        stats = player[1]

        r_values = [stat[0] for stat in stats] + [stats[0][0]]  # Close the loop
        customdata_values = [stat[1] for stat in stats] + [stats[0][1]]

        fig.add_trace(go.Scatterpolar(
            r=r_values,
            customdata=customdata_values,
            theta=selected_categories + [selected_categories[0]],
            fill='toself',
            name=player_name,
            hovertemplate=
                '<b>%{theta}</b><br>' +
                'Percentile Rank: %{r}<br>' +
                'Raw Score: %{customdata}<extra></extra>'
    ))



    #Add 'and' before the last player name in the title   
    def format_names(names):
        if len(names) == 0:
            return ""
        elif len(names) == 1:
            return names[0]
        else:
            return ', '.join(names[:-1]) + ' and ' + names[-1]

    # Update the layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(
                    (max((stat[0] for stat in player_values), default=0) for player_values in player_stats_complete),
                    default=0
                ) + 5]
  # Adjust range dynamically
            )
        ),
        showlegend=True,
        legend=dict(
            x=0.2,
            y=0.5,
            xanchor='left',
            yanchor='middle',
            orientation='v'
        ),
        title=f"Radar Chart for {format_names(player_names)}"
    )

    return fig, {'display': 'block'}, html.H3(f"Radar chart for {format_names(player_names)} with the following categories: {format_names(selected_categories)}")



# Run the app
if __name__ == '__main__':
    app.run(debug=True)



