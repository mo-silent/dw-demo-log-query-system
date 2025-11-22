"""
Property-based tests for logger module.

These tests verify universal properties that should hold across all inputs
using Hypothesis for property-based testing.
"""

import pytest
import time
from unittest.mock import Mock, patch, call
from hypothesis import given, strategies as st, settings
from backend.logger import LokiLogger
from backend.config import config


# Feature: log-query-system, Property 10: Backend operations generate logs
# Validates: Requirements 4.1
@settings(max_examples=100)
@given(
    message=st.text(min_size=1, max_size=200),
    level=st.sampled_from(['debug', 'info', 'warning', 'error'])
)
@patch('backend.logger.push_log')
def test_property_backend_operations_generate_logs(mock_push_log, message, level):
    """
    Property 10: Backend operations generate logs
    
    For any backend operation (API request, Loki query, error), the backend 
    should generate a corresponding log entry.
    """
    # Setup mock to succeed
    mock_push_log.return_value = True
    
    # Create logger instance
    logger = LokiLogger()
    
    # Execute: Call the appropriate log method
    log_method = getattr(logger, level)
    log_method(message)
    
    # Give async thread time to execute
    time.sleep(0.1)
    
    # Verify: Backend should generate a log entry for the operation
    assert mock_push_log.called, \
        f"Backend should generate a log entry when {level} operation occurs"
    
    # Verify the log was pushed with correct message and level
    call_args = mock_push_log.call_args
    assert call_args is not None, "push_log should have been called"
    
    # Check message was passed
    assert call_args[0][0] == message or call_args[1].get('message') == message, \
        "Log message should match the operation message"
    
    # Check level was passed (uppercase)
    level_arg = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get('level')
    assert level_arg == level.upper(), \
        f"Log level should be {level.upper()}"


# Feature: log-query-system, Property 12: Backend logs labeled correctly
# Validates: Requirements 4.3
@settings(max_examples=100)
@given(
    message=st.text(min_size=1, max_size=200),
    level=st.sampled_from(['debug', 'info', 'warning', 'error'])
)
@patch('backend.logger.push_log')
def test_property_backend_logs_labeled_correctly(mock_push_log, message, level):
    """
    Property 12: Backend logs labeled correctly
    
    For any log pushed by the backend to Loki, the log should include 
    the label "app: main".
    """
    # Setup mock to succeed
    mock_push_log.return_value = True
    
    # Create logger instance
    logger = LokiLogger()
    
    # Execute: Call the appropriate log method without custom labels
    log_method = getattr(logger, level)
    log_method(message)
    
    # Give async thread time to execute
    time.sleep(0.1)
    
    # Verify: Backend should push log with correct labels
    assert mock_push_log.called, "Backend should push log to Loki"
    
    call_args = mock_push_log.call_args
    
    # Extract labels argument
    labels_arg = None
    if len(call_args[0]) > 2:
        labels_arg = call_args[0][2]
    elif 'labels' in call_args[1]:
        labels_arg = call_args[1]['labels']
    
    # When no custom labels are provided, logger should use default labels
    # Default labels should be {'app': 'main'} based on config.DEFAULT_LABEL
    expected_labels = {'app': 'main'}
    
    assert labels_arg == expected_labels, \
        f"Backend logs should be labeled with 'app: main', but got {labels_arg}"

