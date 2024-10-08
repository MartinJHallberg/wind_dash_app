from dash import dcc, html, Dash, set_props
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash.dependencies import Input, Output, State
import dash_mantine_components as dmc
from plotly.subplots import make_subplots
from dotenv import load_dotenv
from app_helper_functions import get_map
import os
import pandas as pd
import app_graph_functions as graphs
from app_helper_functions import parse_dmi_forecast_data_wind
import datetime as dt
import dash_daq as daq



######## INITIALIZE APP ####################
def custom_error_handler(err):
    set_props(
        "error-no-obs-date",
        dict(children="No date for observational data has been chosen.")
    )


app = Dash(
    prevent_initial_callbacks=True
)

load_figure_template("MORPH")

start_cell_id="10km_622_71"
start_date="2023-01-02"

######## READ BASE DATA ######################
dmi_obs_data = pd.read_csv(
    "data/parse_data_test.csv", 
    usecols=["cellId", "from", "parameterId", "value"],
    nrows=200000
    )

dmi_forecast_data = pd.read_csv("data/wind_forecast.csv")
dmi_forecast_data = parse_dmi_forecast_data_wind(dmi_forecast_data)

##############################################


######## SET UP DASH COMPONENTS ##############

# HEADER
header_app = dbc.Col(
    html.H1(
        children=["Header"],
        className="page-header"
    ),
)

navbar_app = dbc.Card([
        dbc.CardBody([
            html.H2(id="navigation_bar_header", children="Card header")
        ])
    ],
    class_name="card",
    style={
        "height": "100vh",
        "width": "13rem",
        "position": "fixed",
        "background-color": "blue",
    }
    ),

# FIGURES
# Map
fig_map = graphs.create_map_chart()

# Forecast chart
chart_dmi_forecast = graphs.create_forecast_chart(
        forecast_data=dmi_forecast_data,
        col_wind_speed="wind_speed",
        col_wind_max_speed="gust_wind_speed_10m",
        col_wind_direction="wind_dir",
        col_datetime="timestamp",
        cell_id=start_cell_id
    )

content_header = html.Div([
    html.H1("Surf Wind Analytics")
])

content_top_row = html.Div([
    dbc.Card(
        dcc.Graph(
            id='map_figure',
            figure=fig_map,
            config={
                'displayModeBar': False},
            style={
                'height': '50vh',
            }
        ),
        style={
                "display": "inline-block",
                "width": "70%",
                },
       class_name="card"
    ),
        html.Div([
            dbc.Card(
                dbc.CardBody([
                    html.Div(
                        "Area",
                    ),
                    html.H5(
                        id="area_name_card",
                        children="Gilleleje"
                    )
                ]),
            class_name="card bg-light mb-3",
            ),
            dbc.Card(
                dbc.CardBody([
                    html.Div(
                        "Wind speed",
                    ),
                    html.H5(
                        id="wind_speed_card",
                        children="7 m/s"
                    )
                ]),
            class_name="card bg-light mb-3",
            ),
        ],
        style={
                "display": "inline-block",
                "width": "20%",
                "verticalAlign": "top",
                "justify-content": "right",
            }
        ),
    ],
)

content_bottom_row = html.Div([
        dcc.Graph(
            id="chart_forecast",
            figure=chart_dmi_forecast,
            style={
                "display": "inline-block",
                "width": "80%",
            }
        ),

         html.Div([

            dcc.DatePickerSingle(
                id='date_picker',
                min_date_allowed=dt.date(2019, 1, 1),
                max_date_allowed=dt.date.today(),
                first_day_of_week=1,
                date=dt.date.fromisoformat(start_date),
                display_format='YYYY-MM-DD'
            ),
    
            dmc.Switch(
                #size="lg",
                #radius="sm",
                id='toggle-observational-data',
                label="Show conditions from previous date",
                checked=False
            ),
            html.Div(id='toggle-switch-result'),
            html.Div(id="error-no-obs-date"),
            ],
            style={
                    "display": "inline-block",
                    "width": "20%",
                    "vertical-align":"top",
                }
            ),
])

content = html.Div(
    [
        content_header,
        content_top_row,
        content_bottom_row
    ],
    #width=8,
)



chart_forecast_app = dbc.Col(
    [
        dcc.Graph(
            id="chart_forecast",
            figure=chart_dmi_forecast,
        ),
    ],
    class_name="card",
    width=8
)

chart_forecast_w_obs_app = dbc.Col(
    [
        dcc.Graph(
            id="chart_forecast_w_obs",
            figure=chart_dmi_forecast,
        ),
    ],
    class_name="card",
    width=8
)


# OBSERVATIONAL CHART
chart_dmi_obs = graphs.create_obs_chart(
    dmi_obs_data,
    start_cell_id,
    start_date,
)

chart_obs_app = dbc.Col(
    [
        dcc.Graph(
            id="chart_obs",
            figure=chart_dmi_obs,
        ),
    ],
    class_name="card",
    width=8
)

# DATE PICKER
date_picker_app = dbc.Col(
    dcc.DatePickerSingle(
            id='date_picker_old',
            min_date_allowed=dt.date(2019, 1, 1),
            max_date_allowed=dt.date.today(),
            first_day_of_week=1,
            date=dt.date.fromisoformat(start_date),
            display_format='YYYY-MM-DD'
            ),
    width="auto"
)

text_app = dbc.Col(
    html.Div(
        id="text_output"
    )
)
#####################################################



########### APP LAYOUT ##############################
app.layout = dbc.Container(
    [
        dbc.Row(
            header_app,
            justify="center",
        ),

        dbc.Row([
            dbc.Col(
                navbar_app,
                width=6,
                lg=2,
            ),
            dbc.Col(
                content,
                width={"size":"5"},
                lg=8,
            style={
                "margin-left": "3rem",
            }
            ),
        ],
        justify="start",
        ),
        
        # dbc.Row(
        #     [
        #         chart_forecast_w_obs_app,
        #         date_and_toggle_switch_column,
        #     ],
        #     justify="center",
        #     ),

        # dbc.Row(
        #     chart_obs_app,
        #     justify="center",
        #     ),
        
        dbc.Row(
            text_app,
            justify="center",
            ),
    ],
    fluid=True,
    class_name="container-fluid"
)
#########################################################


############ CALLBAKCKS #################################

# @app.callback(
#     Output('chart_forecast', 'figure'),
#     Input('map_figure', 'clickData'),
# )

# def update_dmi_forecast_data(click_data):

#     if click_data is None:
#         cell_id = start_cell_id
    
#     else:
#         cell_id = click_data["points"][0]["location"]

#     chart = graphs.create_forecast_chart_wind(dmi_forecast_data, cell_id)

#     return chart

@app.callback(
    Output("chart_forecast", 'figure'),
    Output("error-no-obs-date", 'children'),
    Input('toggle-observational-data', 'checked'),
    Input('map_figure', 'clickData'),
    Input('date_picker', 'date')
)

def update_dmi_forecast_data_with_obs(toggle, click_data, date): # date is to be added as input here

    if click_data is None:
        cell_id = start_cell_id
    
    else:
        cell_id = click_data["points"][0]["location"]

    chart = graphs.create_forecast_chart(
            forecast_data=dmi_forecast_data,
            col_wind_speed="wind_speed",
            col_wind_max_speed="gust_wind_speed_10m",
            col_wind_direction="wind_dir",
            col_datetime="timestamp",
            cell_id=start_cell_id
    )

    if toggle:
        if date:
            chart = graphs.add_obs_data_to_forecast_chart(
                forecast_chart=chart,
                obs_data=dmi_obs_data,
                col_wind_speed="mean_wind_speed",
                col_wind_max_speed="max_wind_speed_3sec",
                col_wind_direction="mean_wind_dir",
                col_datetime="from",
                cell_id=cell_id,
                obs_date=date,
                #marker_opacity=0.2
            )
            return chart, "Observational data is shown"
        else:
            return chart, f"No date given for observational data"

    return chart, "Toggle off"

@app.callback(
    Output('toggle-switch-result', 'children'),
    Input('toggle-observational-data', 'value')
)

def update_output(value):
    return f'The switch is {value}.'

@app.callback(
    Output('chart_obs', 'figure'),
    Input('map_figure', 'clickData'),
    Input('date_picker', 'date')
)

def update_dmi_obs_chart(click_data, date):

    print(f"Map click {click_data}")

    if click_data is None:
        cell_id = start_cell_id
    
    else:
        cell_id = click_data["points"][0]["location"]

    chart = graphs.create_obs_chart(
        dmi_obs_data,
        cell_id,
        date,
    )

    return chart


@app.callback(
    Output('text_output', 'children'),
    Input('chart_obs', 'clickData'),
)

def test_chart_click(click_data):

    print(f"Chart click {click_data}")

    return f"Chart click: {click_data}"

###########################################################

if __name__ == '__main__':
    app.run(debug=True)


