from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import requests
from io import BytesIO
from PIL import Image
import pandas as pd
import os

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load data
players = pd.read_csv('roster_2024.csv')
players['name/team/pos'] = players['full_name'] + ' ' + players['team'] + ' ' + players['position']

df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

# Function to retrieve image URL from website based on player name
def get_image_url(player_name):
    image_url = players[players['name/team/pos'] == player_name]['headshot_url'].unique()[0]

    # Send a GET request to fetch the raw image data
    response = requests.get(image_url)
            
    # Check if the request was successful (status code 200)
    
    if response.status_code == 200:
        # Return player name and image as HTML elements
        return [None, html.Img(src=image_url, style={'width': '100%', 'height': 'auto', 'maxWidth': '325px', 'maxHeight': '232px'})]
    else:
        return f"Failed to retrieve the image for {player_name}. Status code: {response.status_code}", html.Div()


# App layout
app.layout = html.Div([
    html.H1(children='Fantasy Football Scoring App', style={'textAlign': 'center'}),
    html.H2(children='Enter your custom scoring settings below.', style={'textAlign': 'left'}),
    html.Div('Passing',style={'textAlign': 'left',"text-decoration": "underline"}),
dbc.Row(
    [
        dbc.Col(
            [
                html.Div("Passing TDs", style={'marginRight': '10px', 'display': 'inline-block', 'width': '120px'}),
                dcc.Input(id="pass_tds", type="text", placeholder="", style={'width': '100px', 'display': 'inline-block'})
            ],
            width=4,
            className="p-0"  # Adjust horizontal padding to reduce space between columns
        ),
        dbc.Col(
            [
                html.Div("Passing YDs", style={'marginRight': '10px', 'display': 'inline-block', 'width': '120px'}),
                dcc.Input(id="pass_yds", type="text", placeholder="", style={'width': '100px', 'display': 'inline-block'})
            ],
            width=4,
            className="p-0"  # Adjust horizontal padding to reduce space between columns
        ),
        dbc.Col(
            [
                html.Div("Interceptions", style={'marginRight': '10px', 'display': 'inline-block', 'width': '120px'}),
                dcc.Input(id="ints", type="text", placeholder="", style={'width': '100px', 'display': 'inline-block'})
            ],
            width=4,
            className="p-0"  # Adjust horizontal padding to reduce space between columns
        ),
    ],
),




    # dbc.Container([
    # html.H3(children='Passing', style={'textAlign': 'left',"text-decoration": "underline"}),
    # dbc.Stack(
    #     [
    #         html.Div("Pass TDs"),
    #         dcc.Input(id="Pass Tds", type="text", placeholder="",style={'width':20}),
    #         html.Div("Pass YDs"),
    #         dcc.Input(id="Pass YDs", type="text", placeholder="",style={'width':20})


    #     ],
    #     direction="horizontal", gap=1),
    # ], style={'textAlign': 'left'}),

    # dbc.Container([
    # html.H3(children='Rushing', style={'textAlign': 'left',"text-decoration": "underline"}),
    # dbc.Stack(
    #     [
    #         html.Div("Rushing TDs"),
    #         dcc.Input(id="Rushing Tds", type="text", placeholder="",style={'width':20}),
    #         html.Div("Rushing YDs"),
    #         dcc.Input(id="Rushing YDs", type="text", placeholder="",style={'width':20})


    #     ],
    #     direction="horizontal", gap=1),
    # ], style={'textAlign': 'left'}),
            
    html.H2('Enter a player\'s name below'),
    dcc.Dropdown(
        id='player-dropdown', 
        options=[{'label': name, 'value': name} for name in players['name/team/pos']], 
        multi=False, 
        placeholder='Select a player'
    ),
    html.Button('Search', id='search_button', n_clicks=0),
    html.Div(id='player_name_out'),
    dbc.Container([
        dbc.Row([
            dbc.Col(html.Div(id='image-container', style={'textAlign': 'center'}), width=4),
            dbc.Col(
                dash_table.DataTable(
                    df.to_dict('records'),
                    [{"name": i, "id": i} for i in df.columns],
                    id='tbl',
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left'}
                ),
                width=8
            )
        ])
    ], fluid=True)
], style={'padding': '20px'})

# Callback to update player name output and display image
@app.callback(
    [Output('player_name_out', 'children'),
     Output('image-container', 'children')],
    [Input('search_button', 'n_clicks')],
    [State('player-dropdown', 'value')]
)
def update_output(n_clicks, player_name):
    if n_clicks == 0:
        return "", html.Div()  # Return empty div for image container if button hasn't been clicked
    if not player_name:
        return "No Player Selected", html.Div()  # Return empty div for image container if no player name
    else:
        image_url=players[players['name/team/pos']==player_name]['headshot_url'].unique()[0]
        if image_url is not None:
             # Send a GET request to fetch the raw image data
            response = requests.get(image_url)
            
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Extract the raw image content
                image_content = response.content
                
                # Use PIL to open the image from the bytes
                image = Image.open(BytesIO(image_content))
                
                # Return player name and image as HTML elements
                return f"You entered: {player_name}", html.Img(src=image_url, style={'width': '325px', 'height': '232px'})
            
            else:
                return f"Failed to retrieve the image for {player_name}. Status code: {response.status_code}", html.Div()
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run_server(host='0.0.0.0', port=port)
