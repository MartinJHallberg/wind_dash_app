from app_helper_functions import filter_dmi_obs_data, get_map
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def dict_layout_cols():
    dict_cols = {
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

    return dict_cols


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
    dk_grid['Col'] = fun_col_to_trans(dict_layout_cols()['primary'], 0.4)

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
            #colorbar={'outlinecolor': dict_layout_cols()['primary']}
        ),
        layout=go.Layout(
            mapbox=dict(
                accesstoken=mapbox_api,
                center=dict_cent,
                zoom=5.5,
                style="dark",
            ),
            autosize=True,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor=dict_layout_cols()["transparent"],
            paper_bgcolor=dict_layout_cols()["transparent"],
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
    dmi_obs_filtered = filter_dmi_obs_data(
        dmi_data,
        cell_id = cell_id,
        obs_date = obs_date
    )

    chart = create_mean_wind_speed_chart(dmi_obs_filtered)

    chart = add_direction_arrows(
        dmi_obs_filtered,
        chart,
        y_column="mean_wind_speed",
        dir_column="mean_wind_dir",
        x_scale=25,
        y_scale=1,
        y_distance=1
    )

    chart = add_max_wind_chart(
        dmi_obs_filtered,
        chart
    )

    chart.update_layout(
        clickmode = "event+select"
    )

    return chart

def create_mean_wind_speed_chart(
        df,
):
    y_max= df["mean_wind_speed"].max()

    if y_max> 19:
        y_max= 30
    else:
        y_max= 20
        
    chart = go.Figure()

    df["mean_wind_direction_cardinal"] = df["mean_wind_dir"].apply(degrees_to_cardinal_directions)
    hover_data_chart = np.stack(
        (
            df["mean_wind_dir"],
            df["mean_wind_direction_cardinal"],
            df["from"].dt.hour.astype(str) + ':00'
        ),
        axis=1
    )

    chart.add_trace(
        go.Bar(
            x=df["from"],
            y=df["mean_wind_speed"],
            customdata=hover_data_chart,
            hovertemplate=
            'Mean wind: %{y}' +
            '<br>Wind direction: %{customdata[1]} (%{customdata[0]}\xb0)',
            name="Mean wind speed [m/s]"
        )
    )

    y_axes = dict(
        gridwidth=0.0001,
        showticksuffix='last',
        ticksuffix=' m/s',
    )
    
    x_axes = dict(
        linewidth=0.1,
        showgrid=False
    )

    chart.update_yaxes(y_axes)
    chart.update_xaxes(x_axes)

    chart.update_layout(
        yaxis=dict(range=[0, y_max]),
    #     autosize=True,
    #     bargap=0.5,
        margin=dict(l=40, r=40, t=10, b=20),
#     plot_bgcolor=dict_layout_cols()["transparent"],
        paper_bgcolor=dict_layout_cols()["transparent"],
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor=fun_col_to_trans(dict_layout_cols()['white'],0.75),
            font=dict(color='black')
        ),
    )

    return chart


def add_direction_arrows(
    df,
    chart,
    y_column,
    dir_column,
    x_scale,
    y_scale,
    y_distance,
):

    for i, row in df.iterrows():
    
        x = row["from"]
        y = row[y_column]

        x_diff, y_diff = get_angle_coordinate_from_degree(row[dir_column])
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
            arrowcolor=dict_layout_cols()['orange'],
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
                # opacity = 0.8,
                #color="rgb(255,255,255)",  # dict_layout_cols['bg_blue']
                width=2,
                dash='dash'
            ),
            showlegend=True,
            name='Max wind speed',
            legendrank=1
        )
    )

    return chart
