from app_helper_functions import (
    filter_dmi_obs_data,
    get_map,
    parse_dmi_forecast_data_wind
)
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from plotly.subplots import make_subplots


layout_colors = {
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

#    return dict_cols


def fun_col_to_trans(col, transparency):

    t_trans = str(transparency)

    col_out = col.split(')')[0] + ',' + t_trans + ')'

    col_out = col_out.replace('rgb', 'rgba')

    return col_out

def create_map_chart(
        mapbox_api,
):
    geoj_grid, dk_grid, dk_grid_hover = get_map()

    dk_grid['Val'] = 1
    dk_grid['Col'] = fun_col_to_trans(layout_colors['primary'], 0.4)

    dict_center = {'lon': 10.52,
                'lat': 55.89
                }

    fig_map = go.Figure(
        go.Choroplethmap(
            geojson=geoj_grid,
            featureidkey="properties.KN10kmDK",
            locations=dk_grid['KN10kmDK'],
            z=dk_grid['Val'],
            colorscale=dk_grid['Col'],
            showscale=False,
            #customdata=dk_grid_hover,
            #hovertemplate='%{customdata[0]}<extra></extra>',
            colorbar={'outlinecolor': layout_colors['primary']}
        ),
        layout=go.Layout(
            map_style="carto-positron",
            map_zoom=6,
            map_center = dict_center,
            autosize=True,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor=layout_colors["transparent"],
            paper_bgcolor=layout_colors["transparent"],
            clickmode='event+select'
        )
    )

    return fig_map

cardinal_directions = [
    'N',
    'NNE',
    'NE',
    'ENE',
    'E',
    'ESE',
    'SE',
    'SSE',
    'S',
    'SSW',
    'SW',
    'WSW',
    'W',
    'WNW',
    'NW',
    'NNW'
]


def degrees_to_cardinal_directions(degrees):

    ix = round(degrees / (360. / len(cardinal_directions)))
    
    card_text = cardinal_directions[ix % len(cardinal_directions)]
    
    return card_text

def get_angle_coordinate_from_degree(degree):

    y_cord = -round(np.cos(np.deg2rad(degree)), 2)
    x_cord = round(np.sin(np.deg2rad(degree)), 2)

    return x_cord, y_cord


def create_obs_chart(
        dmi_data,
        cell_id,
        obs_date

):
    # Get data
    dmi_obs_filtered = filter_dmi_obs_data(
        dmi_data,
        cell_id = cell_id,
        obs_date = obs_date
    )

    # Get mean wind chart
    chart = create_wind_speed_chart(
        dmi_obs_filtered,
        "mean_wind_speed",
        "mean_wind_dir",
        "from"
        )

    # Add directional arrows
    chart = add_direction_arrows(
        dmi_obs_filtered,
        chart,
        col_wind_speed="mean_wind_speed",
        col_wind_direction="mean_wind_dir",
        col_datetime="from",
        x_scale=25,
        y_scale=0.5,
        y_distance=1
    )

    # Add max wind chart
    chart = add_max_wind_chart(
        dmi_obs_filtered,
        chart
    )



    # Set layout
    y_max = max(
        dmi_obs_filtered["mean_wind_speed"].max(),
        dmi_obs_filtered["max_wind_speed_3sec"].max()
    )

    if y_max> 19:
        y_max= 30
    else:
        y_max= 20

    # Set axes
    y_axes = dict(
        gridwidth=0.0001,
        showticksuffix='last',
        ticksuffix=' m/s',
        range=[0, y_max],
        fixedrange=True,
        tickfont_size=14
    )
    
    x_axes = dict(
        linewidth=0.1,
        showgrid=False,
        fixedrange=True,
        tickfont_size=13
    )

    #chart.update_yaxes(y_axes)
    #chart.update_xaxes(x_axes)

    chart.update_layout(
        xaxis=x_axes,
        yaxis=y_axes,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            font_size=15
        ),
        margin=dict(l=40, r=40, t=10, b=20),
        paper_bgcolor=layout_colors["transparent"],
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor=fun_col_to_trans(layout_colors['white'],0.75),
            font=dict(color='black')
        ),
        clickmode = "event+select"
        #plot_bgcolor=layout_colors["transparent"],
        #autosize=True,
        #bargap=0.5,
    )

    return chart

def create_wind_speed_chart(
        df,
        col_wind_speed,
        col_wind_direction,
        col_datetime,
):
        
    chart = go.Figure()

    df[col_wind_direction + "_cardinal"] = df[col_wind_direction].apply(degrees_to_cardinal_directions)
    hover_data_chart = np.stack(
        (
            df[col_wind_direction],
            df[col_wind_direction + "_cardinal"],
            df[col_datetime].dt.hour.astype(str) + ':00'
        ),
        axis=1
    )

    chart.add_trace(
        go.Bar(
            x=df[col_datetime],
            y=df[col_wind_speed],
            customdata=hover_data_chart,
            hovertemplate=
            'Mean wind: %{y}' +
            '<br>Wind direction: %{customdata[1]} (%{customdata[0]}\xb0)',
            name="Mean wind speed [m/s]"
        )
    )

    return chart


def add_direction_arrows(
    df,
    chart,
    col_wind_speed,
    col_wind_direction,
    col_datetime,
    x_scale,
    y_scale,
    y_distance,
):

    for i, row in df.iterrows():
    
        x = row[col_datetime]
        y = row[col_wind_speed]

        x_diff, y_diff = get_angle_coordinate_from_degree(row[col_wind_direction])
        x_diff = x_diff * x_scale
        y_diff = y_diff * y_scale

        chart.add_annotation(
            x=x + pd.Timedelta(minutes=-x_diff),
            y=y + y_distance + y_diff,
            ax=x + pd.Timedelta(minutes=x_diff),
            axref="x",
            ay=y + y_distance - y_diff,
            ayref="y",
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=1.1,
            arrowcolor=layout_colors['orange'],
            xref="x",
            yref="y",
            # row=2,
            # col=1
        )

    return chart

def add_max_wind_chart(
    df,
    chart=None
):
    
    if not chart:
        chart = go.Figure()
    
    chart.add_trace(
        go.Scatter(
            x=df["from"],
            y=df['max_wind_speed_3sec'],
            hovertemplate=
            'Max wind speed (3s): %{y}<extra></extra>',
            line=dict(
                width=2,
                dash='dash'
            ),
            showlegend=True,
            name='Max wind speed',
            legendrank=1
        )
    )

    return chart

def create_forecast_chart_wind(
        df,
        cell_id=None,
):

    # Get mean wind chart
    chart = create_wind_speed_chart(
        df,
        "wind_speed",
        "wind_dir",
        "timestamp"
        )

    # Add directional arrows
    chart = add_direction_arrows(
        df,
        chart,
        col_wind_speed="wind_speed",
        col_wind_direction="wind_dir",
        col_datetime="timestamp",
        x_scale=25,
        y_scale=0.5,
        y_distance=1
    )

    chart.update_layout(title=cell_id)

    return chart


def add_obs_data_to_forecast_chart(
        forecast_chart,
        obs_data,
        col_wind_speed,
        col_datetime,
):
    
    obs_data[col_wind_speed] = obs_data[col_wind_speed]*0.5

    chart = go.Figure(forecast_chart) # needed to create a copy
    
    chart.add_trace(
        go.Bar(
            x=obs_data[col_datetime],
            y=obs_data[col_wind_speed],
            #customdata=hover_data_chart,
            #hovertemplate=
            #'Mean wind: %{y}' +
            #'<br>Wind direction: %{customdata[1]} (%{customdata[0]}\xb0)',
            #name="Mean wind speed [m/s]"
        )
    )

    return chart

# def make_combo_forecast_and_obs_chart(
#         forecast_chart,
#         obs_chart
# ):
    
#     chart = make_subplots(
#         rows=2,
#         cols=1,
#         shared_xaxes=True,
#         vertical_spacing=0.02
#     )

    
