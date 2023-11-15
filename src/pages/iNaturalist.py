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

dash.register_page(__name__,
                   path='/biodiversity',  # represents the url text
                   name='Biodiversity',  # name of page, commonly used as name of link
                   title='ParKli Biodiversity'  # epresents the title of browser's tab
)

##########################################################################################################################################

# Funktion zum Herunterladen von iNaturalist-Daten in einem bestimmten geografischen Bereich

def download_inaturalist_data(min_lat, max_lat, min_lon, max_lon):
     
    # Definieren Sie den geografischen Bereich
    swlat = min_lat  # Südliche Breite
    swlng = min_lon  # Westliche Länge
    nelat = max_lat  # Nördliche Breite
    nelng = max_lon  # Östliche Länge


    # Setzen Sie die Anfangsseite auf 1
    page = 1

    # Initialisieren Sie eine leere Liste zum Speichern der Beobachtungsdaten
    all_observations = []

    while True:
        # Setzen Sie die API-Endpunkt-URL mit den entsprechenden Parametern
        url = f'https://api.inaturalist.org/v1/observations?swlat={swlat}&swlng={swlng}&nelat={nelat}&nelng={nelng}&page={page}&per_page=200'

        # Machen Sie eine GET-Anfrage an die iNaturalist API
        response = requests.get(url)

        # Extrahieren Sie die Beobachtungsdaten aus der API-Antwort (JSON-Format)
        data = response.json()

        # Überprüfen Sie, ob Beobachtungsdaten vorhanden sind
        if 'results' in data:
            # Fügen Sie die Beobachtungsdaten zur Liste hinzu
            all_observations.extend(data['results'])
            
            # Überprüfen Sie, ob die Anzahl der Beobachtungen kleiner als die maximale Seite ist
            if len(data['results']) < data['per_page']:
                break  # Beenden Sie die Schleife, wenn alle Beobachtungen abgerufen wurden

            # Inkrementieren Sie die Seite für die nächste Anfrage
            page += 1
        else:
            break  # Beenden Sie die Schleife, wenn keine Beobachtungen vorhanden sind
    # Ausgabe der Gesamtanzahl der heruntergeladenen Beobachtungen
    observation_count = len(all_observations)
    print(f'Anzahl der heruntergeladenen Beobachtungen: {observation_count}')
    
    df = pd.json_normalize(all_observations)
    df[['lat', 'lon']] = df['location'].str.split(',', expand=True)

    # Datentypen der neuen Spalten korrigieren
    df['lat'] = df['lat'].astype(float)
    df['lon'] = df['lon'].astype(float)
    df.head()
    print(len(df))
    return df 
#########################################################################################################################################
#Lesen der Invasive Arten aus Excel Datei
def excel_invasive_species():
    
    #current_directory = os.getcwd()
    #path = os.path.join(current_directory, 'urlTest/src/assets/')
    # Navigiert eine Ebene nach oben und dann in den Ordner 'assets'
    relative_path = os.path.join('..', 'assets', '2023_02_14__IAS_Liste_BW_Kurzfassung_Internet_LUBW.xlsx')
    
    # Vollständiger Pfad zur Datei, ausgehend vom aktuellen Skriptverzeichnis
    file_path = os.path.join(os.path.dirname(__file__), relative_path)
    
    try:
        dfInvasiveArten = pd.read_excel(file_path, skiprows=1)
    except FileNotFoundError:
        print(f"Datei nicht gefunden: {file_path}")
    #dfInvasiveArten  = pd.read_excel(file_path, skiprows=1)
    return dfInvasiveArten

#######################################################################################################################################
def restorPage_boxSelect(filtered_df, df):
    
      #fig = px.box(filtered_df, x='month', y=['fu_processed', 'fu_value'], points='all')
            species_counts = filtered_df.groupby('taxon.preferred_common_name').size().reset_index(name='observation_count')
            print(species_counts)
            print(len(species_counts))
            fig = px.bar(species_counts, y='observation_count', x='taxon.preferred_common_name', text='observation_count')
            fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
            #return dcc.Graph(figure=fig)
            #return fig
            
            dfInvasiveSpecies = excel_invasive_species()
            
            merged_dfInvasiveSpecies = pd.merge(filtered_df['taxon.name'], dfInvasiveSpecies['Wissenschaftlicher Name'], left_on='taxon.name', right_on='Wissenschaftlicher Name')
            print(merged_dfInvasiveSpecies.head(30))
            
            # Gruppieren und Anzahl der Beobachtungen pro invasive Spezies berechnen
            merged_dfInvasiveSpeciesCount = merged_dfInvasiveSpecies.groupby('taxon.name').size().reset_index(name='Count Invasive Species')
            
            
            figSpecies = px.scatter_mapbox(
                filtered_df, 
                lat="lat", 
                lon="lon",
                hover_name="taxon.preferred_common_name",
                hover_data=["taxon.preferred_common_name", "time_observed_at", "place_guess", 'quality_grade'],
                color="taxon.preferred_common_name",
                color_continuous_scale= px.colors.cyclical.IceFire, 
                zoom=10, height=400
            )
            #figSpecies.update_layout(mapbox_style="stamen-terrain")
            figSpecies.update_layout(mapbox_style=" open-street-map")
            figSpecies.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            
        
            return html.Div([
        
                # dbc.Row([
                #     dbc.Col([
                #         html.Br(),
                #         html.H3('Auswertung der Beobachtungen für den markierten Bereich', style={'textAlign': 'center'}),
                #     ], width={"size": 12})
                # ]),  
                
                html.Br(),
                html.Br(),
                
                dbc.Row([
                    
                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H3("Übersicht über die Beobachtungen", className="card-title text-center text-nowrap"),
                                        html.Br(),
                                        html.P("Anzahl der Beobachtungen Gesamt:", className="card-subtitle"),
                                        html.P(len(df)),
                                        html.P("Anzahl der Beobachtungen im ausgewählten Bereich:", className="card-subtitle"),
                                        html.P(len(filtered_df)),
                                        html.P("Anzahl der unterschiedlichen Arten im ausgewählten Bereich:", className="card-subtitle"),
                                        html.P(len(species_counts)),
                                        html.P("Anzahl der Beobachtungen von invasiven Arten im ausgewählten Bereich:", className="card-subtitle"),
                                        html.P(len(merged_dfInvasiveSpecies)),
                                        html.P("Anzahl der unterschiedlichen invasiven Arten im ausgewählten Bereich:", className="card-subtitle"),
                                        html.P(len(merged_dfInvasiveSpecies['taxon.name'].unique())), 
                                            
                                    ]
                                        
                                ),
                                className="m-4 shadow bg-light rounded",
                            ),                     
                        #], width={"size": 4}
                    #),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H3("Übersicht invasive Arten", className="card-title text-center text-nowrap"),
                                        html.Br(),
                                        dash_table.DataTable(
                                            merged_dfInvasiveSpeciesCount.to_dict('records'),
                                            [{'name': i, 'id': i} for i in merged_dfInvasiveSpeciesCount.columns],
                                            #page_size=10,
                                            filter_action="native",
                                            sort_action="native",
                                            sort_mode="single",
                                            column_selectable="single",
                                            fixed_rows={'headers': True},
                                            style_table={'margin': '5px', 'height': '200px'},
                                            style_cell={'textAlign': 'left', 'padding': '1px', 'minWidth': 30, 'maxWidth': 50, 'width': 50}
                                        ),
                                        
                                    ]
                                    
                                ),
                                className="m-4 shadow bg-light rounded",
                            ),                     
                        ]#, 
                        #width={"size": 4}
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H3("Übersicht Arten", className="card-title text-center text-nowrap"),
                                        dcc.Graph(figure = figSpecies),
                                        html.Br(),
                                        
                                    ]
                                    
                                ),
                                className="m-4 shadow bg-light rounded",
                            ),                     
                        ]#, width={"size":5}
                    ),
                ]),
                
                html.Br(),
                html.Br(),
                
                dbc.Row([
                    dbc.Col([
    
                        dcc.Graph(figure = fig),
                        html.Br(),
                    ], width={"size": 12})
                ]),  
                
                #html.H5(filename),
                #html.H6(datetime.datetime.fromtimestamp(date)),
                

                html.Hr(),
                html.Br(),
                
                dbc.Row([
                    dbc.Col([
                        dash_table.DataTable(
                            species_counts.to_dict('records'),
                            [{'name': i, 'id': i} for i in species_counts.columns],
                            #page_size=10,
                            filter_action="native",
                            sort_action="native",
                            sort_mode="single",
                            column_selectable="single",
                            fixed_rows={'headers': True},
                            style_table={'margin': '10px', 'height': '350px'},
                            style_cell={'textAlign': 'left', 'padding': '1px', 'minWidth': 30, 'maxWidth': 50, 'width': 50}
                        ),
                    ], width=12)
                ]),  
            ])
##############################################################################################################################################
def restorPage_map(df):
    
    fig = px.scatter_mapbox(df, 
            lat="lat", 
            lon="lon",
            hover_name="taxon.preferred_common_name",
            hover_data=["id","taxon.preferred_common_name", "time_observed_at", "place_guess", 'quality_grade'],
            color_discrete_sequence=["black"],
            zoom=10, height=400
        )
    #fig.update_layout(mapbox_style="stamen-terrain")
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    
    return fig
##########################################################################################################################################

card_Location = dbc.Card(
    dbc.CardBody(
        [
            html.H2([html.I(className="bi bi-geo-alt me-2"), "Untersuchungsort"], className="text-nowrap text-center pe-2"),
            #dbc.FormText("Geben Sie den Namen der Stadt ein", className="text-nowrap", style={'width': '300px'}),
            #dbc.Input(id='city-input',persistence=True, placeholder="Geben Sie ein Namen einer Stadt ein...", type="text", style={'width': '300px'}),
            dbc.FormText("Geben Sie den Namen einer Stadt ein", className="text-nowrap w-auto col-md-6"),
            dbc.Input(id='city-input',persistence=True, placeholder="Stadt...", type="text", className="form-control col-md-6", style={'width': '200px'}),
            
            #dbc.FormText("Legen Sie den Suchradius in ° schrittweite 0.01 fest",className="text-nowrap", style={'width': '300px'}),
            #dbc.Input(id='latLon-input',placeholder='0.05', type="number", min=0, max=1, step=0.01, value='0.05', style={'width': '300px'}),
            dbc.FormText("Legen Sie den Suchradius in ° schrittweite 0.01 fest",className="text-nowrap w-auto col-md-6"),
            dbc.Input(id='latLon-input',placeholder='0.02', type="number", min=0, max=1, step=0.01, value='0.02', className="form-control col-md-6", style={'width': '200px'}),
            html.Br(),
            #html.Button('Daten herunterladen', id='download-button', n_clicks=0),
            dbc.Button("Daten herunterladen", id="download-button", n_clicks=0, outline=True, color="secondary", className="me-2 text-nowrap"),
            #dbc.Button("Load Session", id="loadSession-button", n_clicks=0, outline=True, color="secondary", className="me-2 text-nowrap"),
            html.Br(),
        ],
        className="border-start border-success border-5",
       
    ),
    className="m-2 shadow bg-white rounded ",
)

card_UpdateMap = dbc.Card(
    dbc.CardBody(
        [
            html.H1([html.I(className="bi bi-map me-2"), "Auswahl Daten"], className="text-nowrap text-center"),
            html.Br(),
            #html.Div(id='map'),
            dcc.Graph(id='map', figure={}),
        ],
        className="border-start border-success border-5",
       
    ),
    className="m-2 shadow bg-white rounded",
)




    
################################################################################################################################################
def layout(data = dcc.Store(id='memory-output'), selectedDataState= dcc.Store(id='selectedData-State')):
    
    print(data)
    print(type(data))
    
    if data and selectedDataState:
    
        return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                        [
                            html.H1("ParKli Biodiversität", style={'textAlign': 'center', 'color': '#2F5F53'}),
                        ], width=12
                    )
                ]),
                
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                card_Location,
                                
                            ], width={"size": 2, "offset":0}
                        ),
                        dbc.Col(
                            [
                               card_UpdateMap,
                                
                            ], width={"size": 10, "offset":0}
                        )
                
                    
                    ]
                ),
              
                html.Br(),
                html.Br(),
                html.Br(), 
                
                dbc.Row(
                    [
                        dbc.Col(
                            [   
                                #html.Div(id='map'),
                                dcc.Graph(id='map', figure={}),
                            ], width=12
                        )
                    ]
                ),
                
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(id='box-select'),
                            ], width=12
                        )
                    ]
                ),  
        
            ]
        )
    else:
        return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        
                                        html.Br(), 
                                        html.Br(), 
                                        html.Br(), 
                                        html.Img(src="./assets/ParKli_Biodiv_300px.png", height="50", style={'display': 'inline-block'}),
                                        html.H1("ParKli Biodiversität",style={'textAlign': 'center', 'color': '#2F5F53','display': 'inline-block', 'margin-left': 'auto', 'margin-right': 'auto' }),
                                        
                                    ],
                                    className="position-absolute top-0 start-50"
                                    
                                )
                            ], width=12
                        )
                        
                    ]
                ),
                html.Br(), 
                html.Br(), 
                
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                card_Location,
                               
                            ], 
                            #width={"size": 2}
                            xs=5, sm=5, md=5, lg=4, xl=3, xxl=3
                        ),
                        dbc.Col(
                            [
                                card_UpdateMap,
                               
                            ], 
                            #width={"size": 10}
                            xs=7, sm=7, md=7, lg=9, xl=9, xxl=9
                        ),
                    ]
                ),
        
                html.Br(),
                html.Br(), 
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(id='box-select'),
                            ], width=12
                        )
                    ]
                ),  
        
            ]
        )

##################################################################################################################################################

# Callback-Funktion für das Herunterladen der iNaturalist-Daten und Aktualisierung der Scattermapbox
@callback(
    #Output('map', 'figure', allow_duplicate=True),
    Output('map', 'figure'),
    Output('memory-output', 'data'),
    Input('download-button', 'n_clicks'),
    State('city-input', 'value'),
    State('latLon-input', 'value'),
    State('memory-output', 'data'),
    prevent_initial_call=True
)
def update_map(n_clicks, city, latLonCorrection, data):
    
    print(data)
    print(type(data))
    
    if n_clicks > 0 and city:
        # Längen- und Breitengrade der Stadt finden
        geolocator = Nominatim(user_agent='my_app')
        location = geolocator.geocode(city, language='de')
        
        if location is None:
            return fig
        
        lat = location.latitude
        lon = location.longitude
        
        print(type(latLonCorrection))
        
        latLonCorrection = float(latLonCorrection) 
        
        # Bereich für iNaturalist-Daten berechnen (z.B. 0.1 Grad um den ausgewählten Punkt)
        min_lat = lat - latLonCorrection
        max_lat = lat + latLonCorrection
        min_lon = lon - latLonCorrection
        max_lon = lon + latLonCorrection
        
        # iNaturalist-Daten herunterladen
        obersvation = download_inaturalist_data(min_lat, max_lat, min_lon, max_lon)
        
        data=obersvation.to_dict('records')
        
        fig = px.scatter_mapbox(obersvation, 
            lat="lat", 
            lon="lon",
            hover_name="taxon.preferred_common_name",
            hover_data=["id","taxon.preferred_common_name", "time_observed_at", "place_guess", 'quality_grade'],
            color_discrete_sequence=["black"],
            zoom=10, height=300
        )
        #fig.update_layout(mapbox_style="stamen-terrain")
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
         
        #return html.Div([ dcc.Graph(figure = fig)]), data     
        return fig, data
        #return fig
    elif data:
        print('Test')
    
    return dash.no_update
#########################################################################################################################################
# Callback-Funktion für den Box Select
@callback(
    #Output('box-select', 'children', allow_duplicate=True),
    #Output('selectedData-State', 'selectedDataState', allow_duplicate=True),
    Output('box-select', 'children'),
    Output('selectedData-State', 'selectedDataState'),
    Input('map', 'selectedData'),
    State ('memory-output', 'data'),
    State ('selectedData-State', 'selectedDataState'),
    prevent_initial_call=True
)
def update_box_select(selectedData, data, selectedDataState):
    if not selectedData:
        # Wenn keine Daten ausgewählt wurden, zeige einen leeren Plot
        return dash.no_update
    else:
        
        try:
            # Extrahiere die ausgewählten Daten
            print(selectedData)
            print(type(selectedData))
            
            
            
            points = selectedData['points']
            selected_df = pd.DataFrame(points)
            print(selected_df.head())
            selected_df.info()
            #print(selected_df['hovertext'])
            listHovertext= selected_df['customdata'].values.tolist()
            print(type(listHovertext))
            print(listHovertext)
            
            #extraction der id aus Liste
            new_list = [list[0] for list in listHovertext]
            
            print(new_list)
            df = pd.DataFrame(data)
            print(df)
            df.info()
            
            #Filtern der ausgewählten ID aus Dataframe
            boolean_series = df.id.isin(new_list)
            filtered_df = df[boolean_series]
            print(filtered_df)
            print(len(filtered_df))
            selectedDataState=filtered_df.to_dict()
                    
            #fig = px.box(filtered_df, x='month', y=['fu_processed', 'fu_value'], points='all')
            species_counts = filtered_df.groupby('taxon.preferred_common_name').size().reset_index(name='observation_count')
            print(species_counts)
            print(len(species_counts))
            fig = px.bar(species_counts, y='observation_count', x='taxon.preferred_common_name', text='observation_count')
            fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
            #return dcc.Graph(figure=fig)
            #return fig
            
            dfInvasiveSpecies = excel_invasive_species()
            
            merged_dfInvasiveSpecies = pd.merge(filtered_df['taxon.name'], dfInvasiveSpecies['Wissenschaftlicher Name'], left_on='taxon.name', right_on='Wissenschaftlicher Name')
            print(merged_dfInvasiveSpecies.head(30))
            
            # Gruppieren und Anzahl der Beobachtungen pro invasive Spezies berechnen
            merged_dfInvasiveSpeciesCount = merged_dfInvasiveSpecies.groupby('taxon.name').size().reset_index(name='Count Invasive Species')
            
            
            figSpecies = px.scatter_mapbox(
                filtered_df, 
                lat="lat", 
                lon="lon",
                hover_name="taxon.preferred_common_name",
                hover_data=["taxon.preferred_common_name", "time_observed_at", "place_guess", 'quality_grade'],
                color="taxon.preferred_common_name",
                color_continuous_scale= px.colors.cyclical.IceFire, 
                zoom=10, height=400
            )
            #figSpecies.update_layout(mapbox_style="stamen-terrain")
            figSpecies.update_layout(mapbox_style="open-street-map")
            figSpecies.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            
        
            return html.Div([
                
              
                # dbc.Row([
                #     dbc.Col([
                #         html.Br(),
                #         html.H3('Auswertung der Beobachtungen für den markierten Bereich', style={'textAlign': 'center'}),
                #     ], width={"size": 12})
                # ]),  
                
                html.Br(),
                html.Br(),
                
                dbc.Row(
                    [
                    
                        dbc.Col(
                            [
                                dbc.Row([
                                    
                                    dbc.Col(
                                        [
                                            dbc.Card(
                                                dbc.CardBody(
                                                    [

                                                        html.P(children=["Beobachtungen Gesamt"], className="card-subtitle h5 text-center"),
                                                        html.Br(),
                                                        html.P(children=[len(df)], className="card-subtitle text-n h5 text-center"),
                                                    ],
                                                    className="border-start border-success border-5",
                                                ),
                                                className="m-2 shadow bg-white rounded h-100 class",
                                            )
                                        ],
                                        width={"size": 6},
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Card(
                                                dbc.CardBody(
                                                    [
                                                        #html.P(children=["Anzahl der Beobachtungen im ausgewählten Bereich: ",len(filtered_df)], className="card-subtitle text-nowrap h6 text-center"),
                                                        html.P(children=["Ausgewählter Bereich"], className="card-subtitle h5 text-center"),
                                                        html.Br(),
                                                        html.P(children=[len(filtered_df)], className="card-subtitle  h5 text-center"),
                                                    ],
                                                    className="border-start border-success border-5",
                                                ),
                                                className="m-2 shadow bg-white rounded h-100 class",
                                            )
                                        ],
                                        width={"size": 6},
                                    ),
                                    
                                    ]),
                                html.Br(),
                                
                                dbc.Row([
                                    
                                    dbc.Col(
                                            [
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.P(children=["Unterschiedliche Arten"],className="card-subtitle h5 text-center"),
                                                            html.Br(),
                                                            html.P(children=[len(species_counts)],className="card-subtitle h5 text-center"),
                                                        ],
                                                        className="border-start border-success border-5",
                                                    ),
                                                    className="m-2 shadow bg-white rounded h-100 class",
                                                )
                                            ],
                                            width={"size": 6},
                                        ),
                                    dbc.Col(
                                        [
                                            dbc.Card(
                                                dbc.CardBody(
                                                    [
                                                        #html.P(children=["Beobachtungen von invasiven Arten im ausgewählten Bereich: ",len(merged_dfInvasiveSpecies)], className="card-subtitle text-nowrap h6 text-center"),
                                                        html.P(children=["Invasive Arten"], className="card-subtitle h5 text-center"),
                                                        html.Br(),
                                                        html.P(children=[len(merged_dfInvasiveSpecies)], className="card-subtitle h5 text-center"),
                                                    ],
                                                    className="border-start border-success border-5",
                                                ),
                                                className="m-2 shadow bg-white rounded h-100 class",
                                            )
                                        ],
                                        width={"size": 6},
                                    ),
                                    
                                    
                                ]),
                                html.Br(),
                                dbc.Row(
                                    [
                                    
                                    dbc.Col(
                                            [
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.P(children=["Unterschiedliche invasive Arten"], className="card-subtitle h5 text-center"),
                                                            html.Br(),
                                                            html.P(children=[len(merged_dfInvasiveSpecies['taxon.name'].unique())], className="card-subtitle h5 text-center"),
                                                        ],
                                                        className="border-start border-success border-5",
                                                    ),
                                                    className="m-2 shadow bg-white rounded h-100 class",
                                                )
                                            ],
                                            width={"size": 12},
                                        ),
                                    ],
                                ),
                                    
                         
                            
                            # dbc.Row([
                                
                            #     dbc.Card(
                            #         dbc.CardBody(
                            #             [
                            #                html.P(children=["Anzahl der unterschiedlichen Arten im ausgewählten Bereich: ", len(species_counts)],className="card-subtitle text-nowrap h5 text-center"),
                            #             ],
                            #             className="border-start border-success border-5 text-nowrap",
                            #         ),
                            #         className="m-4 shadow bg-white rounded h-100 class",
                            #     )
                            # ]),
                            #  dbc.Row([
                                
                            #     dbc.Card(
                            #         dbc.CardBody(
                            #             [
                            #                html.P(children=["Anzahl der Beobachtungen von invasiven Arten im ausgewählten Bereich: ",len(merged_dfInvasiveSpecies)], className="card-subtitle text-nowrap h5 text-center"),
                            #             ],
                            #             className="border-start border-success border-5 text-nowrap",
                            #         ),
                            #         className="m-4 shadow bg-white rounded h-100 class",
                            #     )
                            # ]),
                            #    dbc.Row([
                                
                            #     dbc.Card(
                            #         dbc.CardBody(
                            #             [
                            #                html.P(children=["Anzahl der unterschiedlichen invasiven Arten im ausgewählten Bereich: ", len(merged_dfInvasiveSpecies['taxon.name'].unique())], className="card-subtitle text-nowrap h5 text-center"),
                            #             ],
                            #             className="border-start border-success border-5 text-nowrap",
                            #         ),
                            #         className="m-4 shadow bg-white rounded h-100 class",
                            #     ),
                            # ]),
        
                        
                            # dbc.Card(
                            #     dbc.CardBody(
                            #         [
                            #             html.H5("Übersicht über die Beobachtungen", className="card-title text-center text-nowrap"),
                            #             html.Br(),
                            #             html.Br(),
                            #             html.Br(),
                            #             #html.H3("Anzahl der Beobachtungen Gesamt:", className="card-subtitle text-nowrap"),
                            #             html.P(children=["Anzahl der Beobachtungen Gesamt: ", len(df)], className="card-subtitle text-nowrap"),
                            #             html.Br(),
                            #             html.Br(),
                            #             html.P(children=["Anzahl der Beobachtungen im ausgewählten Bereich: ",len(filtered_df)], className="card-subtitle"),
                            #             html.Br(),
                            #             html.Br(),
                            #             #html.P(len(filtered_df)),
                            #             html.P(children=["Anzahl der unterschiedlichen Arten im ausgewählten Bereich: ", len(species_counts)],className="card-subtitle"),
                            #             html.Br(),
                            #             html.Br(),
                            #             #html.P(len(species_counts)),
                            #             html.P(children=["Anzahl der Beobachtungen von invasiven Arten im ausgewählten Bereich: ",len(merged_dfInvasiveSpecies)], className="card-subtitle"),
                            #             #html.P(len(merged_dfInvasiveSpecies)),
                            #             html.Br(),
                            #             html.Br(),
                            #             html.P(children=["Anzahl der unterschiedlichen invasiven Arten im ausgewählten Bereich: ", len(merged_dfInvasiveSpecies['taxon.name'].unique())], className="card-subtitle"),
                            #             #html.P(len(merged_dfInvasiveSpecies['taxon.name'].unique())), 
                                            
                            #         ],
                            #         className="border-start border-success border-5 text-nowrap h6 text-justify",
                                        
                            #     ),
                            #     className="m-2 shadow bg-white rounded h-100 class",
                            # ),
                                        
                            ], 
                            width={"size": 4},
                            className = "h-100 class",
                        
                    ),
                    
                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H5("Übersicht invasive Arten", className="card-title text-center text-nowrap"),
                                        html.Br(),
                                        dash_table.DataTable(
                                            merged_dfInvasiveSpeciesCount.to_dict('records'),
                                            [{'name': i, 'id': i} for i in merged_dfInvasiveSpeciesCount.columns],
                                            #page_size=10,
                                            filter_action="native",
                                            sort_action="native",
                                            sort_mode="single",
                                            column_selectable="single",
                                            fixed_rows={'headers': True},
                                            style_table={'margin': '5px', 'height': '200px'},
                                            style_cell={'textAlign': 'left', 'padding': '1px', 'minWidth': 30, 'maxWidth': 50, 'width': 50}
                                        ),
                                        
                                    ],
                                     className="border-start border-success border-5",
                                    
                                ),
                                className="m-3 shadow bg-white rounded h-100 class",
                            ),                     
                        ], width={"size": 4}
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H5("Übersicht Arten", className="card-title text-center text-nowrap"),
                                        dcc.Graph(figure = figSpecies),
                                        #html.Br(),
                                        
                                    ],
                                     className="border-start border-success border-5",
                                    
                                ),
                                className="m-3 shadow bg-white rounded h-100 class",
                            ),                     
                        ], 
                        width={"size":4}
                    ),
                ]),
                
                html.Br(),
                html.Br(),
                
                dbc.Row([
                    dbc.Col([
    
                        dcc.Graph(figure = fig),
                        html.Br(),
                    ], width={"size": 12})
                ]),  
                
                #html.H5(filename),
                #html.H6(datetime.datetime.fromtimestamp(date)),
                

                html.Hr(),
                html.Br(),
                
                dbc.Row([
                    dbc.Col([
                        dash_table.DataTable(
                            species_counts.to_dict('records'),
                            [{'name': i, 'id': i} for i in species_counts.columns],
                            #page_size=10,
                            filter_action="native",
                            sort_action="native",
                            sort_mode="single",
                            column_selectable="single",
                            fixed_rows={'headers': True},
                            style_table={'margin': '10px', 'height': '350px'},
                            style_cell={'textAlign': 'left', 'padding': '1px', 'minWidth': 30, 'maxWidth': 50, 'width': 50}
                        ),
                    ], width=12)
                ]),  
            ]), selectedDataState
        except Exception as e:
            print(e)
            
# # # # Callback-Funktion für das Aktualisieren der Seite
# @callback(
#     Output('map', 'figure'),
#     Output('box-select', 'children'),
#     Input('loadSession-button', 'n_clicks'),
#     State('city-input', 'value'),
#     State('memory-output', 'data'),
#     State('selectedData-State', 'selectedDataState') 
# )
# def restorePage(n_clicks,city, data, selectedDataState):
    
#     print(data)
#     print(type(data))
    
#     if data and city and selectedDataState:
#          # Extrahiere die ausgewählten Daten
#         print(selectedDataState)
#         print(type(selectedDataState))
            
                      
#         #points = selectedDataState['points']
#         filtered_df = pd.DataFrame(selectedDataState)
#         # print(selected_df.head())
#         # selected_df.info()
#         # listHovertext= selected_df['customdata'].values.tolist()
#         # #extraction der id aus Liste
#         # new_list = [list[0] for list in listHovertext]
            
#         df = pd.DataFrame(data)
               
#         #Filtern der ausgewählten ID aus Dataframe
#         # boolean_series = df.id.isin(new_list)
#         # filtered_df = df[boolean_series]
        
#         fig = restorPage_map(df)
        
#         boxSelect = restorPage_boxSelect(filtered_df, df)        
        
        
        
#         return fig, boxSelect
        
        

#     return dash.no_update