from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import requests
import pandas as pd
import os
import nfl_data_py as nfl
import warnings
warnings.filterwarnings("ignore")

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load data
players = nfl.import_players()
players = players[(players['status'] == 'ACT') & players['position'].isin(['QB', 'RB', 'WR', 'TE'])]
players['name/team/pos'] = players['display_name'] + ' ' + players['team_abbr'] + ' ' + players['position']

seasonal_data = nfl.import_seasonal_data([2018, 2019, 2020, 2021, 2022, 2023], 'REG')
seasonal_data['fumbles_lost'] = seasonal_data['sack_fumbles_lost'] + seasonal_data['rushing_fumbles_lost'] + seasonal_data['receiving_fumbles_lost']
seasonal_data.rename(columns={'season':'Season','passing_yards':'Passing Yds','passing_tds':'Passing TDs','interceptions':'INTs','rushing_yards':'Rushing Yds','rushing_tds':'Rushing TDs','fumbles_lost':'Fumbles','receiving_yards':'Receiving Yds','receiving_tds':'Receiving TDs','receptions':'Receptions'},inplace=True)

# Projections data from FantasyPros
url_fp_qb = "https://www.fantasypros.com/nfl/projections/qb.php?week=draft"
fp_qb = pd.read_html(url_fp_qb, header=1)[0]
fp_qb['Site']='FantasyPros'

url_fp_wr = "https://www.fantasypros.com/nfl/projections/wr.php?week=draft"
fp_wr = pd.read_html(url_fp_wr, header=1)[0]
fp_wr['Site']='FantasyPros'

url_fp_rb = "https://www.fantasypros.com/nfl/projections/rb.php?week=draft"
fp_rb = pd.read_html(url_fp_rb, header=1)[0]
fp_rb['Site']='FantasyPros'

url_fp_te = "https://www.fantasypros.com/nfl/projections/te.php?week=draft"
fp_te = pd.read_html(url_fp_te, header=1)[0]
fp_te['Site']='FantasyPros'

# Empty Dataframes for app layout
df = pd.DataFrame(columns=['Season', 'Passing Yds', 'Passing TDs', 'INTs', 'Rushing Yds', 'Rushing TDs', 'Fumbles', 'Receiving Yds', 'Receiving TDs', 'Receptions'])
#projected_df = pd.DataFrame(columns=['REC'])

# App layout
app.layout = html.Div([
    html.H1(children='Fantasy Football Scoring App', style={'textAlign': 'center'}),
    html.H2(children='Enter your custom scoring settings below.', style={'textAlign': 'left', 'marginBottom': '20px'}),
    dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardHeader(html.Div('Passing', style={'textAlign': 'left', "text-decoration": "underline"})),
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(html.Div("Passing TD pts", style={'white-space': 'nowrap'}), width=6),
                                            dbc.Col(dcc.Input(id="pass_tds", type="number", placeholder=0, style={'width': '100%'}), width=2)
                                        ],
                                        className="mb-4"  # Adjusted margin-bottom
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(html.Div("Passing YDs (per 1 yard)", style={'white-space': 'nowrap'}), width=6),
                                            dbc.Col(dcc.Input(id="pass_yds", type="number", placeholder=0, style={'width': '100%'}), width=2)
                                        ],
                                        className="mb-4"  # Adjusted margin-bottom
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(html.Div("Interceptions", style={'white-space': 'nowrap'}), width=6),
                                            dbc.Col(dcc.Input(id="ints", type="number", placeholder=0, style={'width': '100%'}), width=2)
                                        ],
                                        className="mb-4"  # Adjusted margin-bottom
                                    ),
                                ]
                            ),
                        ]
                    ),
                ],
            ),
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardHeader(html.Div('Rushing', style={'textAlign': 'left', "text-decoration": "underline"})),
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(html.Div("Rushing TD pts", style={'white-space': 'nowrap'}), width=6),
                                            dbc.Col(dcc.Input(id="rush_tds", type="number", placeholder=0, style={'width': '100%'}), width=2)
                                        ],
                                        className="mb-4"  # Adjusted margin-bottom
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(html.Div("Rushing YDs (per 1 yard)", style={'white-space': 'nowrap'}), width=6),
                                            dbc.Col(dcc.Input(id="rush_yds", type="number", placeholder=0, style={'width': '100%'}), width=2)
                                        ],
                                        className="mb-4"  # Adjusted margin-bottom
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(html.Div("Fumbles Lost", style={'white-space': 'nowrap'}), width=6),
                                            dbc.Col(dcc.Input(id="fumbles", type="number", placeholder=0, style={'width': '100%'}), width=2)
                                        ],
                                        className="mb-4"  # Adjusted margin-bottom
                                    ),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardHeader(html.Div('Receiving', style={'textAlign': 'left', "text-decoration": "underline"})),
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(html.Div("Receiving TD pts", style={'white-space': 'nowrap'}), width=6),
                                            dbc.Col(dcc.Input(id="rec_tds", type="number", placeholder=0, style={'width': '100%'}), width=2)
                                        ],
                                        className="mb-4"  # Adjusted margin-bottom
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(html.Div("Receiving YDs (per 1 yard)", style={'white-space': 'nowrap'}), width=6),
                                            dbc.Col(dcc.Input(id="rec_yds", type="number", placeholder=0, style={'width': '100%'}), width=2)
                                        ],
                                        className="mb-4"  # Adjusted margin-bottom
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(html.Div("Receptions (ppr)", style={'white-space': 'nowrap'}), width=6),
                                            dbc.Col(dcc.Input(id="recs", type="number", placeholder=0, style={'width': '100%'}), width=2)
                                        ],
                                        className="mb-4"  # Adjusted margin-bottom
                                    ),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
        ]
    ),
    html.H2('Enter a player\'s name below', style={'marginTop': '20px', 'marginBottom': '10px'}),  # Adjusted margin-top and margin-bottom
    dcc.Dropdown(
        id='player-dropdown', 
        options=[{'label': name, 'value': name} for name in players['name/team/pos']], 
        multi=False, 
        placeholder='Select a player',
        style={'width': '50%'}  # Adjusted width
    ),
    html.Button('Search', id='search_button', n_clicks=0),
    html.Div(id='player_name_out'),
    html.Div(id='result-container', children=[
        dbc.Container([
            dbc.Row([
                dbc.Col(html.Div(id='image-container', style={'textAlign': 'center'}), width=4),
                dbc.Col(
                    html.Div([
                        html.H3("Season Stats", style={'textAlign': 'center'}),
                        dash_table.DataTable(
                            id='classic_stats',
                            style_table={'overflowX': 'auto'},
                            style_cell={'textAlign': 'left'}
                        ),
                        html.H3("Projected Stats - 2024", style={'textAlign': 'center', 'marginTop': '20px'}),
                        dash_table.DataTable(
                            id='projected_stats',
                            style_table={'overflowX': 'auto'},
                            style_cell={'textAlign': 'left'}
                        )
                    ]),
                    width=8
                )
            ])
        ], fluid=True)
    ], style={'display': 'none'})
], style={'padding': '20px'})

# Callback to update player name output, display image, and update stats tables
@app.callback(
    [Output('classic_stats', 'data'),
     Output('projected_stats', 'data'),
     Output('player_name_out', 'children'),
     Output('image-container', 'children'),
     Output('result-container', 'style')],
    [Input('search_button', 'n_clicks')],
    [State('player-dropdown', 'value')]
)
def update_output(n_clicks, player_name):
    if n_clicks == 0:
        return [], [], "", html.Div(), {'display': 'none'}  # Return empty data, empty name, and hide result container if button hasn't been clicked
    if not player_name:
        return [], [], "No Player Selected", html.Div(), {'display': 'none'}  # Return empty data, empty name, and hide result container if no player name
    else:
        player_gsis_id = players[players['name/team/pos'] == player_name]['gsis_id'].unique()[0]
        df = seasonal_data[seasonal_data['player_id'] == player_gsis_id]
        image_url = players[players['name/team/pos'] == player_name]['headshot'].unique()[0]
        
        # Get projected stats
        player_name_split = player_name.split(' ')
        player_name_only = player_name_split[0] + ' ' + player_name_split[1]
        team = player_name_split[2]
        projected_df = pd.DataFrame()
        position = players[players['name/team/pos'] == player_name]['position'].unique()[0]
        if position == 'QB':
            projected_df = fp_qb[(fp_qb['Player'].str.contains(player_name_only)) & (fp_qb['Player'].str.contains(team))]
            projected_df.columns = fp_qb.columns
        elif position == 'WR':
            projected_df = fp_wr[(fp_wr['Player'].str.contains(player_name_only)) & (fp_wr['Player'].str.contains(team))]
            projected_df.drop(columns=['Player','FPTS','ATT'],inplace=True)
            projected_df.rename(columns={'REC':'Receptions','YDS':'Receiving Yds','TDS':'Receiving TDs','YDS.1':'Rushing Yds','TDS.1':'Rushing TDs','FL':'Fumbles'},inplace=True)
            projected_df=projected_df[['Site','Receiving Yds','Receptions','Receiving TDs','Rushing Yds','Rushing TDs','Fumbles']]
            #projected_df.columns = fp_wr.columns.drop(column='Player')
        elif position == 'RB':
            projected_df = fp_rb[(fp_rb['Player'].str.contains(player_name_only)) & (fp_rb['Player'].str.contains(team))]
            projected_df.columns = fp_rb.columns
        elif position == 'TE':
            projected_df = fp_te[(fp_te['Player'].str.contains(player_name_only)) & (fp_te['Player'].str.contains(team))]
            projected_df.columns = fp_te.columns
                
        
        
        # Format data for dash_table.DataTable
        classic_stats_data = df[['Season', 'Passing Yds', 'Passing TDs', 'INTs', 'Rushing Yds', 'Rushing TDs', 'Fumbles', 'Receiving Yds', 'Receptions']].to_dict('records')
        projected_stats_data = projected_df.to_dict('records')
        
        return classic_stats_data, projected_stats_data, f"Player Selected: {player_name}", html.Img(src=image_url, style={'width': '100%', 'height': 'auto'}), {'display': 'block'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run_server(host='0.0.0.0', port=port)
