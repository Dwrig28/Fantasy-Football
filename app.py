from dash import Dash, dcc, html, Input, Output, State
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import pandas as pd

app = Dash(__name__)

players=pd.read_csv('roster_2024.csv')
players['name/team/pos']=players['full_name'] +' ' + players['team'] + ' ' + players['position']

# Function to retrieve image URL from website based on player name
def get_image_url(player_name):
    # Example URL where player images are stored
    # base_url = "https://www.nfl.com/players/"
    # url = base_url + player_name.lower().replace(" ", "-")
    
    # # Fetch HTML data from the URL
    # response = requests.get(url)
    # htmldata = response.text
    
    # # Parse HTML using BeautifulSoup
    # soup = BeautifulSoup(htmldata, 'html.parser')
    
    # # Find the meta tag with property="og:image" to get image URL
    # image_url = soup.find("meta", property="og:image")['content']
    image_url=players[players['name/team/pos']==player_name]['headshot_url'].unique()[0]
    
    return image_url

# App layout
app.layout = html.Div([
    html.H1(children='Fantasy Football Scoring App', style={'textAlign': 'center'}),
    html.H2('Enter a player\'s name below'),
    dcc.Dropdown(id='player-dropdown', options=players['name/team/pos'], multi=False, placeholder='Select a player'),

    html.Button('Search', id='search_button', n_clicks=0),

    html.Div(id='player_name_out'),
    html.Div(id='image-container')  # Container for displaying the image dynamically
])

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
        try:
            # Get the image URL based on player name
            image_url = get_image_url(player_name)
            
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
        
        except Exception as e:
            return f"An error occurred: {str(e)}", html.Div()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run_server(host='0.0.0.0', port=port)
