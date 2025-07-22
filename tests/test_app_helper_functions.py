from src.helper_functions.app_helper_functions import (
    load_dmi_obs_data_to_app,#
    load_dmi_forecast_data_to_app
)
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

DMI_API_KEY_OBSERVATION = os.getenv("DMI_API_KEY_OBSERVATION")
DMI_API_KEY_FORECAST = os.getenv("DMI_API_KEY_FORECAST")

def test_load_dmi_observational_data():
    cell_id = "10km_620_44"
    date_from = "2025-07-20"
    date_to = "2025-07-21"

    df = load_dmi_obs_data_to_app(DMI_API_KEY_OBSERVATION, cell_id, date_from, date_to)

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["cell_id", "from", "to", "parameter_id", "value"]

def test_load_dmi_forecast_data():
    lon = 12.5683
    lat = 55.6761
    collection_type = "wind"

    df = load_dmi_forecast_data_to_app(DMI_API_KEY_FORECAST, lon, lat, collection_type)

    columns = ["wind-speed", "wind-dir", "timestamp", "longitude", "latitude"]
    assert isinstance(df, pd.DataFrame)
    for col in columns:
        assert col in df.columns