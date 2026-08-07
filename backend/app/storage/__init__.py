"""
Storage Factory Module.
"""
from .local_storage import LocalStorage
from .gcs_storage import GCSStorage
from .storage_interface import StorageInterface
import os


def get_storage() -> StorageInterface:
    """
    Factory function to get storage implementation based on environment variable.
    
    Environment Variables:
        STORAGE_TYPE: "local" (default) or "gcs"
        LOCAL_STORAGE_PATH: Path for local storage (default: from settings)
    
    Returns:
        StorageInterface implementation instance
    """
    storage_type = os.getenv("STORAGE_TYPE", "local")
    
    if storage_type == "gcs":
        return GCSStorage()
    
    return LocalStorage()


__all__ = ["get_storage", "StorageInterface", "LocalStorage", "GCSStorage"]
