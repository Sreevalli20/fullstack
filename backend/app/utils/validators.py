"""
Custom validator utilities for coordinate and filename validation.
"""

import re
from datetime import date
from fastapi import HTTPException, status


def validate_coordinates(latitude: float, longitude: float) -> None:
    """
    Validates latitude and longitude parameters.
    Latitude: [-90, 90]
    Longitude: [-180, 180]
    """
    if not (-90.0 <= latitude <= 90.0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid latitude: {latitude}. Must be between -90 and 90."
        )
    if not (-180.0 <= longitude <= 180.0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid longitude: {longitude}. Must be between -180 and 180."
        )


def validate_date_range(start_date: date, end_date: date, max_days: int = 31) -> None:
    """
    Validates start and end dates.
    Ensures start_date <= end_date and difference <= max_days.
    """
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"start_date ({start_date}) must be before or equal to end_date ({end_date})."
        )
    
    diff_days = (end_date - start_date).days
    if diff_days > max_days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requested date range ({diff_days} days) exceeds maximum allowed limit of {max_days} days."
        )


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes filename to prevent directory traversal or invalid character injection.
    """
    # Remove path slashes or parent directory indicators
    clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '', filename)
    if not clean_name or clean_name.startswith('.'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename provided."
        )
    return clean_name
