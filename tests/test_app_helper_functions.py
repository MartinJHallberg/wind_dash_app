import pytest
import pandas as pd
from dotenv import load_dotenv
import os
from wind_dashapp.helper_functions import app_helper_functions as f

load_dotenv()

DMI_API_KEY_OBSERVATION = os.getenv("DMI_API_KEY_OBSERVATION")
DMI_API_KEY_FORECAST = os.getenv("DMI_API_KEY_FORECAST")



def test_load_dmi_observational_data():
    cell_id = "10km_620_44"
    date_from = "2025-06-20"

    df = f.load_wind_obs_data_to_app(DMI_API_KEY_OBSERVATION, cell_id, date_from)

    assert isinstance(df, pd.DataFrame)

    # Check min and max date in 'from' column
    min_date = df["from_datetime"].min().date()
    input_date = pd.to_datetime(date_from).date()
    assert min_date == input_date
    assert len(df) == 49

def test_load_dmi_forecast_data():
    lon = 12.5683
    lat = 55.6761
    collection_type = "wind"

    df = f.load_wind_forecast_data_to_app(DMI_API_KEY_FORECAST, lon, lat, collection_type)

    columns = ["wind_speed", "wind_dir", "from_datetime", "longitude", "latitude"]
    assert isinstance(df, pd.DataFrame)
    for col in columns:
        assert col in df.columns 