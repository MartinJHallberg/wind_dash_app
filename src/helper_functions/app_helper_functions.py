import json
import pandas as pd
import requests
import numpy as np
import datetime as dt

def get_map(
        dk_grid_url = 'https://raw.githubusercontent.com/MartinJHallberg/DMI_Wind_DashApp/version2/assets/DKN_10KM_epsg4326_filtered_wCent.geojson',
):
    geoj_grid = json.loads(requests.get(dk_grid_url).text)

    shp_grid = pd.json_normalize(geoj_grid['features'])

    shp_grid.rename(
        columns={
            'properties.KN10kmDK': 'KN10kmDK',
            'properties.Stednavn': 'Stednavn',
            'properties.cent_lon': 'cent_lon',
            'properties.cent_lat': 'cent_lat'
        },
        inplace=True
        )

    # Rename None to 'No name'
    shp_grid['Stednavn'].fillna('No name', inplace=True)

    # Hover columns
    hover_data_map = np.stack(
        (
            shp_grid['Stednavn'],
            shp_grid['cent_lon'],
            shp_grid['cent_lat']
        ),
        axis=1
    )
    
    return geoj_grid, shp_grid, hover_data_map
    
def filter_dmi_obs_data(
        dmi_obs,
        cell_id,
        obs_date,
        n_extra_days=1,
        **kwargs
):

    dmi_obs = dmi_obs.loc[dmi_obs["cellId"] == cell_id]

    dmi_obs = pd.pivot_table(dmi_obs, values='value',
                            index='from',
                            columns='parameterId').reset_index()

    dmi_obs['from'] = pd.to_datetime(dmi_obs['from'].str.replace('\+00:00', "", regex=False))
    dmi_obs['date'] = dmi_obs['from'].dt.date

    obs_date = dt.datetime.strptime(obs_date, "%Y-%m-%d").date()

    dmi_obs_filtered = dmi_obs.loc[
        (dmi_obs["date"] == obs_date) |
        (dmi_obs["date"] == obs_date - dt.timedelta(days=n_extra_days))
        ]

    return dmi_obs_filtered

def parse_dmi_forecast_data_wind(
        df
):
    
    df["timestamp"] = pd.to_datetime(df['timestamp'].str.replace('\+00:00', "", regex=False))

    new_col_names = {col: col.replace("-", "_") for col in df.columns}

    df = df.rename(new_col_names, axis="columns")

    df = df.tail(48) # forecast for last 48 hours

    return df


    

