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
    # Convert transparency to string
    t_trans = str(transparency)

    # Split text and insert transparency
    col_out = col.split(')')[0] + ',' + t_trans + ')'
    # Change color type to include transparency
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


def degrees_to_cardinal_directions(d):

    card = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

    ix = round(d / (360. / len(card)))
    
    card_text = card[ix % len(card)]
    
    return card_text

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


def create_dmi_obs_chart(
        dmi_data,
        cell_id,
        obs_date

):
    dmi_obs_filtered = filter_dmi_obs_data(
        dmi_data,
        cell_id = cell_id,
        obs_date = obs_date
    )

    chart_dmi_obs = go.Figure()

    dmi_obs_filtered["mean_wind_direction_cardinal"] = dmi_obs_filtered["mean_wind_dir"].apply(degrees_to_cardinal_directions)
    hover_data_chart = np.stack((dmi_obs_filtered["mean_wind_dir"], dmi_obs_filtered["mean_wind_direction_cardinal"], dmi_obs_filtered["from"].dt.hour.astype(str) + ':00'), axis=1)

    chart_dmi_obs.add_trace(
        go.Bar(
            x=dmi_obs_filtered["from"],
            y=dmi_obs_filtered["mean_wind_speed"],
            customdata=hover_data_chart,
            hovertemplate=
            'Avg. wind: %{y}' +
            '<br>Wind direction: %{customdata[1]} (%{customdata[0]}\xb0)' +
            '<br>Time: %{customdata[2]}<extra></extra>',
            hoverlabel=dict(
                bgcolor='rgba(255,255,255,0.3)',
                font=dict(color='black')
            ),
        )
    )

    y_axes = dict(
        gridwidth=0.0001,
        showticksuffix='last',
        ticksuffix=' m/s'
    )
    
    x_axes = dict(
        linewidth=0.1,
        showgrid=False
    )

    chart_dmi_obs.update_yaxes(y_axes)
    chart_dmi_obs.update_xaxes(x_axes)

    chart_dmi_obs.update_layout(
         yaxis=dict(range=[0, 30]),
    #     autosize=True,
    #     bargap=0.5,
         margin=dict(l=40, r=40, t=10, b=20),
    #     plot_bgcolor=dict_layout_cols()["transparent"],
         paper_bgcolor=dict_layout_cols()["transparent"]
    )



    for i, row in dmi_obs_filtered.iterrows():
        x_date = row["from"]

        ax = dict_dir_coord[row["mean_wind_direction_cardinal"]]['X_cord']*2
        ay = dict_dir_coord[row["mean_wind_direction_cardinal"]]['Y_cord']*2

        chart_dmi_obs.add_annotation(
            x=x_date,
            y=row["mean_wind_speed"],
            ax=ax,
            ay=ay,
            arrowhead=3,
            arrowsize=1.5,
            arrowwidth=1.1,
            arrowcolor=dict_layout_cols()['orange'],
            xref="x",
            yref="y",
            # row=2,
            # col=1
        )

    return chart_dmi_obs
