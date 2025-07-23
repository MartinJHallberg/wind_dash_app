import pytest
import pandas as pd
from dotenv import load_dotenv
import os
from src.wind_dashapp.helper_functions.functions import new_function

load_dotenv()

DMI_API_KEY_OBSERVATION = os.getenv("DMI_API_KEY_OBSERVATION")
DMI_API_KEY_FORECAST = os.getenv("DMI_API_KEY_FORECAST")


def test_new_function():
    assert new_function() == 1

from src.wind_dashapp.helper_functions import app_helper_functions as f


def test_load_dmi_observational_data():
    cell_id = "10km_620_44"
    date_from = "2025-06-20"

    df = f.load_dmi_obs_data_to_app(DMI_API_KEY_OBSERVATION, cell_id, date_from)

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns).sort() == ["cell_id", "from_datetime", "to_datetime", "parameter_id", "value"].sort()

    # Check min and max date in 'from' column
    min_date = df["from_datetime"].min().date()
    input_date = pd.to_datetime(date_from).date()
    assert min_date == input_date

def test_load_dmi_forecast_data():
    lon = 12.5683
    lat = 55.6761
    collection_type = "wind"

    df = f.load_dmi_forecast_data_to_app(DMI_API_KEY_FORECAST, lon, lat, collection_type)

    columns = ["wind-speed", "wind-dir", "timestamp", "longitude", "latitude"]
    assert isinstance(df, pd.DataFrame)
    for col in columns:
        assert col in df.columns 