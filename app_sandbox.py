import plotly.graph_objects as go
from dash import dcc, html, Dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash.dependencies import Input, Output, State
from datetime import date
from plotly.subplots import make_subplots
from dotenv import load_dotenv
from app_helper_functions import get_map
import os
import pandas as pd
import app_graph_functions as graphs
import datetime as dt

app = Dash(
    external_stylesheets=[dbc.themes.MORPH],
    prevent_initial_callbacks=True
)
load_figure_template("MORPH")

######## READ BASE DATA ######################
mapbox_api = os.getenv("mapbox_key")


dmi_obs = pd.read_csv("data/parse_data_test.csv", usecols=[
    "cellId", "from", "parameterId", "value"
])

##############################################


######## SET UP DASH COMPONENTS

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

# OBSERVATIONAL CHART
chart_dmi_obs = graphs.create_dmi_obs_chart(
    dmi_obs,
    "10km_622_71",
    "2023-01-02",
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
            min_date_allowed=date(2019, 1, 1),
            max_date_allowed=date.today(),
            first_day_of_week=1,
            date=date(2023, 1, 2),
            display_format='YYYY-MM-DD'
            ),
        width="auto"
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
            chart_obs_app,
            justify="center",
            ),
    ]
)
#########################################################


############ CALLBAKCKS #################################
@app.callback(
    Output('chart_obs', 'figure'),
    Input('map_figure', 'clickData'),
    Input('date_picker', 'date')
)

def update_dmi_obs_chart(click_data, date):

    print(date)

    cell_id = click_data["points"][0]["location"]

    chart = graphs.create_dmi_obs_chart(
        dmi_obs,
        cell_id,
        date,
    )

    return chart

###########################################################

if __name__ == '__main__':
    app.run(debug=True)


