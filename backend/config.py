"""
Configuration module for the Log Query System backend.

This module centralizes all configuration settings including Loki endpoints,
default labels, and environment variable support.
"""

import os


class Config:
    """Configuration class for backend settings."""
    
    # Loki base URL - can be overridden by environment variable
    LOKI_URL = os.environ.get('LOKI_URL', 'http://localhost:3100')
    
    # Loki API endpoints
    LOKI_PUSH_ENDPOINT = '/loki/api/v1/push'
    LOKI_QUERY_ENDPOINT = '/loki/api/v1/query_range'
    LOKI_LABELS_ENDPOINT = '/loki/api/v1/labels'
    
    # Default label for queries and logging
    DEFAULT_LABEL = 'app:main'
    
    # Application log level
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Flask configuration
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def get_loki_push_url(cls):
        """Get the complete Loki push URL."""
        return f"{cls.LOKI_URL}{cls.LOKI_PUSH_ENDPOINT}"
    
    @classmethod
    def get_loki_query_url(cls):
        """Get the complete Loki query URL."""
        return f"{cls.LOKI_URL}{cls.LOKI_QUERY_ENDPOINT}"
    
    @classmethod
    def get_loki_labels_url(cls):
        """Get the complete Loki labels URL."""
        return f"{cls.LOKI_URL}{cls.LOKI_LABELS_ENDPOINT}"
    
    @classmethod
    def get_loki_label_values_url(cls, label_name: str):
        """Get the complete Loki label values URL for a specific label."""
        return f"{cls.LOKI_URL}/loki/api/v1/label/{label_name}/values"


# Create a default config instance for easy import
config = Config()
