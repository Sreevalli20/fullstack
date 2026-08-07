"""
Storage Interface Module.

Defines abstract base class for storage implementations.
All storage backends must implement these methods.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class StorageInterface(ABC):
    """
    Abstract base class for storage implementations.
    """

    @abstractmethod
    def save(self, filename: str, data: Dict[str, Any]) -> str:
        """
        Save data to storage.
        
        Args:
            filename: Name of the file to save
            data: Dictionary data to save as JSON
            
        Returns:
            The filename that was saved
        """
        pass

    @abstractmethod
    def list_files(self) -> List[Dict[str, Any]]:
        """
        List all files in storage.
        
        Returns:
            List of dicts with 'name', 'size', 'created_at' keys
        """
        pass

    @abstractmethod
    def read_file(self, filename: str) -> Dict[str, Any]:
        """
        Read a file from storage.
        
        Args:
            filename: Name of the file to read
            
        Returns:
            Dictionary data from the file
        """
        pass
