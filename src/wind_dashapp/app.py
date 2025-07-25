from dash import dcc, html, Dash, set_props
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash.dependencies import Input, Output
import dash_mantine_components as dmc
import os
from wind_dashapp.helper_functions import app_graph_functions as graphs
import datetime as dt
from dotenv import load_dotenv

from wind_dashapp.helper_functions.app_helper_functions import (
    load_wind_obs_data_to_app,
    load_wind_forecast_data_to_app,
    DEFAULT_NUMBER_OF_HOURS_FETCH,
)

load_dotenv()

DMI_API_KEY_OBSERVATION = os.getenv("DMI_API_KEY_OBSERVATION")
DMI_API_KEY_FORECAST = os.getenv("DMI_API_KEY_FORECAST")
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA")


######## INITIALIZE APP ####################
def custom_error_handler(err):
    set_props(
        "error-no-obs-date",
        dict(children="No date for observational data has been chosen."),
    )


app = Dash(prevent_initial_callbacks=True)

load_figure_template("MORPH")

start_cell_id = "10km_622_71"
start_lon = 12.374
start_lat = 56.078
start_date = "2023-01-02"

######## READ BASE DATA ######################
wind_obs_data = load_wind_obs_data_to_app(
    DMI_API_KEY_OBSERVATION, start_cell_id, start_date, use_mock_data=USE_MOCK_DATA
)

wind_forecast_data = load_wind_forecast_data_to_app(
    DMI_API_KEY_FORECAST, start_lon, start_lat, "wind", use_mock_data=USE_MOCK_DATA
)

######## CREATE INITIAL FIGURES ##############
# Map
fig_map = graphs.create_map_chart()

# Forecast chart
chart_dmi_forecast = graphs.create_forecast_chart(
    forecast_data=wind_forecast_data,
    col_wind_speed="wind_speed",
    col_wind_max_speed="gust_wind_speed_10m",
    col_wind_direction="wind_dir",
    col_datetime="from_datetime",
    cell_id=start_cell_id,
)

######## SET UP DASH COMPONENTS ##############

# HEADER
header_app = dbc.Col(
    html.H1(children=["Header"], className="page-header"),
)

sidebar = html.Div(
    [
        dbc.Row(
            [
                # html.Img(src="assets/logos/amazon.svg", style={"height": "35px"})
            ],
            className="sidebar-logo",
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Page 1", href="/page_1", active="exact"),
                dbc.NavLink(
                    "Page 2",
                    href="/page_2",
                    active="exact",
                ),
                dbc.NavLink("Page 3", href="/page_3", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
        html.Div(
            [
                html.Br(),
            ],
            className="subtitle-sidebar",
            style={"position": "absolute", "bottom": "10px", "width": "100%"},
        ),
    ],
    className="sidebar",
)

map_card = dbc.Card(
    dcc.Graph(
        id="map_figure",
        figure=fig_map,
        config={"displayModeBar": False},
        style={
            "height": "50vh",
        },
    ),
    class_name="card",
)

right_cards = (
    html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            "Area",
                        ),
                        html.H5(
                            id="area_name_card",
                            children="Gilleleje",
                        ),
                    ],
                    class_name="card-body",
                ),
                class_name="card bg-light mb-3",
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            "Wind speed",
                        ),
                        html.H5(id="wind_speed_card", children="7 m/s"),
                    ]
                ),
                class_name="card bg-light mb-3",
            ),
        ],
    ),
)

fig_corecast_control_panel = dmc.SimpleGrid(
    cols=3,
    spacing="md",
    children=[
        dmc.Stack(
            [
                html.H6("Forecast hours"),
                dmc.Slider(
                    id="range_slider_forecast",
                    min=0,
                    max=DEFAULT_NUMBER_OF_HOURS_FETCH,
                    value=DEFAULT_NUMBER_OF_HOURS_FETCH,
                    labelTransitionProps={"transition": "skew-down", "duration": 150, "timingFunction": "linear"},
                ),
            ],
        ),
        dmc.Stack(
            [
                dmc.Switch(
                    id="toggle-observational-data",
                    checked=False,
                )
            ]
        ),
    ],
)

fig_forecast_w_obs = dbc.Card(
    [
        html.Div(
            [
                fig_corecast_control_panel,
                dcc.Graph(
                    id="chart_forecast",
                    figure=chart_dmi_forecast,
                    style={
                        "margin": "1rem",
                    },
                ),
            ],
        )
    ],
    class_name="card",
)

control_fig_forecast = html.Div(children=[])

card_control_fig_corecast = dbc.Card(
    [
        html.Div(
            [
                html.H6(
                    "Compare forecast with previous date",
                    style={"margin-top": "0.5rem"},
                ),
                # dmc.Switch(
                #    id="toggle-observational-data",
                #     checked=False,
                #    # color="rgba(41, 96, 214, 1)",
                #    style={"display": "inline-block"},
                # ),
            ],
            className="toggle-control-header",
        ),
        dbc.CardBody(
            [
                html.Div(
                    id="control_fig_forecast",
                    children=[
                        html.Div(id="toggle-switch-result"),
                        html.Div(id="error-no-obs-date"),
                        dmc.Select(
                            # label="Select previous session",
                            data=["Session1", "Session2"],
                            searchable=True,
                            # checkIconPosition="right",
                        ),
                        dcc.DatePickerSingle(
                            id="date_picker",
                            min_date_allowed=dt.date(2019, 1, 1),
                            max_date_allowed=dt.date.today(),
                            first_day_of_week=1,
                            # date=dt.date.fromisoformat(start_date),
                            display_format="YYYY-MM-DD",
                        ),
                    ],
                    style={"display": "none"},
                )
            ],
            class_name="card-body",
        ),
    ],
    class_name="card bg-light mb-3",
)

########### APP LAYOUT ##############################
page_content = dbc.Container(
    html.Div(
        [
            html.H1("Header"),
            dbc.Row([dbc.Col(map_card, md=9), dbc.Col(right_cards, md=2)]),
            dbc.Row(
                [
                    dbc.Col(fig_forecast_w_obs, md=9),
                    dbc.Col(card_control_fig_corecast, md=2),
                ]
            ),
        ],
        className="content",
    ),
    fluid=True,
)

app.layout = dmc.MantineProvider(
    [
        html.Div(
            [
                sidebar,
                page_content,
            ],
            className="main-div",
        )
    ]
)


############ CALLBAKCKS ################
@app.callback(
    Output("control_fig_forecast", "style"),
    Input("toggle-observational-data", "checked"),
)
def show_forecast_control(toggle):
    if toggle:
        return {"display": "block"}

    else:
        return {"display": "none"}


@app.callback(
    Output("area_name_card", "children"),
    Input("map_figure", "clickData"),
)
def update_area_name(click_data):
    if click_data is None:
        return "Gilleleje"

    else:
        return click_data["points"][0]["customdata"][0]


@app.callback(
    Output("chart_forecast", "figure"),
    Output("error-no-obs-date", "children"),
    Input("toggle-observational-data", "checked"),
    Input("map_figure", "clickData"),
    Input("date_picker", "date"),
    Input("range_slider_forecast", "value"),
)
def update_wind_forecast_data_with_obs(toggle, click_data, date, forecast_hours):
    if click_data is None:
        cell_id = start_cell_id
        lon = start_lon
        lat = start_lat

    else:
        cell_id = click_data["points"][0]["location"]

        lon = click_data["points"][0]["customdata"][1]
        lat = click_data["points"][0]["customdata"][2]

    wind_forecast_data_from_click = load_wind_forecast_data_to_app(
        DMI_API_KEY_FORECAST, lon, lat, "wind", use_mock_data=USE_MOCK_DATA, n_hours=forecast_hours
    )

    chart = graphs.create_forecast_chart(
        forecast_data=wind_forecast_data_from_click,
        col_wind_speed="wind_speed",
        col_wind_max_speed="gust_wind_speed_10m",
        col_wind_direction="wind_dir",
        col_datetime="from_datetime",
        cell_id=start_cell_id,
    )

    if toggle:
        if date:
            wind_obs_data_from_click = load_wind_obs_data_to_app(
                DMI_API_KEY_OBSERVATION, cell_id, date, use_mock_data=USE_MOCK_DATA
            )

            chart = graphs.add_obs_data_to_forecast_chart(
                forecast_chart=chart,
                obs_data=wind_obs_data_from_click,
                col_wind_speed="mean_wind_speed",
                col_wind_max_speed="max_wind_speed_3sec",
                col_wind_direction="mean_wind_dir",
                col_datetime="from_datetime",
                cell_id=cell_id,
                obs_date=date,
            )
            return chart, "Observational data is shown"
        else:
            return chart, "No date given for observational data"

    return chart, "Toggle off"


@app.callback(
    Output("toggle-switch-result", "children"),
    Input("toggle-observational-data", "value"),
)
def update_output(value):
    return f"The switch is {value}."


###########################################################

if __name__ == "__main__":
    app.run(debug=True)
