from app_helper_functions import filter_dmi_obs_data
import plotly.graph_objects as go

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