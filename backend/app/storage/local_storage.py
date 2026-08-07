"""
Local Storage Module.

Implements file-based storage using local filesystem.
Stores JSON files in a local directory.
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List
from fastapi import HTTPException, status

from app.config import settings
from app.storage.storage_interface import StorageInterface
from app.utils.logger import logger


class LocalStorage(StorageInterface):
    """
    Local filesystem storage implementation.
    """

    def __init__(self, storage_dir: str = None):
        """
        Initialize local storage.
        
        Args:
            storage_dir: Directory path for storing files. Defaults to settings.LOCAL_STORAGE_DIR
        """
        self.storage_dir = storage_dir or settings.LOCAL_STORAGE_DIR
        os.makedirs(self.storage_dir, exist_ok=True)
        logger.info(f"LocalStorage initialized with directory: {self.storage_dir}")

    def save(self, filename: str, data: Dict[str, Any]) -> str:
        """
        Save data as JSON file to local storage.
        
        Args:
            filename: Name of the file to save
            data: Dictionary data to save as JSON
            
        Returns:
            The filename that was saved
        """
        file_path = os.path.join(self.storage_dir, filename)
        json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        
        with open(file_path, "wb") as f:
            f.write(json_bytes)
        
        logger.info(f"Successfully saved {filename} to local storage at {file_path}")
        return filename

    def list_files(self) -> List[Dict[str, Any]]:
        """
        List all JSON files in local storage.
        
        Returns:
            List of dicts with 'name', 'size', 'created_at' keys
        """
        files: List[Dict[str, Any]] = []
        
        try:
            for fname in os.listdir(self.storage_dir):
                if fname.endswith(".json"):
                    fpath = os.path.join(self.storage_dir, fname)
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

    def read_file(self, filename: str) -> Dict[str, Any]:
        """
        Read a JSON file from local storage.
        
        Args:
            filename: Name of the file to read
            
        Returns:
            Dictionary data from the file
            
        Raises:
            HTTPException: If file not found or invalid JSON
        """
        file_path = os.path.join(self.storage_dir, filename)
        
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
