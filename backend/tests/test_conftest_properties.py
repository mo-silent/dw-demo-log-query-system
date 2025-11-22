"""
Property-based tests for pytest configuration and test logging.

Feature: log-query-system, Property 13: Test execution generates logs
Validates: Requirements 5.3
"""

import pytest
import time
from unittest.mock import patch, MagicMock, call
from hypothesis import given, strategies as st, settings
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestTestLoggingProperties:
    """Property-based tests for test execution logging."""
    
    @given(
        test_name=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65),
            min_size=5,
            max_size=50
        )
    )
    @settings(max_examples=100)
    def test_property_test_execution_generates_logs(self, test_name):
        """
        Feature: log-query-system, Property 13: Test execution generates logs
        
        Property: For any unit test execution, the backend should push test execution 
        logs to Loki with label "app: main".
        
        This test verifies that when tests run, the pytest hooks in conftest.py
        generate appropriate log entries that are pushed to Loki.
        
        Validates: Requirements 5.3
        """
        from backend.logger import logger
        
        # Mock the logger to capture log calls
        with patch.object(logger, '_push_to_loki_async') as mock_push:
            # Simulate test lifecycle by calling the hooks directly
            from conftest import pytest_runtest_setup, pytest_runtest_logreport
            
            # Create mock test item
            mock_item = MagicMock()
            mock_item.nodeid = f"tests/test_example.py::TestClass::{test_name}"
            
            # Call setup hook (test started)
            pytest_runtest_setup(mock_item)
            
            # Verify setup log was generated
            assert mock_push.call_count >= 1, "Test setup should generate at least one log"
            
            # Get the first call arguments
            first_call = mock_push.call_args_list[0]
            message = first_call[0][0]
            level = first_call[0][1]
            labels = first_call[0][2] if len(first_call[0]) > 2 else None
            
            # Verify log message contains test name
            assert test_name in message or mock_item.nodeid in message, \
                "Log message should contain test name"
            
            # Verify log level is appropriate (INFO for test start)
            assert level in ['INFO', 'DEBUG', 'WARNING', 'ERROR'], \
                "Log level should be valid"
            
            # Verify labels include app:main
            if labels is not None:
                assert labels == {'app': 'main'}, \
                    "Test logs should be labeled with app:main"
            
            # Reset mock for next phase
            mock_push.reset_mock()
            
            # Create mock report for passed test
            mock_report = MagicMock()
            mock_report.nodeid = mock_item.nodeid
            mock_report.when = 'call'
            mock_report.passed = True
            mock_report.failed = False
            mock_report.skipped = False
            
            # Call report hook (test result)
            pytest_runtest_logreport(mock_report)
            
            # Verify result log was generated
            assert mock_push.call_count >= 1, "Test result should generate at least one log"
            
            # Verify result log contains test name
            result_call = mock_push.call_args_list[0]
            result_message = result_call[0][0]
            assert test_name in result_message or mock_item.nodeid in result_message, \
                "Result log should contain test name"
    
    @given(
        exit_code=st.integers(min_value=0, max_value=5)
    )
    @settings(max_examples=100, deadline=1000)
    def test_property_session_logging_generates_logs(self, exit_code):
        """
        Feature: log-query-system, Property 13: Test execution generates logs
        
        Property: For any test session (start/finish), the backend should push 
        session logs to Loki with label "app: main".
        
        This test verifies that test session lifecycle events generate appropriate
        log entries.
        
        Validates: Requirements 5.3
        """
        from backend.logger import logger
        
        # Mock the logger to capture log calls
        with patch.object(logger, '_push_to_loki_async') as mock_push:
            from conftest import pytest_sessionstart, pytest_sessionfinish
            
            # Create mock session
            mock_session = MagicMock()
            
            # Call session start hook
            pytest_sessionstart(mock_session)
            
            # Verify session start log was generated
            assert mock_push.call_count >= 1, "Session start should generate at least one log"
            
            start_call = mock_push.call_args_list[0]
            start_message = start_call[0][0]
            start_level = start_call[0][1]
            
            # Verify message indicates session start
            assert 'session' in start_message.lower() and 'start' in start_message.lower(), \
                "Session start log should mention session start"
            
            # Verify log level
            assert start_level in ['INFO', 'DEBUG'], \
                "Session start should use INFO or DEBUG level"
            
            # Reset mock
            mock_push.reset_mock()
            
            # Call session finish hook
            pytest_sessionfinish(mock_session, exit_code)
            
            # Give async threads time to complete
            time.sleep(0.1)
            
            # Verify session finish log was generated
            assert mock_push.call_count >= 1, "Session finish should generate at least one log"
            
            finish_call = mock_push.call_args_list[0]
            finish_message = finish_call[0][0]
            finish_level = finish_call[0][1]
            
            # Verify message indicates session finish
            assert 'session' in finish_message.lower() and 'finish' in finish_message.lower(), \
                "Session finish log should mention session finish"
            
            # Verify log level is appropriate
            if exit_code == 0:
                assert finish_level in ['INFO', 'DEBUG'], \
                    "Successful session should use INFO or DEBUG level"
            else:
                # Failed sessions might use INFO or ERROR
                assert finish_level in ['INFO', 'ERROR', 'WARNING'], \
                    "Failed session should use appropriate log level"
    
    @given(
        test_outcome=st.sampled_from(['passed', 'failed', 'skipped'])
    )
    @settings(max_examples=100)
    def test_property_test_outcomes_generate_appropriate_logs(self, test_outcome):
        """
        Feature: log-query-system, Property 13: Test execution generates logs
        
        Property: For any test outcome (passed/failed/skipped), the backend should 
        push appropriate log entries to Loki with label "app: main".
        
        This test verifies that different test outcomes generate logs with
        appropriate log levels.
        
        Validates: Requirements 5.3
        """
        from backend.logger import logger
        
        # Mock the logger to capture log calls
        with patch.object(logger, '_push_to_loki_async') as mock_push:
            from conftest import pytest_runtest_logreport
            
            # Create mock report
            mock_report = MagicMock()
            mock_report.nodeid = "tests/test_example.py::test_something"
            mock_report.when = 'call'
            mock_report.passed = (test_outcome == 'passed')
            mock_report.failed = (test_outcome == 'failed')
            mock_report.skipped = (test_outcome == 'skipped')
            mock_report.longreprtext = "Error details" if test_outcome == 'failed' else ""
            
            # Call report hook
            pytest_runtest_logreport(mock_report)
            
            # Verify log was generated
            assert mock_push.call_count >= 1, f"{test_outcome} test should generate log"
            
            log_call = mock_push.call_args_list[0]
            message = log_call[0][0]
            level = log_call[0][1]
            labels = log_call[0][2] if len(log_call[0]) > 2 else None
            
            # Verify message contains test name
            assert 'test_something' in message, "Log should contain test name"
            
            # Verify message indicates outcome
            assert test_outcome in message.lower() or \
                   ('pass' in message.lower() and test_outcome == 'passed') or \
                   ('fail' in message.lower() and test_outcome == 'failed') or \
                   ('skip' in message.lower() and test_outcome == 'skipped'), \
                   f"Log should indicate {test_outcome} outcome"
            
            # Verify appropriate log level for outcome
            if test_outcome == 'passed':
                assert level in ['INFO', 'DEBUG'], \
                    "Passed tests should use INFO or DEBUG level"
            elif test_outcome == 'failed':
                assert level in ['ERROR', 'WARNING'], \
                    "Failed tests should use ERROR or WARNING level"
            elif test_outcome == 'skipped':
                assert level in ['WARNING', 'INFO'], \
                    "Skipped tests should use WARNING or INFO level"
            
            # Verify labels
            if labels is not None:
                assert labels == {'app': 'main'}, \
                    "All test logs should be labeled with app:main"
    
    def test_property_all_test_phases_generate_logs(self):
        """
        Feature: log-query-system, Property 13: Test execution generates logs
        
        Property: For any complete test execution (setup + call + teardown), 
        the backend should push logs for each phase to Loki.
        
        This test verifies that the complete test lifecycle generates
        appropriate log entries.
        
        Validates: Requirements 5.3
        """
        from backend.logger import logger
        
        # Mock the logger to capture log calls
        with patch.object(logger, '_push_to_loki_async') as mock_push:
            from conftest import pytest_runtest_setup, pytest_runtest_logreport
            
            test_name = "test_complete_lifecycle"
            
            # Create mock item
            mock_item = MagicMock()
            mock_item.nodeid = f"tests/test_example.py::{test_name}"
            
            # Phase 1: Setup
            pytest_runtest_setup(mock_item)
            setup_call_count = mock_push.call_count
            assert setup_call_count >= 1, "Setup phase should generate logs"
            
            # Phase 2: Call (test execution)
            mock_report = MagicMock()
            mock_report.nodeid = mock_item.nodeid
            mock_report.when = 'call'
            mock_report.passed = True
            mock_report.failed = False
            mock_report.skipped = False
            
            pytest_runtest_logreport(mock_report)
            call_count_after_report = mock_push.call_count
            assert call_count_after_report > setup_call_count, \
                "Test result phase should generate additional logs"
            
            # Verify all logs contain test name
            for call_args in mock_push.call_args_list:
                message = call_args[0][0]
                assert test_name in message or mock_item.nodeid in message, \
                    "All logs should reference the test being executed"
