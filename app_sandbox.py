import plotly.graph_objects as go
from dash import dcc, html, Dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from datetime import date
from plotly.subplots import make_subplots
from dotenv import load_dotenv
from graph_functions import get_map, filter_dmi_obs_data
import os
import pandas as pd
import datetime as dt

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

mapbox_api = os.getenv("mapbox_key")


header_app = dbc.Col(html.H1("Header"), width="auto")


geoj_grid, dk_grid, dk_grid_hover = get_map()

dict_cent = {'lon': 10.52,
            'lat': 55.89
            }

fig_map = go.Figure(
    go.Choroplethmapbox(
        geojson=geoj_grid,
        featureidkey="properties.KN10kmDK",
        locations=dk_grid['KN10kmDK'],
        z=dk_grid['Val'],
        colorscale=dk_grid['Col'],
        showscale=False,
        customdata=dk_grid_hover,
        hovertemplate='%{customdata[0]}<extra></extra>',
        #colorbar={'outlinecolor': dict_layout_cols['primary']}
    ),
    layout=go.Layout(
        mapbox=dict(
            accesstoken=mapbox_api,
            center=dict_cent,
            zoom=6.75,
            style="dark"
        ),
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        clickmode='event+select'
    )
)

map_app = dbc.Col(
    [
        dcc.Graph(
            id='map_figure',
            figure=fig_map,
            config={
                'displayModeBar': False},
            style={
                'height': '60vh',
                }
            ),
    ],
    width="auto",
)


# Figure DMI observational
dmi_obs = pd.read_csv("data/parse_data_test.csv", usecols=[
    "cellId", "from", "parameterId", "value"
])

dmi_obs_filtered = filter_dmi_obs_data(
    dmi_obs,
    cell_id = "10km_622_71",
    obs_date = "2023-01-02",
)

chart_dmi_obs = go.Figure()

chart_dmi_obs.add_trace(
    go.Bar(
        x=dmi_obs_filtered["from"],
        y=dmi_obs_filtered["mean_wind_speed"],
    )
)


chart_obs_app = dbc.Col(
    [
        dcc.Graph(
            id="chart_obs",
            figure=chart_dmi_obs
            )
    ]
)

map_click_info = dbc.Col(
    [
        html.Div(id="map_cell_id"),
    ]
)

app.layout = dbc.Container(
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
            chart_obs_app,
            justify="center"
            ),

        dbc.Row(
            map_click_info,
            justify="center"
            ),
    ]
)


@app.callback(
    Output('map_cell_id', 'children'),
    Input('map_figure', 'clickData')
)

def update_click_data(input_value):
    print(input_value)
    return f"Click data: {input_value}"

if __name__ == '__main__':
    app.run(debug=True)