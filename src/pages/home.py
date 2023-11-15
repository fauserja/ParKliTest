import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table, callback


import pandas as pd

import numpy as np
import statistics 
import requests
import os
from geopy.distance import geodesic
from PIL import Image
import sys

import dash_bootstrap_components as dbc
from datetime import datetime
import plotly.express as px
import plotly.graph_objs as go

import requests
from geopy.distance import geodesic
import json
from pandas import json_normalize
from geopy.geocoders import Nominatim
import pyproj


# To create meta tag for each page, define the title, image, and description.
dash.register_page(__name__,
                   path='/',  # '/' is home page and it represents the url
                   name='Home',  # name of page, commonly used as name of link
                   title='Index',  # title that appears on browser's tab
                   #image='pg1.png',  # image in the assets folder
                   description='ParKli Overview'
)


# page 1 data
df = px.data.gapminder()



url = f"https://api.inaturalist.org/v1/observations?project_id=parkli"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    #data["total_results"]
else:
    print("Fehler bei der Anfrage:", response.status_code)
    






card_iNaturalist = dbc.Card(
  
      #dbc.CardHeader("Anzahl Beobachtungen iNaturalist ParKli"),
      dbc.CardBody(
        [
            html.H1([html.I(className="bi bi-search"), "Beobachtungen iNaturalist ParKli"], className="text-nowrap"),
            html.H3(data["total_results"]),
          
        ], className="border-start border-success border-5"
    ),
    className="text-center m-4 shadow bg-light rounded",
  
)


card_GreenSpaceHack = dbc.Card(
    dbc.CardBody(
        [
            html.H1([html.I(className="bi bi-question-square"), "Anzahl Fragebögen Greenspace Hack"], className="text-nowrap"),
            html.H3("100"),
        ], className="border-start border-danger border-5"
    ),
    className="text-center m-4 shadow bg-light rounded",
)


card_EyeOnWater = dbc.Card(
    dbc.CardBody(
        [
            html.H1([html.I(className="bi bi-water"), "Anzahl Beobachtungen EyeOnWater"], className="text-nowrap"),
            html.H3("100"),
    
        ], className="border-start border-secondary border-5"
    ),
    className="text-center m-4 shadow bg-white rounded",
)



layout = html.Div(
    [
      
      dbc.Row(
        [
          dbc.Col(card_iNaturalist), 
          dbc.Col(card_GreenSpaceHack), 
          dbc.Col(card_EyeOnWater),
        ],
        #fluid=True,
      ),
    
      
    html.Br(),
      
      dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(options=df.continent.unique(),
                                     id='cont-choice', persistence=True)
                    ], xs=10, sm=10, md=8, lg=4, xl=4, xxl=4
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(id='line-fig',
                                  figure=px.histogram(df, x='continent',
                                                      y='lifeExp',
                                                      histfunc='avg'))
                    ], width=12
                )
            ]
        )
    ]
)


@callback(
    Output('line-fig', 'figure'),
    Input('cont-choice', 'value')
)
def update_graph(value):
    if value is None:
        fig = px.histogram(df, x='continent', y='lifeExp', histfunc='avg')
    else:
        dff = df[df.continent==value]
        fig = px.histogram(dff, x='country', y='lifeExp', histfunc='avg')
    return fig