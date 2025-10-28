"""
Ohmatdyt CRM API Application
"""

__version__ = "0.1.0"

from .main import app, settings
from .celery_app import celery

__all__ = ["app", "celery", "settings"]