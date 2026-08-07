"""
Root config module re-exporting Settings from app.config.
Allows importing `from config import settings`.
"""

from app.config import Settings, settings

__all__ = ["Settings", "settings"]
