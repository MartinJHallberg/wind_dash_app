from dash import dcc, html, Dash, set_props
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash.dependencies import Input, Output, State
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
    external_stylesheets=[dbc.themes.MORPH],
    prevent_initial_callbacks=True
)
load_figure_template("MORPH")

start_cell_id="10km_622_71"
start_date="2023-01-02"

######## READ BASE DATA ######################
mapbox_api = os.getenv("mapbox_key")


dmi_obs_data = pd.read_csv("data/parse_data_test.csv", usecols=[
    "cellId", "from", "parameterId", "value"
])

dmi_forecast_data = pd.read_csv("data/wind_forecast.csv")
dmi_forecast_data = parse_dmi_forecast_data_wind(dmi_forecast_data)

##############################################


######## SET UP DASH COMPONENTS ##############

# HEADER
header_app = dbc.Col(
    html.H1("Header"),
    style={
        "background-color" : "#2196f3",
    }
)

# MAP
fig_map = graphs.create_map_chart(mapbox_api)

map_app = dbc.Col(
    [
        dcc.Graph(
            id='map_figure',
            figure=fig_map,
            config={
                'displayModeBar': False},
            style={
                'height': '50vh',
                }
            ),
    ],
    width=8,
)

# FORECAST CHART
chart_dmi_forecast = graphs.create_forecast_chart_wind(
    dmi_forecast_data,
    start_cell_id
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

# FORECAST W/ OBSERVATIONAL CHART
chart_dmi_forecast_w_obs = graphs.add_obs_data_to_forecast_chart(
    chart_dmi_forecast,
    dmi_forecast_data,
    "wind_speed",
    "timestamp"
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

toggle_switch_column = dbc.Col(
    [
        daq.ToggleSwitch(
            id='toggle-observational-data',
            value=False,
            color="blue"
        ),
        html.Div(id='toggle-switch-result'),
        html.Div(id="error-no-obs-date")        
    ],
    width=2
)

#toggle_switch_column = dbc.Col(html.Div("One of three columns"), width=3),

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
            id='date_picker',
            min_date_allowed=dt.date(2019, 1, 1),
            max_date_allowed=dt.date.today(),
            first_day_of_week=1,
            #date=dt.date.fromisoformat(start_date),
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
app.layout = html.Div(
    [
        dbc.Row(
            header_app,
            justify="center",
        ),

        dbc.Row(
            map_app,
            justify="center",

        ),

        dbc.Row(
            date_picker_app,
            justify="center",

        ),

        dbc.Row(
            chart_forecast_app,
            justify="center",
            ),
        
        dbc.Row(
            [
                chart_forecast_w_obs_app,
                toggle_switch_column,
            ],
            justify="center",
            ),

        dbc.Row(
            chart_obs_app,
            justify="center",
            ),
        
        dbc.Row(
            text_app,
            justify="center",
            ),
    ]
)
#########################################################


############ CALLBAKCKS #################################

@app.callback(
    Output('chart_forecast', 'figure'),
    Input('map_figure', 'clickData'),
)

def update_dmi_forecast_data(click_data):

    if click_data is None:
        cell_id = start_cell_id
    
    else:
        cell_id = click_data["points"][0]["location"]

    chart = graphs.create_forecast_chart_wind(dmi_forecast_data, cell_id)

    return chart

@app.callback(
    Output("chart_forecast_w_obs", 'figure'),
    Output("error-no-obs-date", 'children'),
    Input('toggle-observational-data', 'value'),
    Input('map_figure', 'clickData'),
    Input('date_picker', 'date')
)

def update_dmi_forecast_data_with_obs(toggle, click_data, date): # date is to be added as input here

    if click_data is None:
        cell_id = start_cell_id
    
    else:
        cell_id = click_data["points"][0]["location"]

    chart = graphs.create_forecast_chart_wind(dmi_forecast_data, cell_id)

    if toggle:
        if date:
            df = dmi_forecast_data.copy() # should be removed
            df["wind_speed"] = df["wind_speed"]*0.5 # should be removed
            chart = graphs.add_obs_data_to_forecast_chart(
                chart,
                df,
                "wind_speed",
                "timestamp"
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


