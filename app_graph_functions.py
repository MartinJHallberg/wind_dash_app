from app_helper_functions import filter_dmi_obs_data, get_map
import plotly.graph_objects as go

def create_map_chart(
        mapbox_api,
):
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

    return chart_dmi_obs