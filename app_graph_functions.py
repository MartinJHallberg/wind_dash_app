from app_helper_functions import filter_dmi_obs_data, get_map
import plotly.graph_objects as go

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
            plot_bgcolor=dict_layout_cols()["transparent"],
            paper_bgcolor=dict_layout_cols()["transparent"],
            clickmode='event+select'
        )
    )

    return fig_map


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

    chart_dmi_obs.add_trace(
        go.Bar(
            x=dmi_obs_filtered["from"],
            y=dmi_obs_filtered["mean_wind_speed"],
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
        autosize=True,
        bargap=0.5,
        margin=dict(l=40, r=40, t=20, b=20),
        plot_bgcolor=dict_layout_cols()["transparent"],
        paper_bgcolor=dict_layout_cols()["transparent"]
    )

    return chart_dmi_obs
