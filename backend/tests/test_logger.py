"""
Unit tests for logger module.

These tests verify specific behaviors and edge cases for the logger module.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from backend.logger import LokiLogger, logger
from backend.loki_client import LokiClientError


class TestLokiLogger:
    """Unit tests for LokiLogger class."""
    
    def test_log_generation_debug_level(self):
        """Test log generation for DEBUG level."""
        with patch('backend.logger.push_log') as mock_push_log:
            mock_push_log.return_value = True
            
            test_logger = LokiLogger()
            test_logger.debug("Debug message")
            
            # Wait for async thread
            time.sleep(0.1)
            
            mock_push_log.assert_called_once()
            args = mock_push_log.call_args
            assert args[0][0] == "Debug message"
            assert args[0][1] == "DEBUG"
    
    def test_log_generation_info_level(self):
        """Test log generation for INFO level."""
        with patch('backend.logger.push_log') as mock_push_log:
            mock_push_log.return_value = True
            
            test_logger = LokiLogger()
            test_logger.info("Info message")
            
            # Wait for async thread
            time.sleep(0.1)
            
            mock_push_log.assert_called_once()
            args = mock_push_log.call_args
            assert args[0][0] == "Info message"
            assert args[0][1] == "INFO"
    
    def test_log_generation_warning_level(self):
        """Test log generation for WARNING level."""
        with patch('backend.logger.push_log') as mock_push_log:
            mock_push_log.return_value = True
            
            test_logger = LokiLogger()
            test_logger.warning("Warning message")
            
            # Wait for async thread
            time.sleep(0.1)
            
            mock_push_log.assert_called_once()
            args = mock_push_log.call_args
            assert args[0][0] == "Warning message"
            assert args[0][1] == "WARNING"
    
    def test_log_generation_error_level(self):
        """Test log generation for ERROR level."""
        with patch('backend.logger.push_log') as mock_push_log:
            mock_push_log.return_value = True
            
            test_logger = LokiLogger()
            test_logger.error("Error message")
            
            # Wait for async thread
            time.sleep(0.1)
            
            mock_push_log.assert_called_once()
            args = mock_push_log.call_args
            assert args[0][0] == "Error message"
            assert args[0][1] == "ERROR"
    
    def test_async_log_pushing_behavior(self):
        """Test that log pushing happens asynchronously without blocking."""
        with patch('backend.logger.push_log') as mock_push_log:
            # Simulate slow push operation
            def slow_push(*args, **kwargs):
                time.sleep(0.2)
                return True
            
            mock_push_log.side_effect = slow_push
            
            test_logger = LokiLogger()
            
            # Record start time
            start_time = time.time()
            
            # Call log method - should return immediately
            test_logger.info("Test message")
            
            # Check that method returned quickly (not blocked by slow push)
            elapsed = time.time() - start_time
            assert elapsed < 0.1, "Log method should not block on async push"
            
            # Wait for async operation to complete
            time.sleep(0.3)
            
            # Verify push was called
            mock_push_log.assert_called_once()
    
    def test_fallback_to_local_logging_on_loki_failure(self):
        """Test fallback to local logging when Loki push fails."""
        with patch('backend.logger.push_log') as mock_push_log, \
             patch('backend.logger.local_logger') as mock_local_logger:
            
            # Simulate Loki failure
            mock_push_log.side_effect = LokiClientError("Loki unavailable")
            
            test_logger = LokiLogger()
            test_logger.info("Test message")
            
            # Wait for async thread
            time.sleep(0.1)
            
            # Verify local logger was used as fallback
            mock_local_logger.warning.assert_called()
            mock_local_logger.info.assert_called_with("Test message")
    
    def test_label_attachment_default_labels(self):
        """Test that default labels (app:main) are attached to all logs."""
        with patch('backend.logger.push_log') as mock_push_log:
            mock_push_log.return_value = True
            
            test_logger = LokiLogger()
            test_logger.info("Test message")
            
            # Wait for async thread
            time.sleep(0.1)
            
            mock_push_log.assert_called_once()
            args = mock_push_log.call_args
            
            # Check labels parameter
            labels = args[0][2] if len(args[0]) > 2 else args[1].get('labels')
            assert labels == {'app': 'main'}, "Default labels should be app:main"
    
    def test_label_attachment_custom_labels(self):
        """Test that custom labels can be attached to logs."""
        with patch('backend.logger.push_log') as mock_push_log:
            mock_push_log.return_value = True
            
            test_logger = LokiLogger()
            custom_labels = {'service': 'api', 'env': 'test'}
            test_logger.info("Test message", labels=custom_labels)
            
            # Wait for async thread
            time.sleep(0.1)
            
            mock_push_log.assert_called_once()
            args = mock_push_log.call_args
            
            # Check labels parameter
            labels = args[0][2] if len(args[0]) > 2 else args[1].get('labels')
            assert labels == custom_labels, "Custom labels should be passed through"
    
    def test_multiple_log_levels_in_sequence(self):
        """Test that multiple log levels can be used in sequence."""
        with patch('backend.logger.push_log') as mock_push_log:
            mock_push_log.return_value = True
            
            test_logger = LokiLogger()
            
            test_logger.debug("Debug msg")
            test_logger.info("Info msg")
            test_logger.warning("Warning msg")
            test_logger.error("Error msg")
            
            # Wait for all async threads
            time.sleep(0.2)
            
            # Verify all four calls were made
            assert mock_push_log.call_count == 4
            
            # Verify correct levels were used
            calls = mock_push_log.call_args_list
            assert calls[0][0][1] == "DEBUG"
            assert calls[1][0][1] == "INFO"
            assert calls[2][0][1] == "WARNING"
            assert calls[3][0][1] == "ERROR"
    
    def test_default_logger_instance(self):
        """Test that the default logger instance is properly initialized."""
        assert logger is not None
        assert isinstance(logger, LokiLogger)
        assert logger.default_labels == {'app': 'main'}
