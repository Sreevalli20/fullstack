"""
Storage Service.
Supports Google Cloud Storage and local file storage.
Storage type is controlled by STORAGE_TYPE environment variable.
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from app.config import settings
from app.utils.logger import logger


class StorageService:
    """
    Service for managing JSON files in Google Cloud Storage or local filesystem.
    """

    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE
        self.local_dir = settings.LOCAL_STORAGE_DIR
        self.gcs_bucket_name = settings.GCS_BUCKET
        
        # Create local directory for fallback if needed
        os.makedirs(self.local_dir, exist_ok=True)

        self._gcs_client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """
        Initializes the GCS client if STORAGE_TYPE is 'gcs'.
        Falls back to local storage if GCS credentials are not configured.
        """
        if self.storage_type == "gcs":
            try:
                from google.cloud import storage as gcs
                self._gcs_client = gcs.Client()
                logger.info(f"Initialized Google Cloud Storage client for bucket '{self.gcs_bucket_name}'")
            except Exception as e:
                logger.warning(f"Could not initialize GCS client ({e}). Falling back to local storage.")
                self._gcs_client = None
                self.storage_type = "local"
        else:
            logger.info(f"Using local storage at {self.local_dir}")
            self._gcs_client = None

    def upload_json(self, filename: str, data: Dict[str, Any]) -> str:
        """
        Uploads a Python dictionary as a JSON file to GCS (or local fallback).
        """
        json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")

        if self._gcs_client and self.storage_type == "gcs":
            try:
                bucket = self._gcs_client.bucket(self.gcs_bucket_name)
                blob = bucket.blob(filename)
                blob.upload_from_string(json_bytes, content_type="application/json")
                logger.info(f"Successfully uploaded {filename} to GCS bucket '{self.gcs_bucket_name}'")
                return filename
            except Exception as e:
                logger.warning(f"GCS upload error for {filename}: {e}. Falling back to local storage.")

        # Local fallback upload
        file_path = os.path.join(self.local_dir, filename)
        with open(file_path, "wb") as f:
            f.write(json_bytes)
        logger.info(f"Successfully saved {filename} to local storage at {file_path}")
        return filename

    def list_files(self) -> List[Dict[str, Any]]:
        """
        Lists all weather JSON files from GCS (or local fallback).
        Returns list of dicts with 'name', 'size', 'created_at'.
        """
        files: List[Dict[str, Any]] = []

        if self._gcs_client and self.storage_type == "gcs":
            try:
                bucket = self._gcs_client.bucket(self.gcs_bucket_name)
                blobs = bucket.list_blobs()
                for blob in blobs:
                    if blob.name.endswith(".json"):
                        files.append({
                            "name": blob.name,
                            "size": blob.size,
                            "created_at": blob.time_created.isoformat() if blob.time_created else datetime.now(timezone.utc).isoformat()
                        })
                # Sort newest first
                files.sort(key=lambda x: x["created_at"], reverse=True)
                logger.info(f"Retrieved {len(files)} files from GCS bucket '{self.gcs_bucket_name}'")
                return files
            except Exception as e:
                logger.warning(f"GCS list_objects error: {e}. Reading from local storage.")

        # Local fallback listing
        try:
            for fname in os.listdir(self.local_dir):
                if fname.endswith(".json"):
                    fpath = os.path.join(self.local_dir, fname)
                    stat = os.stat(fpath)
                    mod_time = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
                    files.append({
                        "name": fname,
                        "size": stat.st_size,
                        "created_at": mod_time.isoformat()
                    })
            # Sort newest first
            files.sort(key=lambda x: x["created_at"], reverse=True)
            logger.info(f"Retrieved {len(files)} files from local storage.")
            return files
        except Exception as e:
            logger.error(f"Error listing local storage files: {e}")
            return []

    def get_file_content(self, filename: str) -> Dict[str, Any]:
        """
        Downloads and parses JSON content for a file from GCS (or local fallback).
        Raises HTTP 404 if file is missing.
        """
        if self._gcs_client and self.storage_type == "gcs":
            try:
                bucket = self._gcs_client.bucket(self.gcs_bucket_name)
                blob = bucket.blob(filename)
                content_bytes = blob.download_as_bytes()
                data = json.loads(content_bytes.decode("utf-8"))
                logger.info(f"Retrieved {filename} from GCS bucket '{self.gcs_bucket_name}'")
                return data
            except Exception as e:
                logger.warning(f"GCS get_object error for {filename}: {e}. Checking local storage fallback.")

        # Local fallback download
        file_path = os.path.join(self.local_dir, filename)
        if not os.path.isfile(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Weather file '{filename}' not found."
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Retrieved {filename} from local storage.")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error reading file '{filename}': Invalid JSON format."
            )


# Global singleton instance of StorageService
storage_service = StorageService()
