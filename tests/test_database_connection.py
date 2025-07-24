import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv
import os
import pytest

load_dotenv()

DB_NAME = "weather"
DB_USER = "weather_user"
DB_PASSWORD = os.getenv("DB_WEATHER_PASSWORD")
DB_HOST = "localhost"
DB_PORT = "5432"

@pytest.mark.skip(reason="Database currently not used")
def test_database_connection():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn.close()
    except OperationalError as e:
        pytest.fail(f"Failed to connect to the PostgreSQL database: {e}") 