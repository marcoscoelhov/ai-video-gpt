"""Configuration modules for AI Video GPT.

This package contains configuration and client setup:
- setup_gemini: Gemini API configuration
- gemini_imagen_client: Gemini Imagen client setup
- gemini_subtitle_client: Gemini subtitle client setup
"""

# Import centralized configuration functions
import sys
import os

# Add parent directory to path to import config.py
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from src.config import (
        validate_configuration,
        print_configuration_status,
        get_output_directories
    )
except ImportError:
    # Fallback: define minimal functions
    def validate_configuration():
        return {'valid': True, 'errors': [], 'warnings': [], 'services_available': {}}
    
    def print_configuration_status():
        print("Configuration status not available")
    
    def get_output_directories():
        return {
            'videos': 'outputs/videos',
            'images': 'outputs/images',
            'audio': 'outputs/audio',
            'subtitles': 'outputs/subtitles'
        }