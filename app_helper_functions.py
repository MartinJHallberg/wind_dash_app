import json
import pandas as pd
import requests
import numpy as np
import datetime as dt

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

def get_map(
        dk_grid_url = 'https://raw.githubusercontent.com/MartinJHallberg/DMI_Wind_DashApp/version2/assets/DKN_10KM_epsg4326_filtered_wCent.geojson'
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

    # Color columns
    shp_grid['Val'] = 1
    shp_grid['Col'] = fun_col_to_trans(dict_layout_cols()['primary'], 0.4)

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
    


def fun_col_to_trans(col, transparency):
    # Convert transparency to string
    t_trans = str(transparency)

    # Split text and insert transparency
    col_out = col.split(')')[0] + ',' + t_trans + ')'
    # Change color type to include transparency
    col_out = col_out.replace('rgb', 'rgba')

    return col_out

def filter_dmi_obs_data(
        dmi_obs,
        cell_id,
        obs_date,
        n_extra_days=1
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


    

