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
    'primary': 'rgb(55, 141, 252)',
    'secondary': 'rgb(217, 227, 241)',
    'dark_blue': 'rgb(0, 72, 170)',
    'yellow': 'rgb(255, 193, 7)',
    'red': 'rgb(180, 15, 74)',
    # 'bg_blue': 'rgb(56, 97, 141)',
    'white': 'rgb(255, 255,255)',
    # 'bg_blue2': 'rgb(15,37,55)',
    'orange': 'rgb(253, 126, 20)',
    'transparent': 'rgba(255,255,255,0)'
    }

#    return dict_cols


def add_transparency_to_color(col, transparency):

    t_trans = str(transparency)

    col_out = col.split(')')[0] + ',' + t_trans + ')'

    col_out = col_out.replace('rgb', 'rgba')

    return col_out

def create_map_chart():
    geoj_grid, dk_grid, dk_grid_hover = get_map()

    dk_grid['Val'] = 1
    dk_grid['Col'] = add_transparency_to_color(layout_colors['primary'], 0.4)

    dict_center = {'lon': 10.52,
                'lat': 55.89
                }

    fig_map = go.Figure(
        go.Choroplethmap(
            geojson=geoj_grid,
            featureidkey="properties.KN10kmDK",
            locations=dk_grid['KN10kmDK'],
            z=dk_grid['Val'],
            colorscale=[[0, layout_colors['primary']], [1, layout_colors['primary']]],
            showscale=False,
            marker_line_width=0,
            marker_opacity=0.4,
            customdata=dk_grid_hover,
            hovertemplate='%{customdata[0]}<extra></extra>',
            hoverlabel=dict(
                font_color=layout_colors["dark_blue"],
                bgcolor=add_transparency_to_color(layout_colors["secondary"],0.4),
                bordercolor=layout_colors['transparent']
            )
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

    #try:
    ix = round(degrees / (360. / len(cardinal_directions)))
    card_text = cardinal_directions[ix % len(cardinal_directions)]

    return card_text
    
    # except:
    #     print(degrees)
    
    
    
    return card_text

def get_angle_coordinate_from_degree(degree):

    y_cord = -round(np.cos(np.deg2rad(degree)), 2)
    x_cord = round(np.sin(np.deg2rad(degree)), 2)

    return x_cord, y_cord

def create_full_wind_chart(
        df,
        **kwargs
):
    # Get mean wind chart
    chart = create_wind_speed_chart(
        df,
        **kwargs
        )

    if "chart" in kwargs.keys():
        kwargs.pop("chart") # remove chart from kwargs, needed when createing overlay graphs
    
    # Add directional arrows
    chart = add_direction_arrows(
        df,
        chart=chart,
        **kwargs
    )

    # Add max wind chart
    chart = add_max_wind_chart(
        df,
        chart=chart,
        **kwargs
    )

    # Set layout
    col_wind_speed = kwargs["col_wind_speed"]
    col_wind_max_speed = kwargs["col_wind_max_speed"]
    y_max = max(
        df[col_wind_speed].max(),
        df[col_wind_max_speed].max()
    )

    bins_list = [0.0, 15.0, 20.0, 25.0]
    bins = np.array(bins_list)

    y_max = bins_list[np.digitize(y_max, bins)] + 2

    # Set axes
    y_axes = dict(
        gridwidth=0.001,
        showticksuffix='last',
        ticksuffix=' m/s',
        showgrid=True,
        range=[-2, y_max],
        #tickvals=[0,2,4],
        tickvals=[*range(0,int(y_max), 2)],
        fixedrange=True,
        tickfont_size=12,
        zerolinecolor=layout_colors["white"],
        gridcolor=layout_colors["white"],
        zerolinewidth=3
    )
    
    x_axes = dict(
        linewidth=0.1,
        showgrid=False,
        fixedrange=True,
        tickfont_size=12
    )

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
        margin=dict(
            l=1,
            r=1,
            b=10,
            t=10,
        ),
        paper_bgcolor=layout_colors["transparent"],
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor=add_transparency_to_color(layout_colors['white'],0.75),
            font=dict(color='black')
        ),
        clickmode = "event+select"
    )

    return chart

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
    chart = create_full_wind_chart(
        df=dmi_obs_filtered,
        col_wind_speed="mean_wind_speed",
        col_wind_max_speed="max_wind_speed_3sec",
        col_wind_direction="mean_wind_dir",
        col_datetime="from",
    )

    return chart
    

def create_forecast_chart(
        forecast_data,
        cell_id=None, # for later use
        **kwargs
    ):
    
    # Filter forecast data
    forecast_data_filter = forecast_data.copy()

    chart = create_full_wind_chart(
            df=forecast_data_filter,
            col_wind_speed="wind_speed",
            col_wind_max_speed="gust_wind_speed_10m",
            col_wind_direction="wind_dir",
            col_datetime="timestamp",
            marker_opacity=1,
    )

    return chart


def create_wind_speed_chart(
        df,
        col_wind_speed,
        col_wind_direction,
        col_datetime,
        marker_opacity=1,
        marker_color=layout_colors["primary"],
        chart=None,
        **kwargs
):
    if not chart:
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
            name="Mean wind speed [m/s]",
            opacity=marker_opacity,
            marker_color=marker_color
        )
    )

    return chart


def add_direction_arrows(
    df,
    chart,
    col_wind_direction,
    col_datetime,
    x_scale=25,
    y_scale=0.65,
    marker_color=layout_colors["primary"],
    marker_opacity=1,
    **kwargs
):



    for i, row in df.iterrows():
    
        x = row[col_datetime]
        y = -1

        x_diff, y_diff = get_angle_coordinate_from_degree(row[col_wind_direction])
        x_diff = x_diff * x_scale
        y_diff = y_diff * y_scale

        chart.add_annotation(
            x=x + pd.Timedelta(minutes=-x_diff),
            y=y + y_diff,
            ax=x + pd.Timedelta(minutes=x_diff),
            axref="x",
            ay=y - y_diff,
            ayref="y",
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=1.1,
            arrowcolor=marker_color,
            opacity=marker_opacity,
            xref="x",
            yref="y",
        )

    return chart

def add_max_wind_chart(
    df,
    col_datetime,
    col_wind_max_speed,
    marker_opacity=1,
    marker_color=layout_colors["primary"],
    chart=None,
    **kwargs
):
    
    if not chart:
        chart = go.Figure()
    
    chart.add_trace(
        go.Scatter(
            x=df[col_datetime],
            y=df[col_wind_max_speed],
            hovertemplate=
            'Max wind speed (3s): %{y}<extra></extra>',
            line=dict(
                width=3,
                dash='dash'
            ),
            showlegend=True,
            name='Max wind speed',
            legendrank=1,
            opacity=marker_opacity,
            marker_color=marker_color,
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
        "timestamp",
        marker_opacity=1
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
        **kwargs
):
    obs_filtered = filter_dmi_obs_data(
        obs_data,
        **kwargs
    )

    obs_filtered["map_forecast_time"] = forecast_chart.data[0].x.tolist()

    chart = go.Figure(forecast_chart) # needed to create a copy

    kwargs["col_datetime"] = "map_forecast_time"

    color = layout_colors["orange"]

    chart = create_wind_speed_chart(
        obs_filtered,
        marker_opacity=0.6,
        marker_color=color,
        chart=chart,
        **kwargs
    )

    chart = add_direction_arrows(
        df=obs_filtered,
        chart=chart,
        marker_opacity=0.6,
        marker_color=color,
        **kwargs
    )

    chart = add_max_wind_chart(
        df=obs_filtered,
        chart=chart,
        marker_opacity=0.7,
        marker_color=color,
        **kwargs
    )
    
    chart.update_layout(
        barmode="overlay"
    )

    return chart

# def map_observational_datetime_to_forecast(
#         obs_data,
#         forecast_data
# ):
    

    
