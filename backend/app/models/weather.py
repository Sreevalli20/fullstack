"""
Pydantic schemas and validators for weather data requests and responses.
"""

from datetime import date, datetime
from typing import List
from pydantic import BaseModel, Field, field_validator, model_validator


class StoreWeatherDataRequest(BaseModel):
    """
    Request body schema for storing weather data.
    Validates coordinates and date ranges.
    """
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitude must be between -90 and 90",
        examples=[37.7749]
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude must be between -180 and 180",
        examples=[-122.4194]
    )
    start_date: date = Field(
        ...,
        description="Start date in YYYY-MM-DD format",
        examples=["2024-01-01"]
    )
    end_date: date = Field(
        ...,
        description="End date in YYYY-MM-DD format",
        examples=["2024-01-15"]
    )

    @model_validator(mode="after")
    def validate_date_range(self) -> "StoreWeatherDataRequest":
        """
        Ensures start_date <= end_date and maximum date range is 31 days.
        """
        if self.start_date > self.end_date:
            raise ValueError("start_date must be less than or equal to end_date")

        date_diff = (self.end_date - self.start_date).days
        if date_diff > 31:
            raise ValueError(f"Maximum date range is 31 days. Requested range is {date_diff} days.")

        return self


class StoreWeatherDataResponse(BaseModel):
    """
    Response schema for POST /store-weather-data endpoint.
    """
    status: str = Field(default="ok", description="Status indicator")
    file: str = Field(..., description="Name of the stored JSON file")


class WeatherFileInfo(BaseModel):
    """
    Metadata info for a single weather file stored in storage.
    """
    name: str = Field(..., description="Filename")
    size: int = Field(..., description="File size in bytes")
    created_at: str = Field(..., description="Creation date/time in ISO8601 format")


class ListWeatherFilesResponse(BaseModel):
    """
    Response schema for GET /list-weather-files endpoint.
    """
    files: List[WeatherFileInfo] = Field(
        default_factory=list,
        description="List of stored weather files metadata"
    )
