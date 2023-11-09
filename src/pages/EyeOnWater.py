import base64
import datetime
from datetime import date

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
from lib.find_water_colour import find_water_colour

import csv

import dash_bootstrap_components as dbc
from datetime import datetime
import plotly.express as px
import plotly.graph_objs as go
import sys
import json




dash.register_page(__name__,
                   path='/Water',  # represents the url text
                   name='Water',  # name of page, commonly used as name of link
                   title='ParKli Water'  # epresents the title of browser's tab
)
    

##################################################################################################################

def parse_contentCSV(contents, filename_csv):
    
    
    
    content_type, content_string = contents.split(',')
    


    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename_csv:
            # Assume that the user uploaded a CSV file
            # df = pd.read_csv(
            #     io.StringIO(decoded.decode('utf-8')))
            #df = pd.read_csv(
             #    io.StringIO(decoded.decode('unicode_escape')))
            df = pd.read_csv(filename_csv, sep=',' , encoding = 'unicode_escape', skipinitialspace=True, skiprows=1)
            #df = pd.read_csv(filename_csv, sep=',', skiprows=1)
            
          
            print(len(df))
            
            
            df.to_csv("new_file.csv")
            df = pd.read_csv("new_file.csv", sep=',')
            
            # first check whether file exists or not
            # calling remove method to delete the csv file
            # in remove method you need to pass file name and type
            file = 'new_file.csv'
            if(os.path.exists(file) and os.path.isfile(file)):
                os.remove(file)
                print("file deleted")
            else:
                print("file not found")
            #df=df.rename(columns={'Unnamed': 'id'}, inplace=True)
            print(df.head())
           
            return df
        else:
            return dash.no_update
    
    except Exception as e:
        print(e)

#########################################################################################################################################
def delete_all_files_in_folder(folder_path):
    """
    Löscht alle Dateien in einem gegebenen Verzeichnis.
    """
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}. Reason: {e}")


############################################################################################################################################
# Funktion zum Herunterladen des Bildes
def download_image(url, save_folder):
    # Check if the image already exists in the folder
    filename = os.path.join(save_folder, os.path.basename(url))
    if os.path.exists(filename):
        return filename

    # If not, download and save the image
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename
    else:
        return None


#########################################################################################################################################
def cleanData(df):
    
  
    try:
        
         
            
            #Abstand zwischen beobachteten und berechneter Wert, wenn dieser zu groß löschen aus dem Dataframe
            dfStreuung = df.loc[(abs(df['fu_value'] - df['fu_processed']) < 2.0)]
            print(len(dfStreuung))

            df = dfStreuung.copy()
            df = df.dropna(subset=['p_cloud_cover'])        
            print(len(dfStreuung))
            
            #path = "../../assets/Bilder"
            # Aktueller Ordner (/src/pages)
            current_directory = os.getcwd()
            print(current_directory)
            
            # Pfad zum Zielordner (/src/assets/Bilder)
            path = os.path.join(current_directory, 'urlTest/src/assets', 'Bilder')
            
            print(path)
            
            save_folder_CSV = os.path.join(current_directory, 'urlTest/src/assets', 'CSVPictureDate')
            
            # Ordner zum Speichern der Bilder
            
            #save_folder_CSV = './CSVPictureDate'
            # Create the save folder if it doesn't exist
            if not os.path.exists(save_folder_CSV):
                os.makedirs(save_folder_CSV)
            # Create the save folder if it doesn't exist
            if not os.path.exists(path):
                os.makedirs(path)
                
            # Überprüfen, ob bereits eine CSV-Datei existiert
            csv_path = os.path.join(save_folder_CSV, 'data.csv')
            if os.path.exists(csv_path):
                # Lade das DataFrame aus der CSV-Datei
                df_existing = pd.read_csv(csv_path)
                dfnew_entries = df[~df['image'].isin(df_existing['image'])]
                #df_updated = pd.concat([df_existing, new_entries], ignore_index=True)
                #df_updated.to_csv('data.csv', index=False)  
            else:
                dfnew_entries = df.copy()
            
            
            if not dfnew_entries.empty:
                dfnew_entries['image_path'] = dfnew_entries['image'].apply(lambda url: download_image(url, path))

                dfnew_entries["total_pixels"] = 0
                dfnew_entries["color_pixels"] = 0

                # # # Schleife über alle Dateien im Ordner
                for filename in os.listdir(path):
                    
                    if filename.endswith(".png"):
                    # Bild öffnen
                        img = Image.open(os.path.join(path, filename))
                        # Gesamtanzahl der Pixel
                        total_pixels = img.width * img.height

                        # Anzahl der Farbpixel
                        color_pixels = len(set(img.getdata()))
                        
                            
                        row = dfnew_entries.loc[dfnew_entries['image'].str.contains(filename)]
                        
                        # Überprüfe, ob eine Zeile gefunden wurde
                        if not row.empty:
                        #Pixelzahl und Anzahl der Farbpixel in DataFrame speichern
                            dfnew_entries.loc[row.index, "total_pixels"] = total_pixels
                            dfnew_entries.loc[row.index, "color_pixels"] = color_pixels
                            
                dfnew_entries = dfnew_entries.dropna(subset=['p_cloud_cover'])
                df_copy = dfnew_entries.copy()
                #Delete Duplicates 
                df_copy.drop_duplicates(['day', 'total_pixels', 'color_pixels'], keep='first', inplace=True)
                dfnew_entries =df_copy.copy()
                #Drop tuples weithout picture
                dfnew_entries = dfnew_entries.drop(dfnew_entries[(dfnew_entries['total_pixels'] == 0) & (dfnew_entries['color_pixels'] == 0)].index)
                print(len(df))
                
                # overcastSunny = 'sunny'
                p_cloud_cover = 0.0

                dfnew_entries["Flag"] = "Placeholder"
                dfnew_entries["fu_processed_wacodi_processed"] = 0

                # # # # Schleife über alle Dateien im Ordner
                for filename in os.listdir(path):
                    
                    if filename.endswith(".png"):
                        
                        row = dfnew_entries.loc[df['image'].str.contains(filename)]
                        
                        if not row.empty:
                # #              #print(row)
                            p_cloud_cover = row['p_cloud_cover'].values[0]

                            if p_cloud_cover <= 50.0:
                                overcastSunny = 'overcast'
                            else:
                                overcastSunny = 'sunny'

                            findWaterColour = find_water_colour(os.path.join(path, filename), overcastSunny)

                            successFindWaterColour = findWaterColour['success']
                            fuProcessedWacodiProcessed = findWaterColour['FUvalue']
                            
                            dfnew_entries.loc[row.index, "Flag"] = successFindWaterColour
                            dfnew_entries.loc[row.index, "fu_processed_wacodi_processed"] = fuProcessedWacodiProcessed
                            
            
            
            
            if os.path.exists(csv_path):
                # Lade das DataFrame aus der CSV-Datei
                #df_existing = pd.read_csv(csv_path)
                #dfnew_entries = df[~df['image'].isin(df_existing['image'])]
                df_updated = pd.concat([df_existing, dfnew_entries], ignore_index=True)
                df_updated.to_csv(csv_path, index=False)
                df = df_updated.copy()
            else:
                #dfnew_entries = df.copy()
                dfnew_entries.to_csv(csv_path)
                df = dfnew_entries.copy()
                #dfAll = pd.read_csv(csv_path, sep=',')
                #print(len(dfAll))
                #new_entries['image_path'] = new_entries['image'].apply(lambda url: download_image(url, save_folder))

            delete_all_files_in_folder(path)
            
            dfTrue = df.loc[(df['Flag'] == True)]
            
            print(len(dfTrue))
            
            dfTrue=dfTrue.drop(columns=['active', 'last_update','update_count','input_date','apk_user_n_code','geom', 'image.1', 'nickname.1'])
            dfTrue.to_csv("new_file.csv")
            dfTrue = pd.read_csv("new_file.csv", sep=',')
            #df=df.rename(columns={'Unnamed': 'id'}, inplace=True)
            print(dfTrue.head())
           
            return dfTrue
    except Exception as e:
        print(e)






########################################################################################################
card_Upload = dbc.Card(
    dbc.CardBody(
        [
            html.H2([html.I(className="bi bi-filetype-csv me-2"), "Upload EyeOnWater Data"], className="text-center pe-2"),
            
            html.Br(),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                        'width': '100%',
                        'height': '40px',
                        'lineHeight': '40px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '1px'
                },
                            # Allow multiple files to be uploaded
                multiple=True
            ),
            
            html.Br(),
        ],
        className="border-start border-secondary border-5",
       
    ),
    className="m-2 shadow bg-white rounded ",
)

card_UpdateMapScatterMapbox = dbc.Card(
    dbc.CardBody(
        [
            html.H1([html.I(className="bi bi-map me-2"), "Auswahl Daten"], className="text-nowrap text-center"),
            html.Br(),
            #html.Div(id='map'),
            dcc.Graph(id='scatter-mapbox', figure={}),
        ],
        className="border-start border-secondary border-5",
       
    ),
    className="m-2 shadow bg-white rounded",
)


 
    
    
    
    
#######################################################################################################

layout = html.Div(
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
                                html.Img(src="./assets/ParKli_Wasser_300px.png", height="50", style={'display': 'inline-block'}),
                                html.H1("ParKli Gewässer",style={'textAlign': 'center', 'color': '#2F5F53','display': 'inline-block', 'margin-left': 'auto', 'margin-right': 'auto' }),
                                        
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
                        card_Upload, 
                                
                    ], width={"size": 3, "offset":0}
                ),
                dbc.Col(
                    [
                        card_UpdateMapScatterMapbox,
                                
                    ], width={"size": 9, "offset":0}
                ),
                
                    
            ],
        ),
              
        html.Br(),
       

 
        

        # Erstelle einen Box Select, um Punkte auszuwählen
        
        html.Div(id='select-box'),
        
        #dcc.Graph(id='box-select', figure={}),
    
       
    
        #html.Div(id='scatter-map'),
    
        #html.Div(id='box-plot'),
        
    ]
)
############################################################################################################################

    
@callback(
    Output('scatter-mapbox', 'figure'),
    Output('stored-data', 'dataEyeonWater'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('stored-data','dataEyeonWater'),
    prevent_initial_call=True
    
)
def update_output(list_of_contents, list_of_names, dataEyeonWater):
    if list_of_contents is not None:
        
        print(list_of_contents)
        print(list_of_names)
        
        parsed_data = []
        
        for content, name in zip(list_of_contents, list_of_names):
            parsed_content = parse_contentCSV(content, name)  # Annahme: parse_contents-Funktion extrahiert den Inhalt und gibt einen DataFrame zurück
            parsed_data.append(parsed_content)
    
        df = pd.concat(parsed_data)  # Zusammenführen der einzelnen DataFrames zu einem DataFrame
        
        dataEyeonWater = df.to_dict('records')
        print(type(dataEyeonWater))

        #df = (parse_contentCSV(c,n)( for c, n in zip(list_of_contents, list_of_names))
       
        fig = px.scatter_mapbox(df, 
            lat="lat", 
            lon="lng",
            hover_name="n_code",
            hover_data=["n_code", "date_photo", "device_model", 'nickname','fu_processed','fu_value'],
            color_discrete_sequence=["black"],
            zoom=10, height=300
        )
        #fig.update_layout(mapbox_style="stamen-terrain")
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        
        return fig, dataEyeonWater
    
    return dash.no_update
    


#######################################################################################################################################
# Callback-Funktion für den Box Select
@callback(
    Output('select-box', 'children'),
    Output ('cleanedEyeOnWater-Data', 'cleanedDataEyeonWater'),
    #Output ('unCleanedEyeOnWater-Data', 'unCleanedDataEyeOnWater'),
    Input('scatter-mapbox', 'selectedData'),
    State('stored-data','dataEyeonWater'),
    State ('cleanedEyeOnWater-Data', 'cleanedDataEyeonWater')
    #State('unCleanedEyeOnWater-Data', 'unCleanedDataEyeOnWater')
)
def update_box_select(selectedData, dataEyeonWater, cleanedDataEyeonWater):
    if not selectedData:
        # Wenn keine Daten ausgewählt wurden, zeige einen leeren Plot
        return dash.no_update
    else:
        
        try:
            # Extrahiere die ausgewählten Daten
            print(selectedData)
            points = selectedData['points']
            selected_df = pd.DataFrame(points)
            print(selected_df.head())
            selected_df.info()
            #print(selected_df['hovertext'])
            listHovertext= selected_df['hovertext'].values.tolist()
            df = pd.DataFrame(dataEyeonWater)
            df.info()
            
            
            
            df['date_photo'] = pd.to_datetime(df['date_photo'], format='%m/%d/%Y %I:%M:%S %p')
            df['month_year'] = df['date_photo'].dt.to_period("M")
            df['month'] = pd.DatetimeIndex(df['date_photo']).month
            df['day'] = df['date_photo'].dt.to_period("D")
            df['month_year_period'] = pd.PeriodIndex(df['month_year'], freq='M')
            df['month_year_period'] = df['month_year_period'].apply(lambda x: x.strftime('%Y-%m'))
            
            #df uncleaned 
            #dfCleaned 
            # df hat alle Beonachtungen 
            # df ausgewählter Bereich gibt alle Beobachtungen für diesen Bereich
            #dfCleaned gibt alle Beobachtungen aus der Datei die herangezogen können
            # dfCleaned ausgewählter Bereich gibt differenz zwischen Beobachtungen und verwndeten Bebachtungen für den Bereich
            #Beobachtungen Gesamt (CSV)
            # Beobachtungen Gesamt nach Cleaning
            # Beobachtungen ausgewählter Bereich
            #Beobachtungen Cleaned ausgewählter Bereich
            
            # Dropdown für Übersicht über die Werte
            #Tabelle
            #Wann wurden die Daten erfasst MonatJahr
            #
            
            #unclean Observations 
            boolean_series = df.n_code.isin(listHovertext)
            filtered_df_unclean = df[boolean_series]
            #filtered_df_unclean['date_photo'] = pd.to_datetime(filtered_df_unclean['date_photo'], format='%m/%d/%Y %I:%M:%S %p')
            #filtered_df_unclean['month_year'] = filtered_df_unclean['date_photo'].dt.to_period("M")
            
            print(filtered_df_unclean.head())
            
            # for item in filtered_df_unclean:
            #     item['month_year'] = str(item['month_year'])
                
            # print(filtered_df_unclean.head())
            
            #unCleanedDataEyeOnWater = filtered_df_unclean.to_dict('records')
            
            # print(filtered_df_unclean.head())
            # print(type(filtered_df_unclean))
            # print(type(unCleanedDataEyeOnWater))
            
            
            #df_summed_filtered_df_unclean = filtered_df_unclean.groupby('month_year')['n_code'].count().reset_index()
            #df_summed_filtered_df_unclean['month_year'] = df_summed_filtered_df_unclean['month_year'].apply(lambda x: x.strftime('%Y-%m'))
            
            #figObservationCount = px.bar(df_summed_filtered_df_unclean, x='month_year', y='n_code', labels={'month_year':'Zeit', 'n_code': 'Beobachtungen'})

            
           

            
            #Cleaning Process
            dfCleaned = cleanData(df) 
            
            boolean_series = dfCleaned.n_code.isin(listHovertext)
            filtered_df = dfCleaned[boolean_series]
            
            print(filtered_df.info())
            
            
            
            df_observation_filtered_df = filtered_df.groupby('month_year')['n_code'].count().reset_index()
            df_observation_filtered_df.sort_values(by='month_year')
            #print(df_observation_filtered_df)
            #df_summed_filtered_df_unclean['month_year'] = df_summed_filtered_df_unclean['month_year'].apply(lambda x: x.strftime('%Y-%m'))
            #df_observation_filtered_df['month_year'] = df_observation_filtered_df['month_year'].apply(lambda x: x.strftime('%Y-%m'))
            
            figObservationCount = px.bar(df_observation_filtered_df, x='month_year', y='n_code', labels={'month_year':'Zeit', 'n_code': 'Beobachtungen'})

            #print(data)
           
            cleanedDataEyeonWater = filtered_df.to_dict('records')
            #df.to_dict('records')
  
            #print(cleanedDataEyeonWater.head())
            print(type(cleanedDataEyeonWater))

            fig = px.box(filtered_df, x='month_year', y=['fu_processed', 'fu_value'], points='all', title='Boxplot')
            
            df_ph =  filtered_df.loc[(filtered_df['p_ph'] > 0)]
            df_SecchiDisk =filtered_df.loc[(((filtered_df['sd_depth']) > 0) & ((filtered_df['sd_depth'] < 1)))] 
            #df_SecchiDisk = round(df_SecchiDisk,2)
            
            #Avg per Month
            df_monthly = filtered_df.filter(['date_photo', 'fu_value', 'fu_processed'])
            df_monthly['date_photo'] = pd.to_datetime(df_monthly['date_photo'])
            df_monthly = df_monthly.set_index('date_photo')
            df_monthly = df_monthly.resample('M').mean()
            df_monthly = df_monthly.interpolate()
            df_monthly = df_monthly.reset_index()
            df_avg = df_monthly.melt(id_vars=['date_photo'], var_name='variable', value_name='value')
            figAvgMonth = px.line(df_avg, x='date_photo', y='value', color='variable')
            
            #Durchschnitte berechnen und Runden
            fu_value_mean = filtered_df['fu_value'].mean()
            fu_value_mean = round(fu_value_mean,2)
            fu_processed_mean = filtered_df['fu_processed'].mean()
            fu_processed_mean=round(fu_processed_mean,2)
            
            
            return html.Div(
                [
                    
                    html.Br(),
                    html.Br(),
                    
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        dbc.CardBody(
                                                            [

                                                                html.P(children=["Beobachtungen Gesamt"], className="card-subtitle h5 text-center"),
                                                                html.Br(),
                                                                html.P(children=[len(df)], className="card-subtitle text-n h5 text-center"),
                                                            ],
                                                            className="border-start border-secondary border-5",
                                                        ),
                                                        className="m-2 shadow bg-white rounded h-100 class",
                                                    ),
                                                ],
                                                width={"size": 6},
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        dbc.CardBody(
                                                            [
                                                                #html.P(children=["Anzahl der Beobachtungen im ausgewählten Bereich: ",len(filtered_df)], className="card-subtitle text-nowrap h6 text-center"),
                                                                html.P(children=["Beobachtungen Gesamt bereinigt"], className="card-subtitle h5 text-center"),
                                                                html.Br(),
                                                                html.P(children=[len(dfCleaned)], className="card-subtitle  h5 text-center"),
                                                            ],
                                                                className="border-start border-secondary border-5",
                                                        ),
                                                        className="m-2 shadow bg-white rounded h-100 class",
                                                    )
                                                ],
                                                width={"size": 6},
                                            ),
                                        ],
                                    ),
                                    html.Br(),
                                    
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        dbc.CardBody(
                                                            [

                                                                html.P(children=["Ausgewählter Bereich"], className="card-subtitle h5 text-center"),
                                                                html.Br(),
                                                                html.P(children=[len(filtered_df_unclean)], className="card-subtitle text-n h5 text-center"),
                                                            ],
                                                            className="border-start border-secondary border-5",
                                                        ),
                                                        className="m-2 shadow bg-white rounded h-100 class",
                                                    ),
                                                ],
                                                width={"size": 6},
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        dbc.CardBody(
                                                            [
                                                                #html.P(children=["Anzahl der Beobachtungen im ausgewählten Bereich: ",len(filtered_df)], className="card-subtitle text-nowrap h6 text-center"),
                                                                html.P(children=["Ausgewählter Bereich bereingt"], className="card-subtitle h5 text-center"),
                                                                html.Br(),
                                                                html.P(children=[len(filtered_df)], className="card-subtitle  h5 text-center"),
                                                            ],
                                                                className="border-start border-secondary border-5",
                                                        ),
                                                        className="m-2 shadow bg-white rounded h-100 class",
                                                    )
                                                ],
                                                width={"size": 6},
                                            ),
                                        ],
                                    ),
                                    
                                    html.Br(),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        dbc.CardBody(
                                                            [

                                                                html.P(children=["Forel-Ule-Skala Wert User"], className="card-subtitle h5 text-center"),
                                                                html.Br(),
                                                                html.P(children=[fu_value_mean], className="card-subtitle text-n h5 text-center"),
                                                            ],
                                                            className="border-start border-secondary border-5",
                                                        ),
                                                        className="m-2 shadow bg-white rounded h-100 class",
                                                    ),
                                                ],
                                                width={"size": 6},
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        dbc.CardBody(
                                                            [
                                                                #html.P(children=["Anzahl der Beobachtungen im ausgewählten Bereich: ",len(filtered_df)], className="card-subtitle text-nowrap h6 text-center"),
                                                                html.P(children=["Forel-Ule-Skala Wert App"], className="card-subtitle h5 text-center"),
                                                                html.Br(),
                                                                html.P(children=[fu_processed_mean], className="card-subtitle  h5 text-center"),
                                                            ],
                                                                className="border-start border-secondary border-5",
                                                        ),
                                                        className="m-2 shadow bg-white rounded h-100 class",
                                                    )
                                                ],
                                                width={"size": 6},
                                            ),
                                        ],
                                    ),
                                    html.Br(),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        dbc.CardBody(
                                                            [

                                                                html.P(children=["pH-Werte"], className="card-subtitle h5 text-center"),
                                                                html.Br(),
                                                                html.P(children=[df_ph['p_ph'].mean()], className="card-subtitle text-n h5 text-center"),
                                                            ],
                                                            className="border-start border-secondary border-5",
                                                        ),
                                                        className="m-2 shadow bg-white rounded h-100 class",
                                                    ),
                                                ],
                                                width={"size": 6},
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        dbc.CardBody(
                                                            [
                                                                #html.P(children=["Anzahl der Beobachtungen im ausgewählten Bereich: ",len(filtered_df)], className="card-subtitle text-nowrap h6 text-center"),
                                                                html.P(children=["Secchi-Disk Wert"], className="card-subtitle h5 text-center"),
                                                                html.Br(),
                                                                html.P(children=[df_SecchiDisk['sd_depth'].mean()], className="card-subtitle  h5 text-center"),
                                                            ],
                                                                className="border-start border-secondary border-5",
                                                        ),
                                                        className="m-2 shadow bg-white rounded h-100 class",
                                                    )
                                                ],
                                                width={"size": 6},
                                            ),
                                        ],
                                    ),
                                ],
                                width={"size": 4},
                                className = "h-100 class",
                            ),
                            
                            dbc.Col(
                                [
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H5("Anzahl der Beobachtungen ausgewähler Bereich pro Monat", className="card-title text-center"),
                                                #html.H5("Box-Plot", className="card-title text-center"),
                                                html.Br(),
                                                # dcc.Dropdown(
                                                #     id="dropdownObservation",
                                                #     options=['Bereinigt', 'Unbereinigt'],
                                                #     value='Bereinigt',
                                                # ),
                                                html.Br(),
                                                dcc.Graph(id='observation', figure = figObservationCount),
                                                #html.Br(),
                                            ],
                                            className="border-start border-secondary border-5",
                                            
                                        ),
                                        className="m-2 shadow bg-white rounded h-100 class",
                                    ),
                                ],
                                width={"size": 8},
                                className = "h-100 class",
                            )
                        ]
                    ),
                    html.Br(),
                    html.Br(),
                    
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H5("Streuung der Werte", className="card-title text-center"),
                                                #html.H5("Box-Plot", className="card-title text-center"),
                                                html.Br(),
                                                dcc.Dropdown(
                                                    id="dropdownPlot",
                                                    options=['Box-Plot', 'Scatter-Plot'],
                                                    value='Box-Plot',
                                                ),
                                                html.Br(),
                                                dcc.Graph(id='distribution', figure = fig),
                                                #html.Br(),
                                            ],
                                            className="border-start border-secondary border-5",
                                        ),
                                        className="m-2 shadow bg-white rounded h-100 class",
                                    ),
                                    
                                ],
                                width={"size": 12},
                                className = "h-100 class",
                            ),
                            
                        ],
                    ),
                    
                    html.Br(),
                    html.Br(),
                    
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H5("Durchschnitt pro Monat", className="card-title text-center"),
                                                dcc.Graph(figure = figAvgMonth),
                                                #html.Br(),
                                                
                                            ],
                                            className="border-start border-secondary border-5",
                                            
                                        ),
                                        className="m-2 shadow bg-white rounded h-100 class",
                                    ),
                                    
                                ],
                                width={"size": 6},
                            ),
                            
                              dbc.Col(
                                [
                                    dbc.Card(
                                        dbc.CardBody(
                                            [   
                                                 html.H5("Übersicht über die Werte", className="card-title text-center"),
                                               dash_table.DataTable(
                                                    filtered_df.to_dict('records'),
                                                    [{'name': i, 'id': i} for i in filtered_df.columns],
                                                    #page_size=10,
                                                    filter_action="native",
                                                    sort_action="native",
                                                    sort_mode="single",
                                                    column_selectable="single",
                                                    fixed_rows={'headers': True},
                                                    style_table={'margin': '10px', 'height': '400px'},
                                                    style_cell={'textAlign': 'left', 'padding': '1px', 'minWidth': 95, 'maxWidth': 95, 'width': 95}
                                                ),
                                                
                                            ],
                                            className="border-start border-secondary border-5",
                                            
                                        ),
                                        className="m-2 shadow bg-white rounded h-100 class",
                                    ),
                                ],
                                width={"size": 6},
                            ),
                            
                            
                        ],
                    ),
                    html.Br(),
                    html.Br(),
                ]
            ), cleanedDataEyeonWater #, unCleanedDataEyeOnWater
        
            #return fig
        except Exception as e:
            print(e)

################################################################################################################################        

@callback(
    Output('distribution', 'figure'),
    Input('dropdownPlot', 'value'),
    Input('cleanedEyeOnWater-Data','cleanedDataEyeonWater'),
    prevent_initial_call=True
    
)
def update_distribution(value, cleanedDataEyeonWater):
    
    df = pd.DataFrame(cleanedDataEyeonWater)
    if value == 'Box-Plot':
        fig = px.box(df, x='month_year', y=['fu_processed', 'fu_value'], points='all', title='Boxplot') 
        
        return fig
    elif value == 'Scatter-Plot':
        
        fig= px.scatter(df, x='month_year', y=['fu_processed', 'fu_value'], title='Scatter-Plot')
        
        return fig
    
    return dash.no_update

# ###############################################################################################################################
# @callback(
#     Output('observation', 'figure'),
#     Input('dropdownObservation', 'value'),
#     Input('cleanedEyeOnWater-Data','cleanedDataEyeonWater'),
#     Input('unCleanedEyeOnWater-Data', 'unCleanedDataEyeOnWater'),
#     prevent_initial_call=True
    
# )
# def update_Observation(value, cleanedDataEyeonWater, unCleanedDataEyeOnWater):
    
#     #
#     if value == 'Bereinigt':
#         df = pd.DataFrame(cleanedDataEyeonWater)
#         df_observation_filtered_df = df.groupby('month_year')['n_code'].count().reset_index()
#         df_observation_filtered_df.sort_values(by='month_year')
#         figObservationCount = px.bar(df_observation_filtered_df, x='month_year', y='n_code', labels={'month_year':'Zeit', 'n_code': 'Beobachtungen'})
#         return figObservationCount
        
#     elif value == 'Unbereinigt':
        
#         df = pd.DataFrame(unCleanedDataEyeOnWater)
        
#         df_observation_filtered_df = df.groupby('month_year')['n_code'].count().reset_index()
#         df_observation_filtered_df.sort_values(by='month_year')
#         figObservationCount = px.bar(df_observation_filtered_df, x='month_year', y='n_code', labels={'month_year':'Zeit', 'n_code': 'Beobachtungen'})
#         return figObservationCount
    
#     return dash.no_update




# def parse_contentCSV(contents, filename_csv):
    
    
    
#     content_type, content_string = contents.split(',')
    


#     decoded = base64.b64decode(content_string)
#     try:
#         if 'csv' in filename_csv:
#             # Assume that the user uploaded a CSV file
#             # df = pd.read_csv(
#             #     io.StringIO(decoded.decode('utf-8')))
#             #df = pd.read_csv(
#              #    io.StringIO(decoded.decode('unicode_escape')))
#             df = pd.read_csv(filename_csv, sep=',' , encoding = 'unicode_escape', skipinitialspace=True, skiprows=1)
#             #df = pd.read_csv(filename_csv, sep=',', skiprows=1)
            
#             df['date_photo'] = pd.to_datetime(df['date_photo'], format='%m/%d/%Y %I:%M:%S %p')
#             df['month_year'] = df['date_photo'].dt.to_period("M")
#             df['month'] = pd.DatetimeIndex(df['date_photo']).month
#             df['day'] = df['date_photo'].dt.to_period("D")
#             #df.to_csv("new_file.csv")
#             #df = pd.read_csv("new_file.csv", sep=',')
#             #df.rename(columns={'Unnamed': 'index'}, inplace=True)
#             #print(df.head())
#             #df = df.drop([0, 150])
#             print(len(df))
            
#             allObservationsCount = len(df)
            
#             dfStreuung = df.loc[(abs(df['fu_value'] - df['fu_processed']) < 3.0)]
#             print(len(dfStreuung))
            
#             df = dfStreuung.copy()
            
#             #path = "../../assets/Bilder"
#             # Aktueller Ordner (/src/pages)
#             current_directory = os.getcwd()

#             # Pfad zum Zielordner (/src/assets/Bilder)
#             path = os.path.join(current_directory, 'urlTest/src/assets', 'Bilder')

#             df["total_pixels"] = 0
#             df["color_pixels"] = 0

#             # # # Schleife über alle Dateien im Ordner
#             for filename in os.listdir(path):
                
#                 if filename.endswith(".png"):
#                 # Bild öffnen
#                     img = Image.open(os.path.join(path, filename))
#                     # Gesamtanzahl der Pixel
#                     total_pixels = img.width * img.height

#                     # Anzahl der Farbpixel
#                     color_pixels = len(set(img.getdata()))
                    
                        
#                     row = df.loc[df['image'].str.contains(filename)]
                    
#                     # Überprüfe, ob eine Zeile gefunden wurde
#                     if not row.empty:
#                     #Pixelzahl und Anzahl der Farbpixel in DataFrame speichern
#                         df.loc[row.index, "total_pixels"] = total_pixels
#                         df.loc[row.index, "color_pixels"] = color_pixels
                        
#             df = df.dropna(subset=['p_cloud_cover'])
#             df_copy = df.copy()
#             df_copy.drop_duplicates(['day', 'total_pixels', 'color_pixels'], keep='first', inplace=True)
#             df =df_copy.copy()
#             #df.drop_duplicates(subset=['day', 'total_pixels', 'color_pixels'], keep='first', inplace=True)
#             df = df.drop(df[(df['total_pixels'] == 0) & (df['color_pixels'] == 0)].index)
#             print(len(df))
            
#             # overcastSunny = 'sunny'
#             p_cloud_cover = 0.0

#             df["Flag"] = "Placeholder"
#             df["fu_processed_wacodi_processed"] = 0

#             # # # # Schleife über alle Dateien im Ordner
#             for filename in os.listdir(path):
                
#                 if filename.endswith(".png"):
                    
#                     row = df.loc[df['image'].str.contains(filename)]
                    
#                     if not row.empty:
#             # #              #print(row)
#                         p_cloud_cover = row['p_cloud_cover'].values[0]

#                         if p_cloud_cover <= 50.0:
#                             overcastSunny = 'overcast'
#                         else:
#                             overcastSunny = 'sunny'

#                         findWaterColour = find_water_colour(os.path.join(path, filename), overcastSunny)

#                         successFindWaterColour = findWaterColour['success']
#                         fuProcessedWacodiProcessed = findWaterColour['FUvalue']
                        
#                         df.loc[row.index, "Flag"] = successFindWaterColour
#                         df.loc[row.index, "fu_processed_wacodi_processed"] = fuProcessedWacodiProcessed
                        
#             print(len(df))
            
                         
#             dfTrue = df.loc[(df['Flag'] == True)]
            
#             print(len(dfTrue))
            
#             dfTrue=dfTrue.drop(columns=['active', 'last_update','update_count','input_date','apk_user_n_code','geom', 'image.1', 'nickname.1'])
#             dfTrue.to_csv("new_file.csv")
#             dfTrue = pd.read_csv("new_file.csv", sep=',')
#             #df=df.rename(columns={'Unnamed': 'id'}, inplace=True)
#             print(dfTrue.head())
           
#             return dfTrue
#         else:
#             return dash.no_update
    
#     except Exception as e:
#         print(e)



##################################################################################################################################
# @callback(
#     Output('output-data-upload', 'children'),
#     Input('upload-data', 'contents'),
#     State('upload-data', 'filename')
# )
# def update_output(list_of_contents, list_of_names):
#     if list_of_contents is not None:
#         children = [
#             parse_contents(c, n) for c, n in
#             zip(list_of_contents, list_of_names)]
#         return children
    
    
#####################################################################################################################################
    
# @callback(
#     Output('output-div', 'children'),
#     Input('submit-button','n_clicks'),
#     State('stored-data','data'),
#     State('xaxis-data','value'),
#     State('yaxis-data', 'value'),
#     State('yaxis-data2', 'value')
# )

# def make_graphs(n, data, x_data, y_data, ydata2):
#     if n is None:
#         return dash.no_update
#     else:
#         #bar_fig = px.bar(data, x=x_data, y=y_data)
#         fig = px.box(data, x=x_data, y=[y_data, ydata2], points='all')
#         # print(data)
#         return dcc.Graph(figure=fig)
    
#########################################################
# Callback-Funktion für den Scatter-Button
# @callback(
#     Output('scatter-mapbox', 'figure'),
#     Input('map-button', 'n_clicks'),
#     State('stored-data','data')
# )
# def update_scatter_mapbox(n, data):
#     # Erstelle die Scatter Mapbox
#     if n is None:
#         return dash.no_update
#     else:
#         fig = px.scatter_mapbox(data, 
#             lat="lat", 
#             lon="lng",
#             hover_name="n_code",
#             hover_data=["n_code", "date_photo", "device_model", 'nickname','fu_processed','fu_value'],
#             color_discrete_sequence=["black"],
#             zoom=10, height=400
#         )
#         fig.update_layout(mapbox_style="stamen-terrain")
#         fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#         return fig



# def parse_contents(contents, filename_csv):
#     content_type, content_string = contents.split(',')
    


#     decoded = base64.b64decode(content_string)
#     try:
#         if 'csv' in filename_csv:
#             # Assume that the user uploaded a CSV file
#             # df = pd.read_csv(
#             #     io.StringIO(decoded.decode('utf-8')))
#             #df = pd.read_csv(
#              #    io.StringIO(decoded.decode('unicode_escape')))
#             df = pd.read_csv(filename_csv, sep=',' , encoding = 'unicode_escape', skipinitialspace=True, skiprows=1)
#             #df = pd.read_csv(filename_csv, sep=',', skiprows=1)
            
#             df['date_photo'] = pd.to_datetime(df['date_photo'], format='%m/%d/%Y %I:%M:%S %p')
#             df['month_year'] = df['date_photo'].dt.to_period("M")
#             df['month'] = pd.DatetimeIndex(df['date_photo']).month
#             df['day'] = df['date_photo'].dt.to_period("D")
#             #df.to_csv("new_file.csv")
#             #df = pd.read_csv("new_file.csv", sep=',')
#             #df.rename(columns={'Unnamed': 'index'}, inplace=True)
#             #print(df.head())
#             #df = df.drop([0, 150])
#             print(len(df))
#             print(len(df))
            
#             dfStreuung = df.loc[(abs(df['fu_value'] - df['fu_processed']) < 5.0)]
#             print(len(dfStreuung))
            
#             #path = "../../assets/Bilder"
#             # Aktueller Ordner (/src/pages)
#             current_directory = os.getcwd()

#             # Pfad zum Zielordner (/src/assets/Bilder)
#             path = os.path.join(current_directory, 'urlTest/src/assets', 'Bilder')

#             df["total_pixels"] = 0
#             df["color_pixels"] = 0

#             # # # Schleife über alle Dateien im Ordner
#             for filename in os.listdir(path):
                
#                 if filename.endswith(".png"):
#                 # Bild öffnen
#                     img = Image.open(os.path.join(path, filename))
#                     # Gesamtanzahl der Pixel
#                     total_pixels = img.width * img.height

#                     # Anzahl der Farbpixel
#                     color_pixels = len(set(img.getdata()))
                    
                        
#                     row = df.loc[df['image'].str.contains(filename)]
                    
#                     # Überprüfe, ob eine Zeile gefunden wurde
#                     if not row.empty:
#                     #Pixelzahl und Anzahl der Farbpixel in DataFrame speichern
#                         df.loc[row.index, "total_pixels"] = total_pixels
#                         df.loc[row.index, "color_pixels"] = color_pixels
                        
#             df = df.dropna(subset=['p_cloud_cover'])
#             df_copy = df.copy()
#             df_copy.drop_duplicates(['day', 'total_pixels', 'color_pixels'], keep='first', inplace=True)
#             df =df_copy.copy()
#             #df.drop_duplicates(subset=['day', 'total_pixels', 'color_pixels'], keep='first', inplace=True)
#             df = df.drop(df[(df['total_pixels'] == 0) & (df['color_pixels'] == 0)].index)
#             print(len(df))
            
#             # overcastSunny = 'sunny'
#             p_cloud_cover = 0.0

#             df["Flag"] = "Placeholder"
#             df["fu_processed_wacodi_processed"] = 0

#             # # # # Schleife über alle Dateien im Ordner
#             for filename in os.listdir(path):
                
#                 if filename.endswith(".png"):
                    
#                     row = df.loc[df['image'].str.contains(filename)]
                    
#                     if not row.empty:
#             # #              #print(row)
#                         p_cloud_cover = row['p_cloud_cover'].values[0]

#                         if p_cloud_cover <= 50.0:
#                             overcastSunny = 'overcast'
#                         else:
#                             overcastSunny = 'sunny'

#                         findWaterColour = find_water_colour(os.path.join(path, filename), overcastSunny)

#                         successFindWaterColour = findWaterColour['success']
#                         fuProcessedWacodiProcessed = findWaterColour['FUvalue']
                        
#                         df.loc[row.index, "Flag"] = successFindWaterColour
#                         df.loc[row.index, "fu_processed_wacodi_processed"] = fuProcessedWacodiProcessed
                         
#             #dfTrue = df.loc[(df['Flag'] == True)]
            
#             df=df.drop(columns=['active', 'last_update','update_count','input_date','apk_user_n_code','geom', 'image.1', 'nickname.1'])
#             df.to_csv("new_file.csv")
#             df = pd.read_csv("new_file.csv", sep=',')
#             #df=df.rename(columns={'Unnamed': 'id'}, inplace=True)
#             print(df.head())
           
            
            
#         elif 'xls' in filename:
#             # Assume that the user uploaded an excel file
#             df = pd.read_excel(io.BytesIO(decoded))
#     except Exception as e:
#         print(e)
#         return html.Div([
#             'There was an error processing this file.'
#         ])

#     return html.Div([
        
#         dbc.Row([
#             dbc.Col([
#                 html.H5(filename_csv, style={'textAlign': 'center'}),
#                 html.Br(),
#                 html.P("Inset X axis data"),
#                 dcc.Dropdown(id='xaxis-data',
#                     options=[{'label':x, 'value':x} for x in df.columns]),
#                 html.Br(),
#                 html.P("Inset Y axis data"),
#                 dcc.Dropdown(id='yaxis-data',
#                     options=[{'label':x, 'value':x} for x in df.columns]),
#                 dcc.Dropdown(id='yaxis-data2',
#                     options=[{'label':x, 'value':x} for x in df.columns]),
#                 html.Br(),
#                 #html.Button(id="submit-button", children="Create Graph"),
#                 dbc.Button("Create Graph", id="submit-button", outline=True, color="secondary", className="me-2"),
#                 dbc.Button("Create Map", id="map-button", outline=True, color="secondary", className="me-2"),
#                 html.Br(),
#                 html.Br(),
#             ], width={"size": 3, "offset":1})
#         ]),  
#         #html.H5(filename),
#         #html.H6(datetime.datetime.fromtimestamp(date)),
         

#         html.Hr(),
        
#         dbc.Row([
#             dbc.Col([
#                 dash_table.DataTable(
#                     df.to_dict('records'),
#                     [{'name': i, 'id': i} for i in df.columns],
#                     #page_size=10,
#                     filter_action="native",
#                     sort_action="native",
#                     sort_mode="single",
#                     column_selectable="single",
#                     fixed_rows={'headers': True},
#                     style_table={'margin': '10px', 'height': '400px'},
#                     style_cell={'textAlign': 'left', 'padding': '1px', 'minWidth': 95, 'maxWidth': 95, 'width': 95}
#                 ),
#             ], width=12)
#         ]),  
        
#         # dash_table.DataTable(
#         #     df.to_dict('records'),
#         #     [{'name': i, 'id': i} for i in df.columns],
#         #     page_size=10,
#         #     filter_action="native",
#         #     sort_action="native",
#         #     sort_mode="single",
#         #     column_selectable="single",
#         #     style_table={'margin': '10px'},
#         # ),
        
#         dcc.Store(id='stored-data', data=df.to_dict('records')),
        
#         #  dash_table.DataTable(
#         #     dfTrue.to_dict('records'),
#         #     [{'name': i, 'id': i} for i in dfTrue.columns]
#         # ),

#         html.Hr(),  # horizontal line
#         #dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True),

#         # For debugging, display the raw contents provided by the web browser
#         # html.Div('Raw Content'),
#         # html.Pre(contents[0:200] + '...', style={
#         #     'whiteSpace': 'pre-wrap',
#         #     'wordBreak': 'break-all'
#         # })
#     ])