"""
Integration tests for FastAPI endpoints.
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "weather-data-backend"


def test_store_weather_data_validation_error_date_range():
    # End date before start date
    payload = {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "start_date": "2024-01-10",
        "end_date": "2024-01-01"
    }
    response = client.post("/store-weather-data", json=payload)
    assert response.status_code == 422


def test_store_weather_data_validation_error_exceeds_31_days():
    # Date range > 31 days
    payload = {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "start_date": "2024-01-01",
        "end_date": "2024-02-15"
    }
    response = client.post("/store-weather-data", json=payload)
    assert response.status_code == 422


def test_store_weather_data_validation_error_invalid_coords():
    # Latitude > 90
    payload = {
        "latitude": 120.0,
        "longitude": -122.4194,
        "start_date": "2024-01-01",
        "end_date": "2024-01-10"
    }
    response = client.post("/store-weather-data", json=payload)
    assert response.status_code == 422


def test_store_weather_data_success():
    fake_open_meteo_response = {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "timezone": "UTC",
        "daily": {
            "time": ["2024-01-01", "2024-01-02"],
            "temperature_2m_max": [15.2, 16.0],
            "temperature_2m_min": [8.1, 8.5],
            "apparent_temperature_max": [14.0, 15.1],
            "apparent_temperature_min": [7.0, 7.8],
        },
    }

    mock_httpx_response = MagicMock()
    mock_httpx_response.status_code = 200
    mock_httpx_response.json.return_value = fake_open_meteo_response

    payload = {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "start_date": "2024-01-01",
        "end_date": "2024-01-05"
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_httpx_response
        response = client.post("/store-weather-data", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "file" in data


def test_list_weather_files():
    response = client.get("/list-weather-files")
    assert response.status_code == 200
    data = response.json()
    assert "files" in data
    assert isinstance(data["files"], list)


def test_get_weather_file_content_not_found():
    response = client.get("/weather-file-content/non_existent_file_xyz.json")
    assert response.status_code == 404
