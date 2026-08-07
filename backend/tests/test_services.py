"""
Unit tests for WeatherService and storage implementations with mocked dependencies.
"""

import json
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import HTTPException

from app.models.weather import StoreWeatherDataRequest
from app.services.weather_service import WeatherService
from app.storage.storage_interface import StorageInterface


@pytest.fixture
def mock_storage():
    service = MagicMock(spec=StorageInterface)
    service.save.return_value = "weather_37.7749_-122.4194_2024-01-01_2024-01-05_12345678.json"
    service.list_files.return_value = [
        {"name": "test_file.json", "size": 1024, "created_at": "2026-08-06T12:00:00+00:00"}
    ]
    service.read_file.return_value = {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "daily": {
            "time": ["2024-01-01"],
            "temperature_2m_max": [15.2],
            "temperature_2m_min": [8.1]
        }
    }
    return service


@pytest.mark.asyncio
async def test_weather_service_fetch_and_store_success(mock_storage):
    service = WeatherService(storage=mock_storage)
    request_data = StoreWeatherDataRequest(
        latitude=37.7749,
        longitude=-122.4194,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 5),
    )

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

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_httpx_response
        result = await service.fetch_and_store_weather_data(request_data)

        assert result.status == "ok"
        assert result.file.startswith("weather_37.7749_-122.4194_2024-01-01_2024-01-05_")
        assert result.file.endswith(".json")
        mock_storage.save.assert_called_once()


@pytest.mark.asyncio
async def test_weather_service_fetch_open_meteo_error(mock_storage):
    service = WeatherService(storage=mock_storage)
    request_data = StoreWeatherDataRequest(
        latitude=37.7749,
        longitude=-122.4194,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 5),
    )

    mock_httpx_response = MagicMock()
    mock_httpx_response.status_code = 500
    mock_httpx_response.text = "Internal Open-Meteo Error"

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_httpx_response
        with pytest.raises(HTTPException) as exc_info:
            await service.fetch_and_store_weather_data(request_data)
        assert exc_info.value.status_code == 502


def test_local_storage(tmp_path):
    # Test LocalStorage with local storage directory
    from app.storage.local_storage import LocalStorage
    
    storage = LocalStorage(storage_dir=str(tmp_path))

    # Test Save
    filename = "test_weather.json"
    content = {"location": "San Francisco", "temp": 18.5}
    saved_file = storage.save(filename, content)
    assert saved_file == filename

    # Test Listing
    files = storage.list_files()
    assert len(files) == 1
    assert files[0]["name"] == filename

    # Test Retrieval
    retrieved = storage.read_file(filename)
    assert retrieved["location"] == "San Francisco"


def test_local_storage_not_found(tmp_path):
    from app.storage.local_storage import LocalStorage
    from fastapi import HTTPException
    import pytest
    
    storage = LocalStorage(storage_dir=str(tmp_path))

    with pytest.raises(HTTPException) as exc_info:
        storage.read_file("non_existent_file.json")
    assert exc_info.value.status_code == 404
