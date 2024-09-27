import plotly.graph_objects as go
from dash import dcc, html, Dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from datetime import date
from plotly.subplots import make_subplots
from dotenv import load_dotenv
from app_helper_functions import get_map, filter_dmi_obs_data
import os
import pandas as pd
import app_graph_functions as graphs
import datetime as dt

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

mapbox_api = os.getenv("mapbox_key")
# Figure DMI observational
dmi_obs = pd.read_csv("data/parse_data_test.csv", usecols=[
    "cellId", "from", "parameterId", "value"
])

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

chart_dmi_obs = graphs.create_dmi_obs_chart(
    dmi_obs,
    "10km_622_71",
    "2023-01-02",
)

chart_obs_app = dbc.Col(
    [
        dcc.Graph(
            id="chart_obs",
            figure=chart_dmi_obs
            )
    ]
)

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
            date_picker_app,
            justify="center",

        ),

        dbc.Row(
            chart_obs_app,
            justify="center"
            ),
    ]
)


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





if __name__ == '__main__':
    app.run(debug=True)


