# Import packages
import requests
import json
import pandas as pd
import datetime as dt
import plotly.graph_objects as go
from plotly.colors import n_colors
import numpy as np
import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash import dcc, html
from datetime import date



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])

# Set up colors
dict_layout_cols = {
    'primary' : 'rgb(76,155,232)',
    'green' : 'rgb(92,184,92)',
    'yellow': 'rgb(255,193,7)',
    'red': 'rgb(217,83,79)',
    'bg_blue': 'rgb(56, 97, 141)',
    'white': 'rgb(255, 255,255)',
    'bg_blue2' : 'rgb(15,37,55)'
}



#region Grid Map
"""
SET UP GRID MAP
"""

## READ GEOGPRAPHICAL DATA
#shp_grid = gdp.read_file('Shapefiles/DKN_10KM_epsg4326_filtered.shp')
# Rename None to 'No name'
#shp_grid['Stednavn'].fillna('No name', inplace = True)

# Set url to geojson
url = 'https://raw.githubusercontent.com/Maud10/DMI_Wind_DashApp/main/assets/Shapefiles/DKN_10KM_epsg4326_filtered.geojson'
geoj_grid = json.loads(requests.get(url).text)


shp_grid = pd.json_normalize(geoj_grid['features'])

shp_grid.rename(columns = {'properties.KN10kmDK':'KN10kmDK',
                          'properties.Stednavn':'Stednavn'}, inplace = True)


shp_grid['Stednavn'].fillna('No name', inplace = True)



## SET UP FIGURE
# Map center
dict_cent = {'lon':  10.582594514193142,
             'lat':55.85925614742615
            }


# Color columns
shp_grid['Val'] = 1
shp_grid['Col'] = 'rgba(76,155,232,0.4)'

# Hover columns
hover_data_map = np.stack(
    (shp_grid['Stednavn'],
    shp_grid['Stednavn']), axis = 1)

# Figure
fig_map = go.Figure(
    go.Choroplethmapbox(
        geojson= geoj_grid,
        featureidkey= "properties.KN10kmDK",
        locations= shp_grid['KN10kmDK'],
        z= shp_grid['Val'],
        colorscale= shp_grid['Col'],
        showscale= False,
        customdata= hover_data_map,
        hovertemplate= '%{customdata[0]}<extra></extra>',
        colorbar= {'outlinecolor' : dict_layout_cols['primary']}
    ),
    layout = go.Layout(
        mapbox = dict(
            accesstoken = 'pk.eyJ1IjoibWFqaGFsIiwiYSI6ImNrd3F3MmgyYTBxc3oydWxja3ZwNnB1enIifQ.XQ6h4h4UsdD_9y2WsOUbcw',
            center = dict_cent,
            zoom = 7,
            style = "dark"
        ),
        autosize=True,
        #width=1000,
        height=250,
        margin=dict(l=20, r=20, t=5, b=0),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        clickmode= 'event+select'
    )
)


# Update layout
# fig_map.update_layout(
#     mapbox_style = "white-bg", #Decide a style for the map
#     mapbox_zoom = 7, #Zoom in scale
#     mapbox_center = dict_cent)

fig_map.update_traces(marker_line_width = 0.3)

#fig_map.show()
#endregion


#region Wind Rose
"""
SET UP WIND ROSE
"""

## CREATE DIRECTIONS DATA FRAME
# Create bins
# Create bins
bins = np.arange(start = 0, stop = 360, step = 22.5)
# Create list of directions
dirs = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']

# Create data frame
df_wind_dir_col = pd.DataFrame({'Direction':dirs,
                              'Degree': bins,
                                'Radius' : np.repeat(100,len(dirs))
                              }
                              )
# Calculate coordinates for angles
df_wind_dir_col['Y_cord'] = -round(np.cos(np.deg2rad(df_wind_dir_col['Degree']) ),2) * 12
df_wind_dir_col['X_cord'] = round(np.sin(np.deg2rad(df_wind_dir_col['Degree']) ),2) * 12
dict_dir_coord = df_wind_dir_col[['Direction', 'X_cord', 'Y_cord']].set_index('Direction').to_dict('index')



## CREATE FUNCTION TO CONVERT DEGREES TO CARDINAL DIRECTIONS
def fun_DegToCard(d):
    card = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
    ix = round(d / (360. / len(card)))
    card_text = card[ix % len(card)]
    return card_text

## DEFINE COLOR PALETTE
blues = n_colors('rgb(39, 18, 228)', 'rgb(68, 196, 228)', n_colors = 4,colortype = 'rgb')
greens =  n_colors('rgb(6, 121, 37)', 'rgb(129, 233, 49)', n_colors = 4,colortype = 'rgb')
yellow=  n_colors('rgb(218, 233, 10)', 'rgb(233, 166, 10)', n_colors = 4,colortype = 'rgb')
reds=  n_colors('rba(246, 105, 35)', 'rba(179, 0, 0)', n_colors = 4,colortype = 'rgb')

# Append colors
cols = blues + greens + yellow + reds

# Create dict with directions and colors
col_pal = dict(zip(dirs, cols))

## SET UP FIGURE
# Create column with color for directions
cols_wind = df_wind_dir_col['Direction'].map(col_pal)

# Add hover data
hover_data_windrose = np.stack(
    (df_wind_dir_col['Direction'],df_wind_dir_col['Degree']),
    axis = 1)

# Set up figure
fig_windrose = go.Figure(
    go.Barpolar(
    r= df_wind_dir_col['Radius'],
    theta0 = 0,
    dtheta = 22.5,
    marker = dict(color = cols_wind),
    customdata = hover_data_windrose,
    #ids = df_wind_dir_col['Direction']
    hovertemplate = '%{customdata[0]}<extra></extra>'
    ),
    layout = go.Layout(
        autosize = True,
        height= 200,
       # width = 200,
        margin = dict(l=10, r=10, t=0, b=15),
        paper_bgcolor ='rgba(255,255,255,0)',
        font_size=16,
        legend_font_size=16,
        polar_bgcolor = 'rgba(255,255,255,0)',
        polar_angularaxis_gridcolor = 'rgba(255,255,255,0)',
        polar_angularaxis_linecolor = 'rgba(255,255,255,0)',
        polar_radialaxis_gridcolor = 'rgba(255,255,255,0)',
        # hoverlabel=dict(bgcolor='rgba(255,255,255,0.1)',
        #                                font=dict(color='black')),
        polar_angularaxis_direction='clockwise',
        polar_angularaxis_rotation=90,
        polar_angularaxis_showticklabels=False,
        polar_radialaxis_showticklabels=False,
        polar_radialaxis_showline=False,
        title= {
            'text': 'Wind direction',
            'y': 0.95,
            'x' : 0.5,
            'xanchor':'center',
            'font': {'color' : dict_layout_cols['white'],
                      'size' : 16
                      }
        }

    )
)


#fig_windrose.show()
#endregion

#WindDir

#endregion
# App layout
app.layout = html.Div([

    # Header
    html.Div(
        [
            html.Div([
            # Text
            html.H2("DMI - Weather App"),
            ],
            style= {'width' : '85%'})
        ,
        html.Div([
            html.A(
                html.Img(src=app.get_asset_url('dash-new-logo.png'),
                     style={'height': '50px'}),
                href="https://plotly.com/dash/",
                style={'width': '20%'}
            ),

        ])
    ],
        style= {'display': 'flex'},
    ),

    # Intialize card for screen
    dbc.Card(
        dbc.CardBody([


    # First row - define input
    dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Card([
                        dbc.CardBody([

                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.Div(
                                                [
                                                    html.H4("Previous date"),
                                                    html.Div(
                                                        'Choose date and area from the map to display wind conditions'),
                                                    html.Br(),
                                                    dcc.DatePickerSingle(
                                                        id='date_picker',
                                                        min_date_allowed=date(2019, 1, 1),
                                                        max_date_allowed=date.today(),
                                                        date=date.today(),
                                                        display_format='YYYY-MM-DD'
                                                    ),
                                                    html.Br(),
                                                    html.Br(),
                                                    html.H4("Forecast date"),
                                                    html.Div('To be implemented...'),
                                                    # dcc.DatePickerSingle(
                                                    #     id='date_picker',
                                                    #     min_date_allowed=date(2019, 1, 1),
                                                    #     max_date_allowed=date.today(),
                                                    #     date=date.today(),
                                                    #     display_format='YYYY-MM-DD'
                                                    # )
                                                ], style={'height': '100%'}),
                                        ]),
                                ],
                                style={'height': '50%'},
                                color='primary',
                            ),

                            html.Br(),
                            #html.Br(),

                            dbc.Card(
                                [
                               # dbc.CardHeader('Credits'),

                                dbc.CardBody([

                                    html.H4('Credits'),
                                    html.Div('Weather data is collected from DMI Rest API:'),
                                    html.A('DMI', href='https://confluence.govcloud.dk/display/FDAPI',
                                           target='_blank',
                                           style={'color': 'white'}),

                                    html.Div('Source code can be found at GitHub'),
                                    html.A('GitHub', href='https://github.com/Maud10',
                                           style={'color': 'white'}),
                                    html.Br(),
                                    html.Br(),
                                    html.Div('Love, hate or life advice can be sent to'),
                                    html.Div('martinjhallberg@gmail.com')
                                ], style={'height': '100%'}
                                ),
                                    ],style={'height': '46%'},
                                color = 'primary'
                            )
                        ],
                        style = {'padding': '0rem'})
                    ],
                        style = {'height': '100%'},
                        color = 'rgba(255,255,255,0'
                    )
                ],

            width={'size': 3, "offset": 0, 'order': 1}
            ),



            dbc.Col(
                dbc.Card(

                    dbc.CardBody(
                        [
                        html.Div([
                            dcc.Graph(id='map_figure', figure=fig_map,
                                      config={
                                          'displayModeBar': False},
                                      style={'width' : '100%',
                                             'height': '100%'})
                        ],style={'width' : '100%',
                                 'height': '40%'}
                        ),

                        html.Div([

                            html.Div(
                            dcc.Graph(
                                id='bar_chart', figure={},
                                config={
                                    'displayModeBar': False},
                                style={'height': '100%',
                                       #'display': 'block'
                                       },
                            ),
                                style={'height': '40%',
                                       'width': '85%',
                                       #'display': 'block'
                                       },
                            ),
                            html.Div([

                                #html.Div('Wind direction',
                                #        style= {'text-align' : 'center'}),
                            dcc.Graph(
                                id='wing_rose', figure=fig_windrose,
                                config={
                                    'displayModeBar': False}
                            ),
                                ],style={'height': '20%',
                                       'width' : '15%',
                                        'margin': '7% 0%'
                                       #'display': 'block'
                                       },
                            ),

                        ], style = {'display':'flex'},
                        ),

                        ]
                    ),
                style= {'height':'100%'},
                color = dict_layout_cols['bg_blue'],
                outline = False,
                ),
                    width={'size': 9 , "offset":0 , 'order': 2},
                    ),


        ],
        #className="g-0", # remove horizontal space between elements
    ),





])
,color= dict_layout_cols['bg_blue2']
)


],style= {'margin' : '1.5% 3%'})



@app.callback(
   # Output('output_date_picker', 'children'),
    Output('bar_chart', 'figure'),
    Input('date_picker', 'date'),
    Input('map_figure', 'clickData')
)




def update_output(date_value, clk_data):
    # Input data
    date_object = date.fromisoformat(date_value)
    date_string = date_object.strftime('%Y-%m-%d')
    date_to_str = date_string




    # Initialize default chart
    if clk_data is None:
        #print('empty')
        # Get DMI data
        cellid = shp_grid['KN10kmDK'].sample(n = 1).values[0]
        cellname = shp_grid.loc[shp_grid['KN10kmDK'] == cellid, 'Stednavn'].values[0]
        #print(cellid)
        # Get DMI data
        df, date_from_str = fun_get_filter_dmi_data(
             date_to_str=date_to_str
             , cellid=cellid)

       # print(df)

        # Create figure
        fig_out = fun_fig_chart(df, cellname, date_from_str, date_to_str)

    else:
        # Help prints
        #print(f'Click data: {clk_data}')
        cellid =clk_data['points'][0]['location']
        cellname = clk_data['points'][0]['customdata'][0]

        # Get DMI data
        df, date_from_str = fun_get_filter_dmi_data(
             date_to_str=date_to_str
             , cellid=cellid)

        #print(df)

        # Create figure
        fig_out = fun_fig_chart(df, cellname, date_from_str, date_to_str)

    string_prefix = 'You have selected: '
    string_suffix = 'Area: '
    string_out = string_prefix + date_string + string_suffix + cellname + ' CellID: ' + cellid

    #print(string_out)
    #return string_out,\
    return fig_out


#region HELPER FUNCTIONS
#region DEFINE FUNCTION FOR GETTING DMI DATA
def fun_get_filter_dmi_data(
        date_to_str, # the last date for which the data is gotten
        cellid, # id from grid cell
        obs_values=['mean_wind_speed', 'max_wind_speed_3sec', 'mean_wind_dir'],# which observations from DMI data to keep
        no_days=2, # number of days to get data for
        api_key = '604e80dd-9ee9-454b-aea0-12edc1ead8bf', # api key for DMI API
        stationid='', # extra parameter, if weather station data
                      # is used instead of grid data
        limit = 10000 # max number of observations to get
):
    ## Calculate first date
    # Create date format from string
    date_to = dt.date.fromisoformat(date_to_str)

    # Add hour to get CEST (ignoring summertime)
    date_to = date_to + dt.timedelta(hours=1)

    # Calculate start date
    date_from = date_to - dt.timedelta(days=no_days)

    # Create string to connection string
    date_to_str = date_to_str + 'T23:00:00Z'
    date_from_str = str(date_from) + 'T00:00:00Z'

    ## Set up connection string
    if not stationid:
        str_geo = '&cellId=' + cellid
        dmi_path = 'https://dmigw.govcloud.dk/v2/climateData/collections/10kmGridValue/items?'
    else:
        str_geo = '&stationId=' + stationid
        dmi_pah = 'https://dmigw.govcloud.dk/v2/climateData/collections/stationValue/items?'

    time_res = 'hour'  # time interval for obersvations
    str_datetime = 'datetime=' + date_from_str + "/" + date_to_str
    str_time_res = '&timeResolution=' + time_res
    str_limit = '&limit=' + str(limit)
    str_api_key = '&api-key=' + api_key

    # Concatenate all
    req_str = dmi_path + str_datetime + str_time_res + str_geo + str_limit + str_api_key
    # req_str = dmi_path + 'datetime='+ date_from_str + "/" + date_to_str +  '&timeResolution=' + time_res +  '&api-key=' + api_key
    #print(req_str)

    ### Get data ###
    # Get data and create data
    data = json.loads(
        requests.get(req_str).text
    )

    # Get date into data frame
    data = pd.json_normalize(data['features'])

    ## Transform data ##

    # 1) Subset relevant columns
    cols_keep = [col for col in list(data.columns) if 'properties' in col]
    data = data[cols_keep].copy()

    # 2) Rename columns
    cols_keep_new_name = [col.replace("properties.", "") for col in cols_keep]
    data.columns = cols_keep_new_name

    # 3) Filter rows
    data = data[data['parameterId'].isin(obs_values)]

    # 4) Pivot table
    data = pd.pivot_table(data, values='value',
                          index='from',
                          columns='parameterId').reset_index()

    # 5) Create date columns
    data['from_datetime'] = pd.to_datetime(data['from'].str.replace('\+00:00', "", regex=False))
    data['date'] = data['from_datetime'].dt.date

    # 6) Drop rows with na
    data.dropna(inplace=True)


    # Return
    return data , date_from_str
#endregion


#region DEFINE FUNCTION FOR FIGURE

def fun_fig_chart(df, AreaName, date_from_str, date_to_str):
    # Create column with cardinal direction
    df['Wind_CardDir'] = df['mean_wind_dir'].apply(fun_DegToCard)
    # Assign color based on cardinal direction
    df['Wind_Dir_Col'] = df['Wind_CardDir'].map(col_pal)

    # Hover data
    hover_data_chart = np.stack(
        (df['mean_wind_dir'], df['Wind_CardDir'], df['from_datetime'].dt.hour.astype(str) + ':00')
        , axis = 1)

    # Figure
    fig_chart = go.Figure()


    # Add first trace
    fig_chart.add_trace(go.Bar(x=df['from_datetime'], y=df['mean_wind_speed']
                         , marker=dict(color=df['Wind_Dir_Col']),
                         customdata=hover_data_chart,
                         hovertemplate=
                         'Mean wind speed: %{y} m/s' +
                         '<br>Wind direction: %{customdata[1]} (%{customdata[0]}\xb0)' +
                         '<br>Time: %{customdata[2]}<extra></extra>',
                        hoverlabel=dict(
                                   bgcolor='rgba(255,255,255,0.3)',
                                   font=dict(color='black')
                               ),
                         showlegend=True,
                               name='Avg. wind speed',
                               legendrank=  2,
                         ),
                  #secondary_y=False
                        )

    fig_chart.add_trace(go.Scatter(x=df['from_datetime'], y=df['max_wind_speed_3sec'],
                             hovertemplate=
                             'Max wind speed (3s): %{y} m/s<extra></extra>',
                                  # hoverlabel=dict(
                                  #     bgcolor='rgba(255,255,255,0.3)',
                                  #     font=dict(color='black')
                                  # ),
                             showlegend=True,
                                   name = 'Max. wind speed',
                                   legendrank=1
                                   ),
                  #secondary_y=True
                        ),




    # Add wind direction arrows
    for i, row in df.iterrows():

        x_date = row['from_datetime']

        # fig_chart.add_layout_image(
        #     dict(
        #         source=Image.open(f"figures/arrow_ene.png"),
        #         #xref="x",
        #         #yref="y",
        #         x=x_date,
        #         y=12,
        #         sizex=3000,
        #         sizey=3000,
        #         sizing="contain",
        #         opacity=0.8,
        #         layer="above"
        #     )
        # )


        ax = dict_dir_coord[row['Wind_CardDir']]['X_cord']
        ay = dict_dir_coord[row['Wind_CardDir']]['Y_cord']

        #print(x_date)
        #print(row['Wind_CardDir'])
        #print(ax)
        #print(ay)
        fig_chart.add_annotation(
            x= x_date,
            y = row['mean_wind_speed'] + 1,
            ax = ax,
            ay = ay,
            arrowhead=3,
            arrowsize=1.6,
            arrowwidth=1.1,
            arrowcolor=dict_layout_cols['primary'],
           # xref="x",
            yref="y"
        )



    # Set axes
    h = 285
    max_y = max(max(df['mean_wind_speed']), max(df['max_wind_speed_3sec'])) + 6  # Find maximun y-value from the two
    min_y = 0
    y_ax_range = dict(range=[min_y, max_y])

    fig_chart.update_yaxes(gridcolor = 'rgba(255,255,255,0.4)',
                           color = dict_layout_cols['white'],
                           gridwidth = 0.0001)

    fig_chart.update_xaxes(color=dict_layout_cols['white'])

    # Set layout
    fig_chart.update_layout(
        yaxis=y_ax_range,#, yaxis2=y_ax_range
        autosize=True,
        #width=800,
        height=330,
        hovermode='x unified',
        hoverlabel=dict(bgcolor='rgba(255,255,255,0.75)',
                          font=dict(color='black')
                          ),
        margin=dict(l=0, r=20, t=20, b=20),
        plot_bgcolor = 'rgba(0, 0, 0, 0)',
        paper_bgcolor = 'rgba(0, 0, 0, 0)',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(76,155,232,0.4)',
            font = dict(color= dict_layout_cols['white'])
            ),
        title = {'text': 'Wind at {}, {} - {}'.format(AreaName, date_from_str[0:10], date_to_str),
                 'x': 0.5,
                 'y':0.94,
                 'font': {'color': dict_layout_cols['white']}
                 }
    )





    #print(x_date)

    return fig_chart

#endregion
#endregion


app.run_server(debug=True)