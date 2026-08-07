"""
S3 Storage Service.
Interacts with AWS S3 using boto3.
Supports upload, list, and download of weather JSON files.
Includes seamless local fallback for local development when AWS credentials are not configured.
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import boto3
from botocore.exceptions import ClientError, BotoCoreError, NoCredentialsError
from fastapi import HTTPException, status

from app.config import settings
from app.utils.logger import logger


class S3StorageService:
    """
    Service for managing JSON files in AWS S3 using boto3.
    """

    def __init__(self):
        self.bucket_name = settings.S3_BUCKET
        self.region = settings.AWS_REGION
        self.aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        self.aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        self.local_dir = settings.LOCAL_STORAGE_DIR

        # Create local directory for fallback if needed
        os.makedirs(self.local_dir, exist_ok=True)

        self._s3_client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """
        Initializes the boto3 S3 client using explicit credentials if provided,
        or falling back to boto3 default credential provider chain (IAM Roles / AWS CLI / Env vars).
        Falls back gracefully to local storage mode if AWS credentials are not configured.
        """
        try:
            if self.aws_access_key_id and self.aws_secret_access_key:
                self._s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    region_name=self.region,
                )
                logger.info(f"Initialized AWS S3 Client with provided keys for bucket '{self.bucket_name}' in region '{self.region}'")
            else:
                session = boto3.Session(region_name=self.region)
                credentials = session.get_credentials()
                if credentials and credentials.access_key:
                    self._s3_client = session.client("s3")
                    logger.info(f"Initialized AWS S3 Client via default credential chain for bucket '{self.bucket_name}' in region '{self.region}'")
                else:
                    self._s3_client = None
                    logger.info("AWS credentials not configured. Operating in local storage fallback mode.")
        except Exception as e:
            logger.info(f"Could not initialize boto3 S3 client ({e}). Operating in local storage mode.")
            self._s3_client = None

    def upload_json(self, filename: str, data: Dict[str, Any]) -> str:
        """
        Uploads a Python dictionary as a JSON file to S3 (or local fallback).
        """
        json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")

        if self._s3_client:
            try:
                self._s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=filename,
                    Body=json_bytes,
                    ContentType="application/json",
                )
                logger.info(f"Successfully uploaded {filename} to S3 bucket '{self.bucket_name}'")
                return filename
            except NoCredentialsError as e:
                logger.info(f"AWS credentials unavailable ({e}). Disabling S3 client and saving to local storage.")
                self._s3_client = None
            except (ClientError, BotoCoreError) as e:
                logger.warning(f"S3 upload error for {filename}: {e}. Falling back to local storage.")

        # Local fallback upload
        file_path = os.path.join(self.local_dir, filename)
        with open(file_path, "wb") as f:
            f.write(json_bytes)
        logger.info(f"Successfully saved {filename} to local storage at {file_path}")
        return filename

    def list_files(self) -> List[Dict[str, Any]]:
        """
        Lists all weather JSON files from S3 (or local fallback).
        Returns list of dicts with 'name', 'size', 'created_at'.
        """
        files: List[Dict[str, Any]] = []

        if self._s3_client:
            try:
                response = self._s3_client.list_objects_v2(Bucket=self.bucket_name)
                contents = response.get("Contents", [])
                for obj in contents:
                    key = obj.get("Key", "")
                    if key.endswith(".json"):
                        created_at = obj.get("LastModified")
                        iso_date = (
                            created_at.isoformat()
                            if isinstance(created_at, datetime)
                            else datetime.now(timezone.utc).isoformat()
                        )
                        files.append({
                            "name": key,
                            "size": obj.get("Size", 0),
                            "created_at": iso_date
                        })
                logger.info(f"Retrieved {len(files)} files from S3 bucket '{self.bucket_name}'")
                return files
            except NoCredentialsError as e:
                logger.info(f"AWS credentials unavailable ({e}). Disabling S3 client and reading from local storage.")
                self._s3_client = None
            except (ClientError, BotoCoreError) as e:
                logger.warning(f"S3 list_objects error: {e}. Reading from local storage.")

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
        Downloads and parses JSON content for a file from S3 (or local fallback).
        Raises HTTP 404 if file is missing.
        """
        if self._s3_client:
            try:
                response = self._s3_client.get_object(Bucket=self.bucket_name, Key=filename)
                content_bytes = response["Body"].read()
                data = json.loads(content_bytes.decode("utf-8"))
                logger.info(f"Retrieved {filename} from S3 bucket '{self.bucket_name}'")
                return data
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "")
                if error_code in ("NoSuchKey", "404"):
                    logger.warning(f"File '{filename}' not found in S3 bucket '{self.bucket_name}'")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Weather file '{filename}' not found."
                    )
                logger.warning(f"S3 get_object error for {filename}: {e}. Checking local storage fallback.")
            except NoCredentialsError as e:
                logger.info(f"AWS credentials unavailable ({e}). Disabling S3 client and checking local storage.")
                self._s3_client = None
            except BotoCoreError as e:
                logger.warning(f"S3 get_object error for {filename}: {e}. Checking local storage fallback.")
            except HTTPException:
                raise
            except Exception as e:
                logger.warning(f"Unexpected error getting object {filename} from S3: {e}")

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


# Global singleton instance of S3StorageService
s3_storage_service = S3StorageService()
