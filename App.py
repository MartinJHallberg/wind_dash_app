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
from dash.dependencies import Input, Output, State
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
# Set url to geojson
url = 'https://raw.githubusercontent.com/MartinJHallberg/DMI_Wind_DashApp/main/assets/DKN_10KM_epsg4326_filtered_wCent.geojson'
geoj_grid = json.loads(requests.get(url).text)

#url = "C:/Users/marti/Dokument/Data Science/DMI/DKN_10KM_epsg4326_filtered_wCent.geojson"
#geoj_grid = json.loads(requests.get(url).text)
#with open(url) as f:
#    geoj_grid = json.load(f)

#print(geoj_grid)



shp_grid = pd.json_normalize(geoj_grid['features'])

print(shp_grid.columns)
shp_grid.rename(columns = {'properties.KN10kmDK':'KN10kmDK',
                          'properties.Stednavn':'Stednavn',
                           'properties.cent_lon': 'cent_lon',
                           'properties.cent_lat': 'cent_lat'}, inplace = True)

# Rename None to 'No name'
shp_grid['Stednavn'].fillna('No name', inplace = True)



## SET UP FIGURE
# Map center
dict_cent = {'lon':  13,
             'lat':55.86
            }


# Color columns
shp_grid['Val'] = 1
shp_grid['Col'] = 'rgba(76,155,232,0.4)'

# Hover columns
hover_data_map = np.stack(
    (shp_grid['Stednavn'],
    shp_grid['cent_lon'],
     shp_grid['cent_lat']), axis = 1)

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
        height=650,
        margin=dict(l=0, r=0, t=0, b=0),
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


# App layout
app.layout = html.Div([

    dcc.Graph(id='map_figure', figure=fig_map,
              config={
                  'displayModeBar': False},
              style={'width': '100%',
                     'height': '100'}),

            html.Div([
                dbc.Button('About',
                           id = 'modal-button',
                           n_clicks=0),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle('DMIWindApp')),
                        dbc.ModalBody('Data is collected from bla bla bla')
                    ],
                    id = 'modal',
                    is_open= False,
                ),

                html.A(
                    html.Img(src=app.get_asset_url('dash-new-logo.png'),
                             style={'height': '40px'}),
                    href="https://plotly.com/dash/",
                    style={'right': '0px'}
                ),
            ],
            style= {'display': 'inline-block'
                }
                )
    ,


    html.Br(),
    html.Div(
        [
            dcc.DatePickerSingle(
                id='date_picker',
                min_date_allowed=date(2019, 1, 1),
                max_date_allowed=date.today(),
                date=date.today() - dt.timedelta(days=1),
                display_format='YYYY-MM-DD'
            ),
        ],
        style={'top': '10px',
               'left': '10px',
               'position': 'absolute'}
    ),


    # Side panel
    html.Div(
        [

            dcc.Loading(
                 id='loading-1',
                 type='default',
                color = 'rgb(246,105,35)',
                 children=[


            html.Br(),
            html.H3(
                id = 'area_headline',
                 style = {'color': dict_layout_cols['white'],
                          'textAlign': 'center'}),


        # Backcast panel
       html.Div(
        [

           # dcc.Loading(
           #     id='loading-1',
           #     type='default',
           #     children=[
            dcc.Graph(
            id='bar_chart', figure={},
            config={
                'displayModeBar': False},
                style={'height': '230px',
                       'width': '95%',
                   "display": "block",
                   "margin-left": "auto",
                   "margin-right": "auto",
                   },
        )
                   #]),
            ]
        , style={'height': '40%',
               'width': '94%',
                 "display": "block",
                 "margin-left": "auto",
                 "margin-right": "auto",
                 'backgroundColor': 'rgba(76,155,232,0.3)'
           }
    ),

    html.Br(),

    # # Forecast panel
    # html.Div([
    #
    #     html.Div([
    #         #dcc.Loading(
    #         #    id='loading-2',
    #         #    type='default',
    #         #    children=[
    #                 dcc.Graph(
    #                     id='bar_chart_2', figure={},
    #                     config={
    #                         'displayModeBar': False},
    #                     style={'height': '200px',
    #                            'width': '95%',
    #                            "display": "block",
    #                            "margin-left": "auto",
    #                            "margin-right": "auto",
    #                            },
    #                 )
    #           # ]),
    #     ], style={'height': '50%',
    #               'width': '100%',
    #               'right': '0px',
    #               'top': '0px',
    #               #'position': 'relative',
    #               },
    #
    #     ),
    #
    #     html.Div([
    #         #dcc.Loading(
    #         #    id='loading-3',
    #         #    type='default',
    #         #    children=[
    #                 dcc.Graph(
    #                     id='bar_chart_3', figure={},
    #                     config={
    #                         'displayModeBar': False},
    #                     style={'height': '200px',
    #                            'width': '95%',
    #                            "display": "block",
    #                            "margin-left": "auto",
    #                            "margin-right": "auto",
    #                            },
    #                 )
    #           #  ]),
    #     ], style={'height': '50%',
    #               'width': '100%',
    #               'right': '0px',
    #               'top': '0px',
    #               #'position': 'absolute',
    #               },
    #     )
    #
    # ],style={'height': '60%',
    #          'width': '94%',
    #          "display": "block",
    #          "margin-left": "auto",
    #          "margin-right": "auto",
    #          'backgroundColor': 'rgba(246,105,35,0.3)'
    #
    #              #'top': '250px',
    #              #'position': 'absolute',
    #             },
    #
    #
    # ),
                     ]),

        ],style={'height': '100%',
                  'width': '50%',
                  'right': '0px',
                  'top': '0px',
                  'position': 'absolute',
                  'backgroundColor': 'rgba(15,37,55,0.5)'
                  },
    ),

],style= {'position': 'relative',
          'height': '100%'},)


# Figure callback
@app.callback(
   # Output('output_date_picker', 'children'),
    Output('bar_chart', 'figure'),
    #Output('bar_chart_2', 'figure'),
    #Output('bar_chart_3', 'figure'),
    Output('area_headline', 'children'),
    Input('date_picker', 'date'),
    Input('map_figure', 'clickData'),
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
        #cell_lon = clk_data['points'][0]['customdata'][1]
        #cell_lat = clk_data['points'][0]['customdata'][2]
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
        print(f'Click data: {clk_data}')
        cellid =clk_data['points'][0]['location']
        cellname = clk_data['points'][0]['customdata'][0]
        cell_lon = clk_data['points'][0]['customdata'][1]
        cell_lat = clk_data['points'][0]['customdata'][2]

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


    #return fig_out, fig_out, fig_out, cellname
    return fig_out, cellname


# Modal callback
@app.callback(
    Output("modal", "is_open"),
    Input("modal-button", "n_clicks"),
    [State("modal", "is_open")],
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

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
    return data, date_from_str
#endregion

#region DEFINE FUNCTION FOR FORECAST DATA (FCOO)
# Define function to get data
def fun_get_fcoo_data(var, lat, lon):
    # Base string to FCOO
    fcoo_path = 'https://app.fcoo.dk/metoc/v2/data/timeseries?variables='

    # Construct request string
    req_str = fcoo_path + var + '&lat=' + str(lat) + '&lon=' + str(lon)
    print(req_str)

    # Collect data
    data = json.loads(
        requests.get(req_str).text
    )

    l_cols = list(data[var].keys())

    if len(l_cols) == 1:
        df = pd.DataFrame(
            {'WavePeriod': data[var][l_cols[0]]['data'],
             'Time': data[var][l_cols[0]]['time']
             })
    else:
        df = pd.DataFrame(
            {l_cols[0]: data[var][l_cols[0]]['data'],
             l_cols[1]: data[var][l_cols[1]]['data'],
             'Time': data[var][l_cols[0]]['time']
             })

    # Set time as index to simpify join
    #df.set_index('Time', inplace=True)


    df['Time'] = pd.to_datetime(df['Time'])
    return df

# Define function to calcualate wind direction and magnitude
def fun_vec_to_dir_mag(df,
                       u_vec,
                       v_vec,
                       var):
    dir_name = var + 'Dir'
    mag_name = var + 'Magnitude'

    df[dir_name] = round(np.arctan2(df[u_vec], df[v_vec]) * 180 / np.pi + 180, 0)
    df[mag_name] = round(np.sqrt(df[u_vec] ** 2 + df[v_vec] ** 2), 1)

    return df

#endregion

#region DEFINE FUNCTION FOR WEATHER FIGURE

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

        ax = dict_dir_coord[row['Wind_CardDir']]['X_cord']
        ay = dict_dir_coord[row['Wind_CardDir']]['Y_cord']

        #print(x_date)
        #print(row['Wind_CardDir'])
        #print(ax)
        #print(ay)
        fig_chart.add_annotation(
            x= x_date,
            y = row['mean_wind_speed'] + 2,
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
    max_y = 30
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
        height=230,
        hovermode='x unified',
        hoverlabel=dict(bgcolor='rgba(255,255,255,0.75)',
                          font=dict(color='black')
                          ),
        margin=dict(l=0, r=20, t=33, b=40),
        plot_bgcolor = 'rgba(0, 0, 0, 0)',
        paper_bgcolor = 'rgba(0, 0, 0, 0)',
        legend=dict(
            yanchor="top",
            y=1.15,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(76,155,232,0.4)',
            font = dict(color= dict_layout_cols['white'])
            ),
        title = {'text': 'Wind {} - {}'.format(date_from_str[0:10], date_to_str),
                 'x': 0.5,
                 'y':0.95,
                 'font': {'color': dict_layout_cols['white'],
                          'size': 15}
                 }
    )





    #print(x_date)

    return fig_chart

#endregion
#endregion



if __name__ == '__main__':
    app.run_server(debug=True)
