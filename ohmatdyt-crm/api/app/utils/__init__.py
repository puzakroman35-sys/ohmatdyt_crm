"""
Utility modules for the application

BE-015: This package provides logging utilities.
File utilities are in the parent utils.py module for backward compatibility.
"""

# BE-015: Import logging utilities
from .logging_config import (
    setup_logging,
    get_logger,
    set_request_id,
    get_request_id,
    clear_request_id,
)

# Re-export utilities from app.utils module (file)
# This handles the conflict between app/utils.py and app/utils/ package
try:
    # Import from sibling utils.py file
    import sys
    from pathlib import Path
    
    # Get the app directory
    app_dir = Path(__file__).parent.parent
    utils_py = app_dir / 'utils.py'
    
    if utils_py.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("_app_utils_file", str(utils_py))
        if spec and spec.loader:
            _utils_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_utils_module)
            
            # Export file utilities
            generate_unique_public_id = _utils_module.generate_unique_public_id
            validate_file_type = _utils_module.validate_file_type
            validate_file_size = _utils_module.validate_file_size
            get_file_storage_path = _utils_module.get_file_storage_path
            sanitize_filename = _utils_module.sanitize_filename
            MAX_FILE_SIZE_BYTES = _utils_module.MAX_FILE_SIZE_BYTES
            ALLOWED_MIME_TYPES = _utils_module.ALLOWED_MIME_TYPES
            ALLOWED_EXTENSIONS = _utils_module.ALLOWED_EXTENSIONS
except Exception as e:
    # If import fails, define None placeholders
    import warnings
    warnings.warn(f"Could not import from utils.py: {e}")
    generate_unique_public_id = None
    validate_file_type = None
    validate_file_size = None
    get_file_storage_path = None
    sanitize_filename = None

__all__ = [
    # Logging utilities (BE-015)
    'setup_logging',
    'get_logger',
    'set_request_id',
    'get_request_id',
    'clear_request_id',
    # File utilities (from utils.py)
    'generate_unique_public_id',
    'validate_file_type',
    'validate_file_size',
    'get_file_storage_path',
    'sanitize_filename',
    'MAX_FILE_SIZE_BYTES',
    'ALLOWED_MIME_TYPES',
    'ALLOWED_EXTENSIONS',
]
