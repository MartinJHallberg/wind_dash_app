import pytest
from src.data_processing.dmi import (
    get_dmi_forecast_data,
    extract_and_parse_forecast_data,
    get_dmi_observational_data,
    extract_and_parse_observational_data
)
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

DMI_API_KEY_OBSERVATION = os.getenv("DMI_API_KEY_OBSERVATION")
DMI_API_KEY_FORECAST = os.getenv("DMI_API_KEY_FORECAST")


def test_get_dmi_forecast_data():
    lon = 12.5683
    lat = 55.6761
    collection_type = "wind"

    json_response = get_dmi_forecast_data(DMI_API_KEY_FORECAST, lon, lat, collection_type)

    assert json_response is not None

def test_extract_and_parse_forecast_data_minimal():
    # Minimal mock JSON response with the required structure
    mock_json = {
        "domain": {
            "axes": {
                "t": {"values": ["2025-07-22T09:00:00.000Z", "2025-07-22T10:00:00.000Z"]},
                "x": {"values": [12.5]},
                "y": {"values": [55.6]}
            }
        },
        "ranges": {
            "wind-speed": {
                "values": [5.0, 6.0]
            },
            "wind-dir": {
                "values": [90.0, 100.0]
            }
        }
    }
    parameters = ["wind-speed", "wind-dir"]

    df = extract_and_parse_forecast_data(mock_json, parameters)

    # Check DataFrame shape and columns
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["wind-speed", "wind-dir", "timestamp", "longitude", "latitude"]
    assert df.shape == (2, 5)
    assert df["wind-speed"].tolist() == [5.0, 6.0]


def test_get_dmi_forecast_data_integration():
    lon = 12.5683
    lat = 55.6761
    collection_type = "wind"

    json_response = get_dmi_forecast_data(DMI_API_KEY_FORECAST, lon, lat, collection_type)

    df = extract_and_parse_forecast_data(json_response, ["wind-speed", "wind-dir"])

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["wind-speed", "wind-dir", "timestamp", "longitude", "latitude"]


def test_get_dmi_observational_data_integration():
    cell_id = "10km_620_44"
    date_from = "2025-07-20"
    date_to = "2025-07-21"
    json_response = get_dmi_observational_data(DMI_API_KEY_OBSERVATION, cell_id, date_from, date_to)
    df = extract_and_parse_observational_data(json_response)
    
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["cell_id", "from", "to", "parameter_id", "value"]
