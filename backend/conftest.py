"""
Pytest configuration and fixtures for the Log Query System backend tests.

This module configures pytest to push test execution logs to Loki with "app: main" label.
Test logs include test names, results, and execution details.
"""

import pytest
import time
from logger import logger


def pytest_runtest_setup(item):
    """
    Hook called before each test execution.
    
    Logs test start information to Loki.
    
    Args:
        item: The test item being executed
    """
    test_name = item.nodeid
    logger.info(f"Test started: {test_name}")


def pytest_runtest_logreport(report):
    """
    Hook called after each test phase (setup, call, teardown).
    
    Logs test results to Loki with "app: main" label.
    
    Args:
        report: Test report object containing test results
    """
    if report.when == 'call':
        test_name = report.nodeid
        
        if report.passed:
            logger.info(f"Test passed: {test_name}")
        elif report.failed:
            logger.error(f"Test failed: {test_name} - {report.longreprtext}")
        elif report.skipped:
            logger.warning(f"Test skipped: {test_name}")


def pytest_sessionstart(session):
    """
    Hook called at the start of the test session.
    
    Logs test session start to Loki.
    
    Args:
        session: The pytest session object
    """
    logger.info("Test session started")


def pytest_sessionfinish(session, exitstatus):
    """
    Hook called at the end of the test session.
    
    Logs test session completion with summary to Loki.
    
    Args:
        session: The pytest session object
        exitstatus: The exit status code
    """
    # Give async logging threads time to complete
    time.sleep(0.5)
    
    status_msg = "success" if exitstatus == 0 else f"failed with exit code {exitstatus}"
    logger.info(f"Test session finished: {status_msg}")


@pytest.fixture(scope='session', autouse=True)
def log_test_session():
    """
    Session-scoped fixture that logs test session information.
    
    This fixture automatically runs for all test sessions and ensures
    test execution is logged to Loki with "app: main" label.
    """
    logger.info("Test session fixture initialized")
    yield
    logger.info("Test session fixture teardown")
