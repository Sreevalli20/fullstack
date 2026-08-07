"""
Weather Service Module.

Handles calls to Open-Meteo Historical Weather API using async httpx
and integrates with S3 Storage Service to persist response JSON files.
"""

import time
from typing import Any, Dict, List
import httpx
from fastapi import HTTPException, status

from app.config import settings
from app.models.weather import (
    StoreWeatherDataRequest,
    StoreWeatherDataResponse,
    ListWeatherFilesResponse,
    WeatherFileInfo,
)
from app.storage.s3_service import s3_storage_service as default_s3_storage_service
from app.utils.logger import logger


class WeatherService:
    """
    Service responsible for fetching historical weather data and managing files.
    """

    def __init__(self, s3_service=None):
        self.base_url = settings.OPEN_METEO_BASE_URL
        self.storage_service = s3_service or default_s3_storage_service

    async def fetch_and_store_weather_data(
        self, request: StoreWeatherDataRequest
    ) -> StoreWeatherDataResponse:
        """
        Fetches historical weather data from Open-Meteo API and stores the JSON in S3.
        """
        lat = request.latitude
        lon = request.longitude
        start_str = request.start_date.isoformat()
        end_str = request.end_date.isoformat()

        # Build query parameters for Open-Meteo API
        # Note: Open-Meteo requires daily variables as a comma-separated string
        daily_vars = [
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "apparent_temperature_min",
        ]

        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_str,
            "end_date": end_str,
            "daily": ",".join(daily_vars),
            "timezone": "auto",
        }

        logger.info(
            f"Fetching Open-Meteo weather data for lat={lat}, lon={lon}, range={start_str} to {end_str}"
        )

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(self.base_url, params=params)

            if response.status_code != 200:
                logger.error(
                    f"Open-Meteo API error ({response.status_code}): {response.text}"
                )
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Open-Meteo API returned error status {response.status_code}: {response.text}"
                )

            weather_json = response.json()

        except httpx.TimeoutException:
            logger.error("Open-Meteo API request timed out.")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request to Open-Meteo Weather API timed out."
            )
        except httpx.RequestError as exc:
            logger.error(f"Network error communicating with Open-Meteo API: {exc}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to communicate with Open-Meteo API: {str(exc)}"
            )

        # Construct S3 filename: weather_<lat>_<lon>_<start>_<end>_<timestamp>.json
        timestamp = int(time.time())
        filename = f"weather_{lat}_{lon}_{start_str}_{end_str}_{timestamp}.json"

        # Store complete JSON response in AWS S3
        self.storage_service.upload_json(filename, weather_json)

        return StoreWeatherDataResponse(status="ok", file=filename)

    def list_weather_files(self) -> ListWeatherFilesResponse:
        """
        Lists stored weather JSON files from S3.
        """
        raw_files = self.storage_service.list_files()
        file_infos = [
            WeatherFileInfo(
                name=f["name"],
                size=f["size"],
                created_at=f["created_at"]
            )
            for f in raw_files
        ]
        return ListWeatherFilesResponse(files=file_infos)

    def get_weather_file_content(self, filename: str) -> Dict[str, Any]:
        """
        Downloads and returns JSON content for a stored weather file.
        """
        return self.storage_service.get_file_content(filename)


# Global singleton instance of WeatherService
weather_service = WeatherService()
