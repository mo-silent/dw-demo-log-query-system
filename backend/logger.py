"""
Logger module for the Log Query System backend.

This module provides logging functionality that pushes logs to Loki asynchronously
with automatic labeling and fallback to local logging if Loki is unavailable.
"""

import logging
import threading
from typing import Optional, Dict
from loki_client import push_log, LokiClientError
from config import config


# Configure local fallback logger
local_logger = logging.getLogger('log_query_system')
local_logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))

# Add console handler if not already present
if not local_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    local_logger.addHandler(handler)


class LokiLogger:
    """
    Logger that pushes logs to Loki asynchronously with fallback to local logging.
    
    All logs are automatically tagged with "app: main" label.
    Supports log levels: DEBUG, INFO, WARNING, ERROR.
    """
    
    def __init__(self):
        """Initialize the Loki logger."""
        self.default_labels = self._parse_default_label()
    
    def _parse_default_label(self) -> Dict[str, str]:
        """
        Parse the default label from config into a dictionary.
        
        Returns:
            Dict[str, str]: Label dictionary
        """
        if ':' in config.DEFAULT_LABEL:
            key, value = config.DEFAULT_LABEL.split(':', 1)
            return {key: value}
        return {'label': config.DEFAULT_LABEL}
    
    def _push_to_loki_async(
        self,
        message: str,
        level: str,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Push log to Loki in a separate thread to avoid blocking.
        
        Args:
            message: Log message content
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            labels: Optional custom labels (defaults to app:main)
        """
        def push_task():
            try:
                # Use default labels if none provided
                log_labels = labels if labels is not None else self.default_labels
                push_log(message, level, log_labels)
            except LokiClientError as e:
                # Fallback to local logging on Loki failure
                local_logger.warning(
                    f"Failed to push log to Loki, logged locally: {str(e)}"
                )
                # Log the original message locally
                log_method = getattr(local_logger, level.lower(), local_logger.info)
                log_method(message)
        
        # Start async push in background thread
        thread = threading.Thread(target=push_task, daemon=True)
        thread.start()
    
    def debug(self, message: str, labels: Optional[Dict[str, str]] = None):
        """
        Log a DEBUG level message.
        
        Args:
            message: Log message content
            labels: Optional custom labels (defaults to app:main)
        """
        self._push_to_loki_async(message, 'DEBUG', labels)
    
    def info(self, message: str, labels: Optional[Dict[str, str]] = None):
        """
        Log an INFO level message.
        
        Args:
            message: Log message content
            labels: Optional custom labels (defaults to app:main)
        """
        self._push_to_loki_async(message, 'INFO', labels)
    
    def warning(self, message: str, labels: Optional[Dict[str, str]] = None):
        """
        Log a WARNING level message.
        
        Args:
            message: Log message content
            labels: Optional custom labels (defaults to app:main)
        """
        self._push_to_loki_async(message, 'WARNING', labels)
    
    def error(self, message: str, labels: Optional[Dict[str, str]] = None):
        """
        Log an ERROR level message.
        
        Args:
            message: Log message content
            labels: Optional custom labels (defaults to app:main)
        """
        self._push_to_loki_async(message, 'ERROR', labels)


# Create a default logger instance for easy import
logger = LokiLogger()
