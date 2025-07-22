import datetime as dt
import json
import os
from zipfile import ZipFile
import hashlib
import numpy as np
import pandas as pd
import requests
from typing import List, Optional, Dict, Any

CACHE_DIR = "cache"

def unzip_and_merge_dmi_obs_data(
        file_path,
        file_type,
        n_files=50,
):

    zip_file = ZipFile(file_path)
    if n_files:
        files_to_parse = zip_file.infolist()[:n_files]
    
    dfs = [read_file_in_zip(zip_file, file_)
        for file_ in files_to_parse
        if file_.filename.endswith(file_type)]
    
    df = pd.concat(dfs)

    return df


def read_file_in_zip(
        zip_file,
        file_name,
        n_rows=None,
):
    
    list_parameters = [
        "mean_temp",
        "mean_daily_max_temp",
        "mean_daily_min_temp",
        "mean_wind_speed",
        "max_wind_speed_10min",
        "max_wind_speed_3sec",
        "mean_wind_dir",
        "mean_pressure"
    ]

    list_columns_to_keep = [
        "cellId",
        "from",
        "to",
        "parameterId",
        "value"
    ]

    #with ZipFile(file_path) as z:
    with zip_file.open(file_name) as f:
        print(f"Parsing file {file_name}")
        list_rows = []
        for line in f:
            line_content = json.loads(line)["properties"]
            
            if (line_content["timeResolution"] == "hour") & (line_content["parameterId"] in list_parameters):

                list_values = [line_content[col] for col in list_columns_to_keep]

                list_rows.append(list_values)
            
            else:
                next
        
        df = pd.DataFrame(list_rows, columns=list_columns_to_keep)

    return df


FORECAST_WIND_PARAMETERS = ["wind-speed", "wind-dir", "gust-wind-speed-10m"]

def get_dmi_forecast_data(
        api_key: str,
        lon: float,
        lat: float,
        collection_type: str,
        parameters: Optional[List[str]] = None,
        cache_dir: str = CACHE_DIR
    ) -> Dict[str, Any]:
    """
    Fetches raw forecast data from the DMI API, with file-based caching.
    Returns the raw JSON response (does not extract values).
    """

    base_url="https://dmigw.govcloud.dk/v1/forecastedr/collections/"
    collections = {
        "wind": "harmonie_dini_sf",
        "waves": "wam_dw"
    }

    if collection_type not in collections.keys():
        error_message = f"""Collection type has to be one of {list(collections.keys())}.
        {collection_type} not valid.
        """

        raise ValueError(error_message)

    if parameters is None:
        parameters = FORECAST_WIND_PARAMETERS

    api_type = collections[collection_type]
    parameters_text = ",".join(parameters)
    query_url = f"{base_url}{api_type}/position?coords=POINT({lon} {lat})&crs=crs84&parameter-name={parameters_text}&api-key={api_key}"


    # --- Caching logic ---
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    # Use a hash of the query as the cache filename
    cache_key = hashlib.md5(query_url.encode('utf-8')).hexdigest()
    cache_path = os.path.join(cache_dir, f"{cache_key}.json")

    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            print(f"Loading cached response from {cache_path}")
            return json.load(f)


    # --- Fetch data from API ---
    try:
        response = requests.get(query_url)

        response.raise_for_status()

        json_response = response.json()

                # Save to cache
        with open(cache_path, "w") as f:
            json.dump(json_response, f)
        return json_response
    except requests.exceptions.RequestException as errh:
        raise ValueError(errh.args[0])




def extract_and_parse_forecast_data(
        json_response: Dict[str, Any],
        parameters: List[str],
):

    time_values = json_response["domain"]["axes"]["t"]["values"]
    longitude = json_response["domain"]["axes"]["x"]["values"][0]
    latitude = json_response["domain"]["axes"]["y"]["values"][0]

    parameter_values = {p:json_response["ranges"][p]["values"] for p in parameters}

    parameter_values["timestamp"] = time_values

    df = pd.DataFrame(parameter_values)
        
    df["longitude"] = longitude
    df["latitude"] = latitude

    return df
        

def get_dmi_observational_data(
    api_key: str,
    cell_id: str,
    date_from: str,
    date_to: str,
    cache_dir: str = CACHE_DIR
):


    base_url = "https://dmigw.govcloud.dk/v2/climateData/collections/10kmGridValue/items?"

    query_url = f"{base_url}cellId={cell_id}&datetime={date_from}T00:00:00Z/{date_to}T23:59:59Z&api-key={api_key}"

    # --- Caching logic ---
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    # Use a hash of the query as the cache filename
    cache_key = hashlib.md5(query_url.encode('utf-8')).hexdigest()
    cache_path = os.path.join(cache_dir, f"{cache_key}.json")

    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            print(f"Loading cached response from {cache_path}")
            return json.load(f)
        
    try:
        response = requests.get(query_url)

        response.raise_for_status()

        json_response = response.json()
        
        with open(cache_path, "w") as f:
            json.dump(json_response, f)
        return json_response
    except requests.exceptions.RequestException as errh:
        raise ValueError(errh.args[0])

if __name__ == "__main__":
    api_key = os.getenv("DMI_API_KEY_OBSERVATION")
    cell_id = "10km_620_44"
    date_from = "2025-07-20"
    date_to = "2025-07-21"
    json_response = get_dmi_observational_data(api_key, cell_id, date_from, date_to)
    print(json_response)




