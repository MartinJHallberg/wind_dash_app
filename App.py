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
from plotly.subplots import make_subplots
from dotenv import load_dotenv
import os

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])


# API keys
load_dotenv()
dmi_api = os.getenv("dmi_key")
mapbox_api = os.getenv("mapbox_key")

# Set up colors
dict_layout_cols = {
    'primary': 'rgb(76,155,232)',
    'green': 'rgb(92,184,92)',
    'yellow': 'rgb(255,193,7)',
    'red': 'rgb(217,83,79)',
    'bg_blue': 'rgb(56, 97, 141)',
    'white': 'rgb(255, 255,255)',
    'bg_blue2': 'rgb(15,37,55)',
    'orange': 'rgb(246,105,35)',
    'transparent': 'rgba(255,255,255,0)'
}


# region FUNCTION FOR TRANSPARENT COLORS

def fun_col_to_trans(col, transparency):
    # Convert transparency to string
    t_trans = str(transparency)

    # Split text and insert transparency
    col_out = col.split(')')[0] + ',' + t_trans + ')'
    # Change color type to include transparency
    col_out = col_out.replace('rgb', 'rgba')

    return col_out


# endregion


# region Grid Map
"""
SET UP GRID MAP
"""

## READ GEOGPRAPHICAL DATA
# Set url to geojson
url = 'https://raw.githubusercontent.com/MartinJHallberg/DMI_Wind_DashApp/version2/assets/DKN_10KM_epsg4326_filtered_wCent.geojson'
geoj_grid = json.loads(requests.get(url).text)

shp_grid = pd.json_normalize(geoj_grid['features'])

print(shp_grid.columns)
shp_grid.rename(columns={'properties.KN10kmDK': 'KN10kmDK',
                         'properties.Stednavn': 'Stednavn',
                         'properties.cent_lon': 'cent_lon',
                         'properties.cent_lat': 'cent_lat'}, inplace=True)

# Rename None to 'No name'
shp_grid['Stednavn'].fillna('No name', inplace=True)

## SET UP FIGURE
# Map center
dict_cent = {'lon': 10.52,
             'lat': 55.89
             }

# Color columns
shp_grid['Val'] = 1
shp_grid['Col'] = fun_col_to_trans(dict_layout_cols['primary'], 0.4)

# Hover columns
hover_data_map = np.stack(
    (shp_grid['Stednavn'],
     shp_grid['cent_lon'],
     shp_grid['cent_lat']), axis=1)

# Figure
fig_map = go.Figure(
    go.Choroplethmapbox(
        geojson=geoj_grid,
        featureidkey="properties.KN10kmDK",
        locations=shp_grid['KN10kmDK'],
        z=shp_grid['Val'],
        colorscale=shp_grid['Col'],
        showscale=False,
        customdata=hover_data_map,
        hovertemplate='%{customdata[0]}<extra></extra>',
        colorbar={'outlinecolor': dict_layout_cols['primary']}
    ),
    layout=go.Layout(
        mapbox=dict(
            accesstoken=mapbox_api,
            center=dict_cent,
            zoom=6.75,
            style="dark"
        ),
        autosize=True,
        # width=1000,
        # height=700,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        clickmode='event+select'
    )
)

# Update layout
# fig_map.update_layout(
#     mapbox_style = "white-bg", #Decide a style for the map
#     mapbox_zoom = 7, #Zoom in scale
#     mapbox_center = dict_cent)

fig_map.update_traces(marker_line_width=0.01,
                      marker_line_color = fun_col_to_trans(dict_layout_cols['primary'],0.1))

# fig_map.show()
# endregion


# region Wind Rose
"""
SET UP WIND ROSE
"""

## CREATE DIRECTIONS DATA FRAME
# Create bins
# Create bins
bins = np.arange(start=0, stop=360, step=22.5)
# Create list of directions
dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

# Create data frame
df_wind_dir_col = pd.DataFrame({'Direction': dirs,
                                'Degree': bins,
                                'Radius': np.repeat(100, len(dirs))
                                }
                               )
# Calculate coordinates for angles
df_wind_dir_col['Y_cord'] = -round(np.cos(np.deg2rad(df_wind_dir_col['Degree'])), 2) * 12
df_wind_dir_col['X_cord'] = round(np.sin(np.deg2rad(df_wind_dir_col['Degree'])), 2) * 12
dict_dir_coord = df_wind_dir_col[['Direction', 'X_cord', 'Y_cord']].set_index('Direction').to_dict('index')


## CREATE FUNCTION TO CONVERT DEGREES TO CARDINAL DIRECTIONS
def fun_DegToCard(d):
    card = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    ix = round(d / (360. / len(card)))
    card_text = card[ix % len(card)]
    return card_text


## DEFINE COLOR PALETTE
blues = n_colors('rgb(39, 18, 228)', 'rgb(68, 196, 228)', n_colors=4, colortype='rgb')
greens = n_colors('rgb(6, 121, 37)', 'rgb(129, 233, 49)', n_colors=4, colortype='rgb')
yellow = n_colors('rgb(218, 233, 10)', 'rgb(233, 166, 10)', n_colors=4, colortype='rgb')
reds = n_colors('rba(246, 105, 35)', 'rba(179, 0, 0)', n_colors=4, colortype='rgb')

l_wind_bins = [0, 3, 6, 9, 12, 15, 100]
l_wind_bins_labels = ['0-3', '3-6', '6-9', '9-12', '12-15', '+15']

blues = ["rgb(30,62,92)", "rgb(93,165,234)", "rgb(26,117,205)", "rgb(165,205,243)", "rgb(201,225,248)",
         "rgb(237,245,252)"]

dict_col_blues = dict(zip(l_wind_bins_labels, blues))

# Append colors
cols = blues + greens + yellow + reds

cols_trans = []

for col in cols:
    cols_trans.append(fun_col_to_trans(col, 0.8))

# Create dict with directions and colors
col_pal = dict(zip(dirs, cols))
col_pal_trans = dict(zip(dirs, cols_trans))

# Create column with color for directions
cols_wind = df_wind_dir_col['Direction'].map(col_pal)
cols_wind_trans = df_wind_dir_col['Direction'].map(col_pal_trans)


# App layout
app.layout = dbc.Container([

    dbc.Row([

        dbc.Col([

            dbc.Card([

                dbc.CardBody([
                    html.Div([
                        dbc.Button('About',
                                   id='modal-button',
                                   n_clicks=0, ),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(dbc.ModalTitle('DMIWindApp')),
                                dbc.ModalBody([
                                    html.Div([
                                        html.Div(
                                            'Previous data is collected from DMI API:'
                                        ),
                                        html.A('DMI', href='https://confluence.govcloud.dk/display/FDAPI',
                                               target='_blank',
                                               style={'color': 'white'}),
                                        html.Br(),
                                        html.Br(),
                                        html.Div(
                                            'Forecast data is collected from FCOO API:'
                                        ),
                                        html.A('FCOO', href='https://www.fmi.dk/da/forsvarets-center-for-operativ-oceanografi/prognosedata/',
                                               target='_blank',
                                               style={'color': 'white'}),
                                        html.Br(),
                                        html.Br(),
                                        html.Div('Source code can be found on GitHub:'),
                                        html.A('GitHub', href='https://github.com/martinjhallberg/DMI_Wind_DashApp',
                                               target='_blank',
                                               style={'color': 'white'}),
                                        html.Br(),
                                        html.Br(),
                                        html.Div('Life advice can be sent to'),
                                        html.Div('martinjhallberg@gmail.com')

                                        # dbc.ModalBody('Source code')

                                    ])

                                ]
                                ),

                            ],
                            id='modal',
                            is_open=False,
                        ),
                    ],
                        #    style={'width': '85%'}
                    ),

                    # html.H2(
                    #     'Surfcast',
                    #     className='card-title'
                    # ),
                    html.A(
                        html.Img(src=app.get_asset_url('dash-new-logo.png'),
                                 style={'height': '40px',
                                        'float': 'right'}
                                 ),
                        href="https://plotly.com/dash/",
                        style={'width': '100%',

                               }
                    ),
                ],
                    style={
                        'display': 'flex',
                    }
                )
            ], outline=True,
                color='primary',
                style={'background': dict_layout_cols['transparent'],
                       'border-width': 'medium'}
            )

        ], width={"size": 8, "offset": 0}
        )

    ], justify="center"
    ),

    dbc.Row([

        dbc.Col([
            dcc.Graph(id='map_figure', figure=fig_map,
                      config={
                          'displayModeBar': False},
                      style={  # 'width': '80vw',
                          'height': '60vh',
                      }),
        ], width={"size": 8, "offset": 0},

        )

    ], justify="center"
    ),
    html.Br(),
    dbc.Row([
        # dbc.Col([

        # html.Div([

        dbc.Col([

            html.Div([

                html.Div(
                    dbc.Button(
                        'Forecast (FCOO)',
                        id='forc-button',
                        # color=dict_layout_cols['bg_blue2'],
                        n_clicks=0,
                        size='me',
                        style={'background-color': dict_layout_cols['orange'],
                               'border-color': dict_layout_cols['orange'],

                               }
                    ),
                    style={'width': '33.3%',
                           'justify-content': 'center',
                           # 'align-items':'center',
                           'display': 'flex'}
                ),
                html.Div([
                    html.Div(
                        dbc.Button(
                            'Previous day (1)',
                            id='prev-button',
                            color='primary',
                            n_clicks=0,
                            size='me',
                        ),
                    ),
                    html.Div(
                    ),

                ], style={'width': '33.3%',
                          'justify-content': 'center',
                          'align-items': 'center',
                          'display': 'flex',
                          }
                )
                ,

                html.Div([
                    # dbc.Col([
                    html.Div(
                        dbc.Button(
                            'Previous day (2)',
                            id='prev-button-2',
                            color='primary',
                            n_clicks=0,
                            size='me',
                        ),
                    ),


                    html.Div(
                    ),
                ], style={'width': '33.3%',
                          'justify-content': 'center',
                          'align-items': 'center',
                          'display': 'flex'}
                ),
            ], style={'display': 'flex',
                      'justify-content': 'center',
                      'align-items': 'center'}
            ),
        ], width={"size": 8, "offset": 0}
        ),


    ], className='g-0',
        justify="center",
        style = {'margin-bottom':'10px'},
    ),
    dbc.Row([

        dbc.Col([

            html.Div([

                html.Div(

                    style={'width': '33.3%',
                           'justify-content': 'center',
                           # 'align-items':'center',
                           'display': 'flex'}
                ),
                html.Div([

                    html.Div(
                        dcc.DatePickerSingle(
                            id='date_picker',
                            min_date_allowed=date(2019, 1, 1),
                            max_date_allowed=date.today(),
                            date=date.today() - dt.timedelta(days=1),
                            display_format='YYYY-MM-DD'
                        ),
                    ),

                ], style={'width': '33.3%',
                          'justify-content': 'center',
                          'align-items': 'center',
                          'display': 'flex'}
                )
                ,

                html.Div([

                    html.Div(
                        dcc.DatePickerSingle(
                            id='date_picker_prev',
                            min_date_allowed=date(2019, 1, 1),
                            max_date_allowed=date.today(),
                            date=date.today() - dt.timedelta(days=1),
                            display_format='YYYY-MM-DD'
                        ),
                    ),
                ], style={'width': '33.3%',
                          'justify-content': 'center',
                          'align-items': 'center',
                          'display': 'flex'}
                ),
            ], style={'display': 'flex',
                      'justify-content': 'center',
                      'align-items': 'center'}
            ),
        ], width={"size": 8, "offset": 0},
        ),

    ], className='g-0',
        justify="center"
    ),

    html.Br(),
    dbc.Row([
        dbc.Col([

            html.H3(
                id='area_headline',
                style={'color': dict_layout_cols['white'],
                       'textAlign': 'center',
                       # 'margin-left': 'auto',
                       # 'margin-right': 'auto'
                       }
            ),
        ], width={"size": 8, "offset": 0}
        )
    ], justify="center"
    ),

    dbc.Row([
        dbc.Col([

            dbc.Collapse(
                dcc.Loading(
                    id='loading-2',
                    type='default',
                    color=dict_layout_cols['orange'],
                    children=[

                        html.Div([
                            dcc.Graph(
                                id='bar_chart_fcoo', figure={},
                                config={
                                    'displayModeBar': False},
                                style={'height': '70vh',
                                       'width': '100%',
                                       "display": "block",
                                       "margin-left": "auto",
                                       "margin-right": "auto",
                                       },
                            ),
                        ],style = {
                            "display": "block",
                            "margin-left": "auto",
                            "margin-right": "auto",
                        }
                        ),
                    ]),
                id='forc-collapse',
                is_open=True,
                style={'backgroundColor': fun_col_to_trans(dict_layout_cols['orange'], 0.1),
                       'border-color': fun_col_to_trans(dict_layout_cols['orange'], 0.5),
                       'border-style': 'solid'
                       #
                       }
            ),

            dbc.Collapse(
                dcc.Loading(
                    id='loading-1',
                    type='default',
                    color=dict_layout_cols['primary'],
                    children=[

                        html.Div([
                            dcc.Graph(
                                id='bar_chart', figure={},
                                config={
                                    'displayModeBar': False},
                                style={'height': '45vh',
                                       'width': '100%',
                                       "display": "block",
                                       "margin-left": "auto",
                                       "margin-right": "auto",
                                       },
                            ),
                        ],style = {
                            "display": "block",
                            "margin-left": "auto",
                            "margin-right": "auto",
                        }
                        ),
                    ], ),
                id='prev-collapse',
                is_open=True,
                style={'backgroundColor': fun_col_to_trans(dict_layout_cols['primary'], 0.1),
                       'border-color': fun_col_to_trans(dict_layout_cols['primary'], 0.5),
                       'border-style': 'solid'
                       #
                       }
            ),

            dbc.Collapse(
                dcc.Loading(
                    id='loading-3',
                    type='default',
                    color=dict_layout_cols['primary'],
                    children=[

                        html.Div([
                            dcc.Graph(
                                id='bar_chart_2', figure={},
                                config={
                                    'displayModeBar': False},
                                style={'height': '45vh',
                                       'width': '100%',
                                       "display": "block",
                                       "margin-left": "auto",
                                       "margin-right": "auto",
                                       },
                            ),
                        ]),
                    ]),
                id='prev-collapse-2',
                is_open=False,
                style={'backgroundColor': fun_col_to_trans(dict_layout_cols['primary'], 0.1),
                       'border-color': fun_col_to_trans(dict_layout_cols['primary'], 0.5),
                       'border-style': 'solid'
                       #
                       }
            ),

        ], width={"size": 8, "offset": 2},

        ),

    ])
],
)


#region CALLBACKS

# Figure 1 callback
@app.callback(
    # Output('output_date_picker', 'children'),
    Output('bar_chart', 'figure'),
    # Output('bar_chart_2', 'figure'),
    # Output('bar_chart_3', 'figure'),
    Output('area_headline', 'children'),
    Input('date_picker', 'date'),
    Input('map_figure', 'clickData'),
)
# region DMI CALLBACKS
def update_chart_1(date_value, clk_data):
    # Input data
    date_object = date.fromisoformat(date_value)
    date_string = date_object.strftime('%Y-%m-%d')
    date_to_str = date_string

    # Initialize default chart
    if clk_data is None:
        # print('empty')
        # Get DMI data
        cellid = '10km_622_71'
        cellname = shp_grid.loc[shp_grid['KN10kmDK'] == cellid, 'Stednavn'].values[0]
        # cell_lon = clk_data['points'][0]['customdata'][1]
        # cell_lat = clk_data['points'][0]['customdata'][2]

        # Get DMI data
        df, date_from_str = fun_get_filter_dmi_data(
            date_to_str=date_to_str
            , cellid=cellid)

        print('Waves at {} - {}'.format(date_from_str[0:10], date_to_str))

        # Create figure
        fig_out = fun_wind_bar_chart(
            df=df,
            mag_col='mean_wind_speed',
            dir_col='mean_wind_dir',
            dt_col='from_datetime',
            date_from_str=date_from_str,
            date_to_str=date_to_str
        )

        # fig_dmi.show()
        fig_out = fun_max_wind_chart(
            df=df,
            dt_col='from_datetime',
            fig=fig_out
        )

    else:
        # Help prints
        print(f'Click data: {clk_data}')
        cellid = clk_data['points'][0]['location']
        cellname = clk_data['points'][0]['customdata'][0]
        cell_lon = clk_data['points'][0]['customdata'][1]
        cell_lat = clk_data['points'][0]['customdata'][2]

        # Get DMI data
        df, date_from_str = fun_get_filter_dmi_data(
            date_to_str=date_to_str
            , cellid=cellid)

        # print(df)

        # Create figure
        fig_out = fun_wind_bar_chart(
            df=df,
            mag_col='mean_wind_speed',
            dir_col='mean_wind_dir',
            dt_col='from_datetime',
            date_from_str=date_from_str,
            date_to_str=date_to_str
        )

        # fig_dmi.show()
        fig_out = fun_max_wind_chart(
            df=df,
            dt_col='from_datetime',
            fig=fig_out
        )

    string_prefix = 'You have selected: '
    string_suffix = 'Area: '
    string_out = string_prefix + date_string + string_suffix + cellname + ' CellID: ' + cellid

    # print(string_out)
    # return string_out,\

    return fig_out, cellname
    # return fig_out, cellname


# Figure 2 callback
@app.callback(
    Output('bar_chart_2', 'figure'),
    Input('date_picker_prev', 'date'),
    Input('map_figure', 'clickData'),
)
def update_chart_2(date_value, clk_data):
    # Input data
    date_object = date.fromisoformat(date_value)
    date_string = date_object.strftime('%Y-%m-%d')
    date_to_str = date_string

    # Initialize default chart
    if clk_data is None:
        # print('empty')
        # Get DMI data
        cellid = '10km_622_71'
        cellname = shp_grid.loc[shp_grid['KN10kmDK'] == cellid, 'Stednavn'].values[0]
        # cell_lon = clk_data['points'][0]['customdata'][1]
        # cell_lat = clk_data['points'][0]['customdata'][2]
        # print(cellid)

        # Get DMI data
        df, date_from_str = fun_get_filter_dmi_data(
            date_to_str=date_to_str
            , cellid=cellid)

        # Create figure
        # Create figure
        fig_out = fun_wind_bar_chart(
            df=df,
            mag_col='mean_wind_speed',
            dir_col='mean_wind_dir',
            dt_col='from_datetime',
            date_from_str=date_from_str,
            date_to_str=date_to_str
        )

        # fig_dmi.show()
        fig_out = fun_max_wind_chart(
            df=df,
            dt_col='from_datetime',
            fig=fig_out
        )

    else:
        # Help prints
        print(f'Click data: {clk_data}')
        cellid = clk_data['points'][0]['location']
        cellname = clk_data['points'][0]['customdata'][0]
        cell_lon = clk_data['points'][0]['customdata'][1]
        cell_lat = clk_data['points'][0]['customdata'][2]

        # Get DMI data
        df, date_from_str = fun_get_filter_dmi_data(
            date_to_str=date_to_str
            , cellid=cellid)

        # print(df)

        # Create figure
        fig_out = fun_wind_bar_chart(
            df=df,
            mag_col='mean_wind_speed',
            dir_col='mean_wind_dir',
            dt_col='from_datetime',
            date_from_str=date_from_str,
            date_to_str=date_to_str
        )

        # fig_dmi.show()
        fig_out = fun_max_wind_chart(
            df=df,
            dt_col='from_datetime',
            fig=fig_out
        )

    string_prefix = 'You have selected: '
    string_suffix = 'Area: '
    string_out = string_prefix + date_string + string_suffix + cellname + ' CellID: ' + cellid

    # print(string_out)
    # return string_out,\

    return fig_out
    # return fig_out, cellname


# endregion

#region FCOO CALLBACK
@app.callback(
    Output('bar_chart_fcoo', 'figure'),
    # Output('bar_chart_wave', 'figure'),
    Input('map_figure', 'clickData'),
)
def update_chart_3(clk_data):
    # Initialize default chart

    if clk_data is None:

        # Get data
        cellid = '10km_622_71'
        dict_fcoo = shp_grid[['KN10kmDK', 'cent_lat', 'cent_lon']].set_index('KN10kmDK').to_dict(orient='index')

        lat = dict_fcoo[cellid]['cent_lat']
        lon = dict_fcoo[cellid]['cent_lon']
        print(lat)
        print(lon)
        # Get DMI data

        df_fcoo = fun_append_fcoo_dfs(lat=lat, lon=lon)

        fun_vec_to_dir_mag(df_fcoo, 'UGRD', 'VGRD', 'Wind', 'Speed')

        fun_vec_to_dir_mag(df_fcoo, 'u', 'v', 'Wave', 'Height')

        # Create figure
        fig_wind_fcoo = fun_wind_bar_chart(
            df=df_fcoo,
            mag_col='WindSpeed',
            dir_col='WindDir',
            dt_col='Time_dt',
            date_from_str='',
            date_to_str='',
        )

        fig_wind_fcoo.set_subplots(2, 1,
                                   horizontal_spacing=1,
                                   # vertical_spacing=0.9,
                                   specs=[
                                       [{"secondary_y": False}],
                                       [{"secondary_y": True}]])

        fig_out = fun_wave_chart(
            df=df_fcoo,
            mag_col='WaveHeight',
            dir_col='WaveDir',
            dt_col='Time_dt',
            fig=fig_wind_fcoo
        )

    else:
        cell_lon = clk_data['points'][0]['customdata'][1]
        cell_lat = clk_data['points'][0]['customdata'][2]
        # print(cellid)

        df_fcoo = fun_append_fcoo_dfs(lat=cell_lat, lon=cell_lon)

        fun_vec_to_dir_mag(df_fcoo, 'UGRD', 'VGRD', 'Wind', 'Speed')

        fun_vec_to_dir_mag(df_fcoo, 'u', 'v', 'Wave', 'Height')

        # Create figure
        fig_wind_fcoo = fun_wind_bar_chart(
            df=df_fcoo,
            mag_col='WindSpeed',
            dir_col='WindDir',
            dt_col='Time_dt',
            date_from_str='',
            date_to_str='',
        )

        fig_wind_fcoo.set_subplots(2, 1,
                                   horizontal_spacing=1,
                                   # vertical_spacing=0.9,
                                   specs=[
                                       [{"secondary_y": False}],
                                       [{"secondary_y": True}]])

        fig_out = fun_wave_chart(
            df=df_fcoo,
            mag_col='WaveHeight',
            dir_col='WaveDir',
            dt_col='Time_dt',
            fig=fig_wind_fcoo
        )

    return fig_out


# region


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


# Backcast collaps callback
@app.callback(
    Output("prev-collapse", "is_open"),
    Input('prev-button', "n_clicks"),
    [State("prev-collapse", "is_open")],
)
def toggle_modal(c1, is_open):
    if c1:
        return not is_open
    return is_open


@app.callback(
    Output("prev-collapse-2", "is_open"),
    Input('prev-button-2', "n_clicks"),
    [State("prev-collapse-2", "is_open")],
)
def toggle_modal(c1, is_open):
    if c1:
        return not is_open
    return is_open


# Backcast collaps callback
@app.callback(
    Output("forc-collapse", "is_open"),
    Input('forc-button', "n_clicks"),
    [State("forc-collapse", "is_open")],
)
def toggle_modal(c2, is_open):
    if c2:
        return not is_open
    return is_open



#endregion


# region HELPER FUNCTIONS
# region DEFINE FUNCTION FOR GETTING DMI DATA
def fun_get_filter_dmi_data(
        date_to_str,  # the last date for which the data is gotten
        cellid,  # id from grid cell
        obs_values=['mean_wind_speed', 'max_wind_speed_3sec', 'mean_wind_dir'],
        # which observations from DMI data to keep
        no_days=2,  # number of days to get data for
        api_key=dmi_api,  # api key for DMI API
        stationid='',  # extra parameter, if weather station data
        # is used instead of grid data
        limit=10000  # max number of observations to get
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
    # print(req_str)

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


# endregion

# region DEFINE FUNCTION FOR FORECAST DATA (FCOO)
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
    print('Data collected')

    l_cols = list(data[var].keys())

    if len(l_cols) == 1:
        df = pd.DataFrame(
            {var: data[var][l_cols[0]]['data'],
             'Time': data[var][l_cols[0]]['time']
             })
    else:
        df = pd.DataFrame(
            {l_cols[0]: data[var][l_cols[0]]['data'],
             l_cols[1]: data[var][l_cols[1]]['data'],
             'Time': data[var][l_cols[0]]['time']
             })

    # return  pd.json_normalize(data['UGRD'])
    return df


def fun_append_fcoo_dfs(
        lat,
        lon,
        variables=['Wind', 'Sealevel', 'WaveHeight2D', 'WavePeriod']

):
    l_dfs = []

    for i, var in enumerate(variables):

        df = fun_get_fcoo_data(var, lat=lat, lon=lon)

        # print('Data collected for {} collected'.format(var))

        # For first data frame, do nothing, join followingly
        if i == 0:
            dfs = df
        else:
            dfs = dfs.merge(df, on='Time')
        # l_dfs.append(df)
        print('Data frame appended')

    # Creaet date time column
    dfs['Time_dt'] = pd.to_datetime(dfs['Time'])

    # Floor data frame to first hour of day

    return dfs


def fun_vec_to_dir_mag(
        df,
        u_vec,
        v_vec,
        var,
        mag
):
    dir_name = var + 'Dir'
    speed_name = var + mag

    df[dir_name] = round(np.arctan2(df[u_vec], df[v_vec]) * 180 / np.pi + 180, 0)
    df[speed_name] = round(np.sqrt(df[u_vec] ** 2 + df[v_vec] ** 2), 1)

    # return df


# endregion


# region FIGURE FUNCTIONS
# Set colorscale
colorscale = [[0, dict_col_blues['0-3']],
              [0.4, dict_col_blues['6-9']],
              [1, dict_col_blues['+15']]]

# Set axes
y_axes = dict(gridcolor='rgba(255,255,255,0.4)',
              color=dict_layout_cols['white'],
              gridwidth=0.0001,
              showticksuffix='last',
              ticksuffix=' m/s'
              )

x_axes = dict(color=dict_layout_cols['white'],
              linewidth=0.1,
              showgrid=False
              )


# region WIND BAR FUNCTION
def fun_wind_bar_chart(df,  # dataframe to be visualized
                       mag_col,  # column containing magnitude values
                       dir_col,  # column containing direction values
                       dt_col,  # column containing datetime values
                       date_from_str,  # start date for period
                       date_to_str,  # end date for period
                       ):
    # Discetize values in magnitude column
    df['Col_bin'] = pd.cut(df[mag_col], bins=l_wind_bins, labels=l_wind_bins_labels)
    # Create column with cardinal direction
    df['Wind_CardDir'] = df[dir_col].apply(fun_DegToCard)

    # Hover data
    hover_data_chart = np.stack((df[dir_col], df['Wind_CardDir'], df[dt_col].dt.hour.astype(str) + ':00'), axis=1)

    fig_chart = go.Figure()

    fig_chart.add_trace(

        go.Bar(
            x=df[dt_col],
            y=df[mag_col],
            marker=dict(

                color=df[mag_col],
                colorscale=colorscale,
                cmin=0,
                cmax=13,
                # opacity = 0.7,
                line_color=dict_layout_cols['orange'],
                line_width=0
            ),
            customdata=hover_data_chart,
            hovertemplate=
            'Avg. wind: %{y}' +
            '<br>Wind direction: %{customdata[1]} (%{customdata[0]}\xb0)' +
            '<br>Time: %{customdata[2]}<extra></extra>',
            hoverlabel=dict(
                bgcolor='rgba(255,255,255,0.3)',
                font=dict(color='black')
            ),
            showlegend=True,
            name='Avg. wind speed',
            legendrank=2,
        )
    )

    # Assign text variable
    t_fig_type = 'wind'

    arr_dist = 1

    title_text = 'Wind {} - {}'.format(date_from_str[0:10], date_to_str)
    print(title_text)
    # format(date_from_str[0:10], date_to_str),

    y_ax_range = dict(range=[0, 30])
    chart_margin = dict(l=40, r=40, t=20, b=20)

    # Add direction arrows
    for i, row in df.iterrows():
        x_date = row[dt_col]

        ax = dict_dir_coord[row['Wind_CardDir']]['X_cord']
        ay = dict_dir_coord[row['Wind_CardDir']]['Y_cord']

        fig_chart.add_annotation(
            x=x_date,
            y=row[mag_col] + arr_dist,
            ax=ax,
            ay=ay,
            arrowhead=3,
            arrowsize=1.6,
            arrowwidth=1.1,
            arrowcolor=dict_layout_cols['orange'],
            xref="x",
            yref="y"
        )

    fig_chart.update_yaxes(y_axes)

    fig_chart.update_xaxes(x_axes)

    # Set layout
    fig_chart.update_layout(
        bargap=0.5,
        yaxis=y_ax_range,
        autosize=True,
        # width=800,
        # height=h,
        hovermode='x unified',
        hoverlabel=dict(bgcolor=fun_col_to_trans(dict_layout_cols['white'],0.75),
                        font=dict(color='black')
                        ),
        margin=chart_margin,
        plot_bgcolor=dict_layout_cols['transparent'],
        paper_bgcolor=dict_layout_cols['transparent'],
        legend=dict(
            yanchor="top",
            y=1.05,
            xanchor="left",
            x=0.01,
            bgcolor=dict_layout_cols['transparent'],
            font=dict(color=dict_layout_cols['white'])
        ),
        title={'text': title_text,
               'x': 0.5,
               'y': 0.96,
               'font': {'color': dict_layout_cols['white']}
               }
    )

    return fig_chart


# endregion

# region MAX WIND FUNCTION
def fun_max_wind_chart(
        fig,  # base figure
        df,  # dataframe
        dt_col  # datetime column
):
    fig.add_trace(
        go.Scatter(
            x=df[dt_col],
            y=df['max_wind_speed_3sec'],
            hovertemplate=
            'Max wind speed (3s): %{y}<extra></extra>',
            line=dict(
                # opacity = 0.8,
                color="rgb(255,255,255)",  # dict_layout_cols['bg_blue']
                width=2,
                dash='dash'
            ),
            showlegend=True,
            name='Max. wind speed',
            legendrank=1
        )
    )
    return fig


# endfunction

# region WAVE FUNCTION
def fun_wave_chart(
        df,  # dataframe to be visualized
        mag_col,  # column containing magnitude values
        dir_col,  # column containing direction values
        dt_col,  # column containing datetime values
        fig  # figure with subplots
):
    t_fig_type = 'Wave'

    # Hover data
    hover_data_chart = np.stack((df[dir_col], df['Wind_CardDir'], df[dt_col].dt.hour.astype(str) + ':00'), axis=1)


    fig.add_trace(
        go.Scatter(
            x=df[dt_col],
            y=df[mag_col],
            fill='tozeroy',
            line_color=dict_layout_cols['primary'],
            # marker = dict(
            #    color = dict_layout_cols['primary'],
            # ),
            hoverlabel=dict(
                bgcolor='rgba(255,255,255,0.3)',
                font=dict(color='black')
            ),
            showlegend=True,
            legendrank=2,
        ),
        row=2,
        col=1
    )

    fig.update_traces(
        customdata=hover_data_chart,
        hovertemplate='Wave height: %{y}' +
                      '<br>Wave direction: %{customdata[1]} (%{customdata[0]}\xb0)' +
                      '<br>Time: %{customdata[2]}<extra></extra>',
        name='{} height'.format(t_fig_type),
        legendrank=2,
        row=2,
        col=1
    )

    fig.add_trace(
        go.Scatter(x=df[dt_col],
                   y=round(df['WavePeriod'], 1),
                   hovertemplate=
                   'Wave period: %{y}<extra></extra>',
                   line=dict(
                       # opacity = 0.8,
                       color=dict_layout_cols['white'],
                       width=2,
                       dash='dash'
                   ),
                   showlegend=True,
                   name='Wave period',
                   legendrank=1
                   ),
        secondary_y=True,
        row=2,
        col=1
    )

    fig.update_yaxes(title_text="Wave height",
                     secondary_y=False,
                     title_font_size=12,
                     showticksuffix='last',
                     showgrid=True,
                     ticksuffix=' m',
                     range=list([0, 4]),
                     tickmode='linear',
                     tick0=1,
                     dtick=1,
                     gridcolor='rgba(255,255,255,0.4)',
                     color=dict_layout_cols['white'],
                     gridwidth=0.0001,
                     row=2,
                     col=1
                     )
    fig.update_yaxes(title_text="Wave period",
                     secondary_y=True,
                     title_font_size=12,
                     showticksuffix='last',
                     showgrid=False,
                     ticksuffix=' s',
                     range=list([0, 10]),
                     tickmode='linear',
                     tick0=2,
                     dtick=2,
                     gridcolor='rgba(255,255,255,0.4)',
                     color=dict_layout_cols['white'],
                     gridwidth=0.0001,
                     row=2,
                     col=1
                     )

    # fig_chart.show()

    chart_margin = dict(l=10, r=10, t=20, b=20)

    title_text = 'Waves at {} - {}'.format('1', '2')
    # format(date_from_str[0:10], date_to_str),

    y_ax_range = dict(range=[0, 4])

    arr_dist = 0.3

    # Add direction arrows
    for i, row in df.iterrows():
        x_date = row[dt_col]

        ax = dict_dir_coord[row['Wind_CardDir']]['X_cord']
        ay = dict_dir_coord[row['Wind_CardDir']]['Y_cord']

        fig.add_annotation(
            x=x_date,
            y=row[mag_col] + arr_dist,
            ax=ax,
            ay=ay,
            arrowhead=3,
            arrowsize=1.6,
            arrowwidth=1.1,
            arrowcolor=dict_layout_cols['orange'],
            xref="x",
            yref="y",
            row=2,
            col=1
        )

    fig.update_xaxes(x_axes)

    fig.update_layout(
        bargap=0.5,
        # yaxis=y_ax_range,
        autosize=True,
        # width=800,
        # height=h,
        hovermode='x unified',
        hoverlabel=dict(bgcolor='rgba(255,255,255,0.75)',
                        font=dict(color='black')
                        ),
        margin=chart_margin,
        plot_bgcolor=dict_layout_cols['transparent'],
        paper_bgcolor=dict_layout_cols['transparent'],
        legend=dict(
            yanchor="top",
            y=1.05,
            xanchor="left",
            x=0.01,
            bgcolor=dict_layout_cols['transparent'],
            font=dict(color=dict_layout_cols['white'])
        ),
        title={'text':"Forecast",
               'x': 0.5,
               'y': 0.96,
               'font': {'color': dict_layout_cols['white']}
               },
        # row = 2,
        # col = 1
    )

    return fig


# endregion

# endregion

# endregion

#endregion

if __name__ == '__main__':
    app.run_server(debug=True)
