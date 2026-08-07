"""
FastAPI APIRouter for weather backend endpoints.
Implements:
- POST /store-weather-data
- GET /list-weather-files
- GET /weather-file-content/{filename}
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, Request, status

from app.config import settings
from app.models.weather import (
    StoreWeatherDataRequest,
    StoreWeatherDataResponse,
    ListWeatherFilesResponse,
)
from app.services.weather_service import WeatherService, weather_service
from app.utils.limiter import limiter
from app.utils.validators import sanitize_filename

router = APIRouter(tags=["Weather Data"])


@router.post(
    "/store-weather-data",
    response_model=StoreWeatherDataResponse,
    status_code=status.HTTP_200_OK,
    summary="Fetch & Store Historical Weather Data in AWS S3",
    description=(
        "Validates coordinates and date ranges (max 31 days), calls Open-Meteo "
        "Historical Weather API for daily temperature variables, stores the JSON response "
        "in AWS S3, and returns the filename."
    ),
)
@limiter.limit(settings.RATE_LIMIT_STORE)
async def store_weather_data(
    request: Request,
    body: StoreWeatherDataRequest,
    svc: WeatherService = Depends(lambda: weather_service),
) -> StoreWeatherDataResponse:
    """
    POST /store-weather-data endpoint handler with rate limiting.
    """
    return await svc.fetch_and_store_weather_data(body)


@router.get(
    "/list-weather-files",
    response_model=ListWeatherFilesResponse,
    status_code=status.HTTP_200_OK,
    summary="List Weather Data Files in S3",
    description="Returns a list of stored weather JSON files from AWS S3 with file metadata.",
)
@limiter.limit(settings.RATE_LIMIT_LIST)
def list_weather_files(
    request: Request,
    svc: WeatherService = Depends(lambda: weather_service),
) -> ListWeatherFilesResponse:
    """
    GET /list-weather-files endpoint handler with rate limiting.
    """
    return svc.list_weather_files()


@router.get(
    "/weather-file-content/{filename}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Content of Weather Data File from S3",
    description="Downloads and returns the JSON content of a specific weather file stored in AWS S3. Returns 404 if missing.",
)
@limiter.limit(settings.RATE_LIMIT_CONTENT)
def get_weather_file_content(
    request: Request,
    filename: str,
    svc: WeatherService = Depends(lambda: weather_service),
) -> Dict[str, Any]:
    """
    GET /weather-file-content/{filename} endpoint handler with rate limiting.
    """
    clean_name = sanitize_filename(filename)
    return svc.get_weather_file_content(clean_name)

