import numpy as np
import pandas as pd
import datetime as dt
import json
from zipfile import ZipFile

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



    
