"""
Google Cloud Storage Module.

Implements storage using Google Cloud Storage.
Only initialized when STORAGE_TYPE=gcs.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List
from fastapi import HTTPException, status

from app.config import settings
from app.storage.storage_interface import StorageInterface
from app.utils.logger import logger


class GCSStorage(StorageInterface):
    """
    Google Cloud Storage implementation.
    Only loads when STORAGE_TYPE=gcs environment variable is set.
    """

    def __init__(self):
        """
        Initialize GCS storage.
        Uses google-cloud-storage library.
        """
        try:
            from google.cloud import storage as gcs_storage
            self.client = gcs_storage.Client()
            self.bucket_name = settings.GCS_BUCKET
            self.bucket = self.client.bucket(self.bucket_name)
            logger.info(f"GCSStorage initialized with bucket: {self.bucket_name}")
        except ImportError:
            logger.error("google-cloud-storage not installed. Install with: pip install google-cloud-storage")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google Cloud Storage library not available."
            )
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize Google Cloud Storage: {str(e)}"
            )

    def save(self, filename: str, data: Dict[str, Any]) -> str:
        """
        Save data as JSON file to Google Cloud Storage.
        
        Args:
            filename: Name of the file to save
            data: Dictionary data to save as JSON
            
        Returns:
            The filename that was saved
        """
        try:
            blob = self.bucket.blob(filename)
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            blob.upload_from_string(json_str, content_type="application/json")
            logger.info(f"Successfully saved {filename} to GCS bucket '{self.bucket_name}'")
            return filename
        except Exception as e:
            logger.error(f"Error saving {filename} to GCS: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file to Google Cloud Storage: {str(e)}"
            )

    def list_files(self) -> List[Dict[str, Any]]:
        """
        List all JSON files in Google Cloud Storage bucket.
        
        Returns:
            List of dicts with 'name', 'size', 'created_at' keys
        """
        files: List[Dict[str, Any]] = []
        
        try:
            blobs = self.bucket.list_blobs()
            for blob in blobs:
                if blob.name.endswith(".json"):
                    created_at = (
                        blob.time_created.isoformat()
                        if blob.time_created
                        else datetime.now(timezone.utc).isoformat()
                    )
                    files.append({
                        "name": blob.name,
                        "size": blob.size or 0,
                        "created_at": created_at
                    })
            
            # Sort newest first
            files.sort(key=lambda x: x["created_at"], reverse=True)
            logger.info(f"Retrieved {len(files)} files from GCS bucket '{self.bucket_name}'")
            return files
        except Exception as e:
            logger.error(f"Error listing GCS files: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list files from Google Cloud Storage: {str(e)}"
            )

    def read_file(self, filename: str) -> Dict[str, Any]:
        """
        Read a JSON file from Google Cloud Storage.
        
        Args:
            filename: Name of the file to read
            
        Returns:
            Dictionary data from the file
            
        Raises:
            HTTPException: If file not found or invalid JSON
        """
        try:
            blob = self.bucket.blob(filename)
            if not blob.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Weather file '{filename}' not found."
                )
            
            json_str = blob.download_as_text()
            data = json.loads(json_str)
            logger.info(f"Retrieved {filename} from GCS bucket '{self.bucket_name}'")
            return data
        except HTTPException:
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error reading file '{filename}': Invalid JSON format."
            )
        except Exception as e:
            logger.error(f"Error reading {filename} from GCS: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read file from Google Cloud Storage: {str(e)}"
            )
