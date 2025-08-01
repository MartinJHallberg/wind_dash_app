import json
import pandas as pd
import requests
import numpy as np
import datetime as dt
from wind_dashapp.data_processing.dmi import (
    fetch_dmi_forecast_data,
    parse_dmi_forecast_data,
    fetch_dmi_observational_data,
    parse_dmi_observational_data,
    CACHE_DIR,
)

DEFAULT_NUMBER_OF_HOURS_FETCH_FORECAST = 48
DEFAULT_NUMBER_OF_HOURS_FETCH_OBS = 60
DEFAULT_HOUR_OBS_DATA = 12


def get_map(
    dk_grid_url="https://raw.githubusercontent.com/MartinJHallberg/DMI_Wind_DashApp/version2/assets/DKN_10KM_epsg4326_filtered_wCent.geojson",
):
    geoj_grid = json.loads(requests.get(dk_grid_url).text)

    shp_grid = pd.json_normalize(geoj_grid["features"])

    shp_grid.rename(
        columns={
            "properties.KN10kmDK": "KN10kmDK",
            "properties.Stednavn": "Stednavn",
            "properties.cent_lon": "cent_lon",
            "properties.cent_lat": "cent_lat",
        },
        inplace=True,
    )

    # Rename None to 'No name'
    shp_grid["Stednavn"].fillna("No name", inplace=True)

    # Hover columns
    hover_data_map = np.stack((shp_grid["Stednavn"], shp_grid["cent_lon"], shp_grid["cent_lat"]), axis=1)

    return geoj_grid, shp_grid, hover_data_map


def filter_dmi_obs_data(dmi_obs, cell_id, obs_date, n_extra_days=1, **kwargs):
    dmi_obs = dmi_obs.loc[dmi_obs["cellId"] == cell_id]

    dmi_obs = pd.pivot_table(dmi_obs, values="value", index="from", columns="parameterId").reset_index()

    dmi_obs["from"] = pd.to_datetime(dmi_obs["from"].str.replace("\+00:00", "", regex=False))
    dmi_obs["date"] = dmi_obs["from"].dt.date

    obs_date = dt.datetime.strptime(obs_date, "%Y-%m-%d").date()

    dmi_obs_filtered = dmi_obs.loc[
        (dmi_obs["date"] == obs_date) | (dmi_obs["date"] == obs_date - dt.timedelta(days=n_extra_days))
    ]

    return dmi_obs_filtered


def parse_dmi_forecast_data_wind(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"].str.replace("\+00:00", "", regex=False))

    new_col_names = {col: col.replace("-", "_") for col in df.columns}

    df = df.rename(new_col_names, axis="columns")

    df = df.tail(48)  # forecast for last 48 hours

    return df


def load_wind_forecast_data_to_app(
    api_key: str,
    lon: float,
    lat: float,
    collection_type: str,
    n_hours: int = DEFAULT_NUMBER_OF_HOURS_FETCH_FORECAST,
    cache_dir: str = CACHE_DIR,
    use_mock_data: bool = True,
):
    if use_mock_data:
        json_response = json.load(open("wind_dashapp/mock_data/dmi_wind_forecast_data_mock1.json"))
        print("Using mock data for forecast data")
    else:
        json_response = fetch_dmi_forecast_data(api_key, lon, lat, collection_type, cache_dir=cache_dir)
    df = parse_dmi_forecast_data(json_response)

    df = parse_and_filter_dates(df)

    new_col_names = {col: col.replace("-", "_") for col in df.columns}

    df = df.rename(new_col_names, axis="columns")

    df = df.sort_values(by="from_datetime")

    df = df.head(n_hours)  # forecast for last 48 hours

    if use_mock_data:
        df["wind_speed"] = df["wind_speed"].apply(lambda x: x * np.random.uniform(0.5, 1.5))

    return df


def load_wind_obs_data_to_app(
    api_key: str,
    cell_id: str,
    date_from: str,
    n_hours=DEFAULT_NUMBER_OF_HOURS_FETCH_OBS,
    cache_dir: str = CACHE_DIR,
    use_mock_data: bool = True,
):
    date_before = pd.to_datetime(date_from) - dt.timedelta(days=1)
    if use_mock_data:
        json_response = json.load(open("wind_dashapp/mock_data/dmi_wind_obs_data_mock6.json"))
        print("Using mock data for observational data")
    else:
        json_response = fetch_dmi_observational_data(api_key, cell_id, date_before, n_hours, cache_dir=cache_dir)
    df = parse_dmi_observational_data(json_response)

    df = parse_and_filter_dates(df)

    df_pivot = pd.pivot_table(df, values="value", index="from_datetime", columns="parameter_id").reset_index()

    if use_mock_data:
        df_pivot["mean_wind_speed"] = df_pivot["mean_wind_speed"].apply(lambda x: x * np.random.uniform(0.5, 1.5))
        start_datetime = pd.Timestamp(date_before.date()).replace(tzinfo=pd.Timestamp(df_pivot['from_datetime'].iloc[0]).tzinfo)
        df_pivot['from_datetime'] = [start_datetime + pd.Timedelta(hours=i) for i in range(len(df_pivot))]

    return df_pivot


def parse_and_filter_dates(df: pd.DataFrame):
    # Remove observations with microseconds, seems to be a bug in the DMI API
    df["has_microseconds"] = df["from"].str.contains("00:00:00.001000")
    df_filtered = df[~df["has_microseconds"]].copy()

    df_filtered["from_datetime"] = pd.to_datetime(df_filtered["from"], format="ISO8601")
    # df_filtered['to_datetime'] = pd.to_datetime(df_filtered['to'], format='ISO8601')

    # Check if timestamps are parsed correctly
    if df_filtered["from_datetime"].dtype != "datetime64[ns, UTC]":
        raise ValueError("Timestamps could not be parsed correctly from API response")

    # Convert to Copenhagen time
    df_filtered["from_datetime"] = df_filtered["from_datetime"].dt.tz_convert("Europe/Copenhagen")
    # df_filtered['to_datetime'] = df_filtered['to_datetime'].dt.tz_convert('Europe/Copenhagen')

    df_filtered = df_filtered.drop(columns=["from", "to", "has_microseconds"], errors="ignore")

    return df_filtered

def convert_json_to_df(stored_json: dict):
    df = pd.DataFrame(stored_json)
    df['from_datetime'] = pd.to_datetime(df['from_datetime'])

    return df

def map_slider_to_date(df):
    slider_to_date = {
        i + 1: dt for i, dt in enumerate(df["from_datetime"])
    }

    return slider_to_date




