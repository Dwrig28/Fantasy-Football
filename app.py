from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import requests
import pandas as pd
import os
import nfl_data_py as nfl


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load data
players = nfl.import_players()
players = players[(players['status']=='ACT') & players['position'].isin(['QB','RB','WR','TE'])]
players['name/team/pos'] = players['display_name'] + ' ' + players['team_abbr'] + ' ' + players['position']

df=pd.DataFrame(columns=['season','passing_yards', 'rushing_yards', 'receiving_yards', 'passing_tds', 'rushing_tds', 'receiving_tds','interceptions','fumbles_lost'])

seasonal_data=nfl.import_seasonal_data([2018,2019,2020,2021,2022,2023],'REG')
seasonal_data['fumbles_lost']=seasonal_data['sack_fumbles_lost'] + seasonal_data['rushing_fumbles_lost'] +seasonal_data['receiving_fumbles_lost']

# App layout
app.layout = html.Div([
    html.H1(children='Fantasy Football Scoring App', style={'textAlign': 'center'}),
    html.H2(children='Enter your custom scoring settings below.', style={'textAlign': 'left'}),
    dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Row(html.Div('Passing', style={'textAlign': 'left', "text-decoration": "underline"})),
                    dbc.Row(
                        [
                            dbc.Col(html.Div("Passing TD pts", style={'white-space': 'nowrap'}), width=6),
                            dbc.Col(dcc.Input(id="pass_tds", type="number", placeholder=0, style={'width': '100%'}), width=2)
                        ],
                        className="mb-3"
                    ),
                    dbc.Row(
                        [
                            dbc.Col(html.Div("Passing YDs (per 1 yard)", style={'white-space': 'nowrap'}), width=6),
                            dbc.Col(dcc.Input(id="pass_yds", type="number", placeholder=0, style={'width': '100%'}), width=2)
                        ],
                        className="mb-3"
                    ),
                    dbc.Row(
                        [
                            dbc.Col(html.Div("Interceptions", style={'white-space': 'nowrap'}), width=6),
                            dbc.Col(dcc.Input(id="ints", type="number", placeholder=0, style={'width': '100%'}), width=2)
                        ],
                        className="mb-3"
                    ),
                ],
            ),
            dbc.Col(
                [
                    dbc.Row(html.Div('Rushing', style={'textAlign': 'left', "text-decoration": "underline"})),
                    dbc.Row(
                        [
                            dbc.Col(html.Div("Rushing TD pts", style={'white-space': 'nowrap'}), width=6),
                            dbc.Col(dcc.Input(id="rush_tds", type="number", placeholder=0, style={'width': '100%'}), width=2)
                        ],
                        className="mb-3"
                    ),
                    dbc.Row(
                        [
                            dbc.Col(html.Div("Rushing YDs (per 1 yard)", style={'white-space': 'nowrap'}), width=6),
                            dbc.Col(dcc.Input(id="rush_yds", type="number", placeholder=0, style={'width': '100%'}), width=2)
                        ],
                        className="mb-3"
                    ),
                    dbc.Row(
                        [
                            dbc.Col(html.Div("Fumbles Lost", style={'white-space': 'nowrap'}), width=6),
                            dbc.Col(dcc.Input(id="fumbles", type="number", placeholder=0, style={'width': '100%'}), width=2)
                        ],
                        className="mb-3"
                    ),
                ]
            ),
            dbc.Col(
                [
                    dbc.Row(html.Div('Receiving', style={'textAlign': 'left', "text-decoration": "underline"})),
                    dbc.Row(
                        [
                            dbc.Col(html.Div("Receiving TD pts", style={'white-space': 'nowrap'}), width=6),
                            dbc.Col(dcc.Input(id="rec_tds", type="number", placeholder=0, style={'width': '100%'}), width=2)
                        ],
                        className="mb-3"
                    ),
                    dbc.Row(
                        [
                            dbc.Col(html.Div("Receiving YDs (per 1 yard)", style={'white-space': 'nowrap'}), width=6),
                            dbc.Col(dcc.Input(id="rec_yds", type="number", placeholder=0, style={'width': '100%'}), width=2)
                        ],
                        className="mb-3"
                    ),
                    dbc.Row(
                        [
                            dbc.Col(html.Div("Receptions (ppr)", style={'white-space': 'nowrap'}), width=6),
                            dbc.Col(dcc.Input(id="recs", type="number", placeholder=0, style={'width': '100%'}), width=2)
                        ],
                        className="mb-3"
                    ),
                ]
            ),
        ]
    ),
    html.H2('Enter a player\'s name below'),
    dcc.Dropdown(
        id='player-dropdown', 
        options=[{'label': name, 'value': name} for name in players['name/team/pos']], 
        multi=False, 
        placeholder='Select a player'
    ),
    html.Button('Search', id='search_button', n_clicks=0),
    html.Div(id='player_name_out'),
    html.Div(id='result-container', children=[
        dbc.Container([
            dbc.Row([
                dbc.Col(html.Div(id='image-container', style={'textAlign': 'center'}), width=4),
                dbc.Col(
                    dash_table.DataTable(
                        df.to_dict('records'),
                        [{"name": i, "id": i} for i in df.columns],
                        id='classic_stats',
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left'}
                    ),
                    width=8
                )
            ])
        ], fluid=True)
    ], style={'display': 'none'})
], style={'padding': '20px'})

# Callback to update player name output and display image
@app.callback(
    [Output('classic_stats', 'data'),
     Output('player_name_out', 'children'),
     Output('image-container', 'children'),
     Output('result-container', 'style')],
    [Input('search_button', 'n_clicks')],
    [State('player-dropdown', 'value')]
)
def update_output(n_clicks, player_name):
    if n_clicks == 0:
        return [], "", html.Div(), {'display': 'none'}  # Return empty data, empty name, and hide result container if button hasn't been clicked
    if not player_name:
        return [], "No Player Selected", html.Div(), {'display': 'none'}  # Return empty data, empty name, and hide result container if no player name
    else:
        player_gsis_id = players[players['name/team/pos'] == player_name]['gsis_id'].unique()[0]
        df = seasonal_data[seasonal_data['player_id'] == player_gsis_id]
        image_url = players[players['name/team/pos'] == player_name]['headshot'].unique()[0]
        if image_url:
            response = requests.get(image_url)
            if response.status_code == 200:
                return df.to_dict('records'), f"You entered: {player_name}", html.Img(src=image_url, style={'width': '325px', 'height': '232px'}), {'display': 'block'}
            else:
                return df.to_dict('records'), f"Failed to retrieve the image for {player_name}. Status code: {response.status_code}", html.Div(), {'display': 'block'}
        else:
            return df.to_dict('records'), f"{player_name} does not have a headshot.", html.Div(), {'display': 'block'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run_server(host='0.0.0.0', port=port)
