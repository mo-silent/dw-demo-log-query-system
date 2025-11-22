"""
Property-based tests for API routes module.

These tests verify universal properties that should hold across all inputs
using Hypothesis for property-based testing.
"""

import pytest
import json
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st, settings, assume
from backend.app import create_app
from backend.loki_client import LokiClientError


def get_test_client():
    """Create a test client for the Flask application."""
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()


# Feature: log-query-system, Property 3: Label data round-trip
# Validates: Requirements 1.3
@settings(max_examples=100)
@given(
    labels=st.lists(
        st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=97, max_codepoint=122)),
        min_size=0,
        max_size=10
    )
)
@patch('backend.routes.get_labels')
def test_property_label_data_roundtrip(mock_get_labels, labels):
    """
    Property 3: Label data round-trip
    
    For any label data received from Loki, the backend should return 
    the same label list to the frontend without modification.
    """
    # Setup: Mock Loki to return specific labels
    mock_get_labels.return_value = labels
    
    # Create test client
    client = get_test_client()
    
    # Execute: Call the API endpoint
    response = client.get('/api/v1/loki/label')
    
    # Verify: Response should contain the exact same labels
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['status'] == 'success'
    assert data['data'] == labels, \
        "Backend should return the same label list received from Loki without modification"


# Feature: log-query-system, Property 7: Label parameter validation
# Validates: Requirements 3.3
@settings(max_examples=100)
@given(
    has_label=st.booleans(),
    label_value=st.one_of(
        st.none(),
        st.just(""),
        st.text(min_size=1, max_size=20)
    ),
    start_time=st.one_of(st.none(), st.text(min_size=1, max_size=30)),
    end_time=st.one_of(st.none(), st.text(min_size=1, max_size=30))
)
def test_property_label_parameter_validation(has_label, label_value, start_time, end_time):
    """
    Property 7: Label parameter validation
    
    For any log query request received by the backend, if the label parameter 
    is missing, the backend should return a validation error response.
    """
    # Create test client
    client = get_test_client()
    
    # Build request body
    request_body = {}
    
    if has_label and label_value:
        request_body['label'] = label_value
    elif has_label and label_value == "":
        request_body['label'] = ""
    # If has_label is False or label_value is None, don't include label
    
    if start_time is not None:
        request_body['start_time'] = start_time
    if end_time is not None:
        request_body['end_time'] = end_time
    
    # Execute: Call the API endpoint
    response = client.post(
        '/api/v1/loki/logs',
        data=json.dumps(request_body),
        content_type='application/json'
    )
    
    # Verify: If label is missing or empty, should return validation error
    data = json.loads(response.data)
    
    if not has_label or not label_value:
        # Missing or empty label should result in validation error
        assert response.status_code == 400, \
            "Backend should return 400 when label parameter is missing or empty"
        assert data['status'] == 'error', \
            "Response status should be 'error' when label is missing"
        assert 'message' in data, \
            "Error response should contain a message"
    else:
        # Valid label should not result in validation error (may fail for other reasons)
        # We're only testing validation logic here
        assert response.status_code != 400 or 'Label parameter is required' not in data.get('message', ''), \
            "Backend should not return label validation error when label is provided"


# Feature: log-query-system, Property 9: Log data round-trip from Loki
# Validates: Requirements 3.5
@settings(max_examples=100)
@given(
    label=st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=97, max_codepoint=122)),
    logs=st.lists(
        st.fixed_dictionaries({
            'timestamp': st.text(min_size=1, max_size=30),
            'message': st.text(min_size=0, max_size=100),
            'labels': st.dictionaries(
                st.text(min_size=1, max_size=10),
                st.text(min_size=1, max_size=10),
                min_size=1,
                max_size=3
            )
        }),
        min_size=0,
        max_size=10
    )
)
@patch('backend.routes.query_logs')
def test_property_log_data_roundtrip_from_loki(mock_query_logs, label, logs):
    """
    Property 9: Log data round-trip from Loki
    
    For any log results received from Loki, the backend should return 
    the log data to the frontend without modification.
    """
    # Setup: Mock Loki to return specific logs
    mock_query_logs.return_value = logs
    
    # Create test client
    client = get_test_client()
    
    # Execute: Call the API endpoint
    response = client.post(
        '/api/v1/loki/logs',
        data=json.dumps({'label': label}),
        content_type='application/json'
    )
    
    # Verify: Response should contain the exact same logs
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['status'] == 'success'
    assert data['data'] == logs, \
        "Backend should return the same log data received from Loki without modification"


# Feature: log-query-system, Property 15: Request body parameter parsing
# Validates: Requirements 7.3
@settings(max_examples=100)
@given(
    label=st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=97, max_codepoint=122)),
    has_start_time=st.booleans(),
    start_time=st.text(min_size=1, max_size=30),
    has_end_time=st.booleans(),
    end_time=st.text(min_size=1, max_size=30)
)
@patch('backend.routes.query_logs')
def test_property_request_body_parameter_parsing(
    mock_query_logs, label, has_start_time, start_time, has_end_time, end_time
):
    """
    Property 15: Request body parameter parsing
    
    For any log query request with parameters in the body, the backend 
    should correctly parse and extract all parameters.
    """
    # Setup: Mock query_logs to return empty list
    mock_query_logs.return_value = []
    
    # Create test client
    client = get_test_client()
    
    # Build request body
    request_body = {'label': label}
    if has_start_time:
        request_body['start_time'] = start_time
    if has_end_time:
        request_body['end_time'] = end_time
    
    # Execute: Call the API endpoint
    response = client.post(
        '/api/v1/loki/logs',
        data=json.dumps(request_body),
        content_type='application/json'
    )
    
    # Verify: Backend should parse all parameters correctly
    assert response.status_code == 200
    
    # Check that query_logs was called with the correct parameters
    mock_query_logs.assert_called_once()
    call_args = mock_query_logs.call_args
    
    # Verify label was parsed
    assert call_args[0][0] == label or call_args[1].get('label') == label, \
        "Backend should correctly parse label parameter from request body"
    
    # Verify start_time was parsed if provided
    if has_start_time:
        start_arg = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get('start_time')
        assert start_arg == start_time, \
            "Backend should correctly parse start_time parameter from request body"
    
    # Verify end_time was parsed if provided
    if has_end_time:
        end_arg = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get('end_time')
        assert end_arg == end_time, \
            "Backend should correctly parse end_time parameter from request body"


# Feature: log-query-system, Property 16: HTTP status code correctness
# Validates: Requirements 7.4
@settings(max_examples=100)
@given(
    scenario=st.sampled_from(['success', 'validation_error', 'server_error']),
    label=st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=97, max_codepoint=122))
)
@patch('backend.routes.query_logs')
@patch('backend.routes.get_labels')
def test_property_http_status_code_correctness(
    mock_get_labels, mock_query_logs, scenario, label
):
    """
    Property 16: HTTP status code correctness
    
    For any backend response, the HTTP status code should be 200 for success, 
    400 for validation errors, and 500 for server errors.
    """
    # Create test client
    client = get_test_client()
    
    if scenario == 'success':
        # Setup for success scenario
        mock_query_logs.return_value = []
        mock_get_labels.return_value = ['app', 'env']
        
        # Test GET endpoint
        response = client.get('/api/v1/loki/label')
        assert response.status_code == 200, \
            "Backend should return 200 status code for successful operations"
        
        # Test POST endpoint
        response = client.post(
            '/api/v1/loki/logs',
            data=json.dumps({'label': label}),
            content_type='application/json'
        )
        assert response.status_code == 200, \
            "Backend should return 200 status code for successful operations"
    
    elif scenario == 'validation_error':
        # Test validation error (missing label)
        response = client.post(
            '/api/v1/loki/logs',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400, \
            "Backend should return 400 status code for validation errors"
        
        # Test validation error (no body)
        response = client.post(
            '/api/v1/loki/logs',
            data='',
            content_type='application/json'
        )
        assert response.status_code == 400, \
            "Backend should return 400 status code for validation errors"
    
    elif scenario == 'server_error':
        # Setup for server error scenario
        mock_query_logs.side_effect = LokiClientError("Loki connection failed")
        mock_get_labels.side_effect = LokiClientError("Loki connection failed")
        
        # Test GET endpoint with error
        response = client.get('/api/v1/loki/label')
        assert response.status_code == 500, \
            "Backend should return 500 status code for server errors"
        
        # Test POST endpoint with error
        response = client.post(
            '/api/v1/loki/logs',
            data=json.dumps({'label': label}),
            content_type='application/json'
        )
        assert response.status_code == 500, \
            "Backend should return 500 status code for server errors"


# Feature: log-query-system, Property 17: JSON response format
# Validates: Requirements 7.5
@settings(max_examples=100)
@given(
    endpoint=st.sampled_from(['labels', 'logs']),
    should_succeed=st.booleans(),
    label=st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=97, max_codepoint=122))
)
@patch('backend.routes.query_logs')
@patch('backend.routes.get_labels')
def test_property_json_response_format(
    mock_get_labels, mock_query_logs, endpoint, should_succeed, label
):
    """
    Property 17: JSON response format
    
    For any backend response, the response body should be valid JSON with 
    a "status" field and appropriate "data" or "message" fields.
    """
    # Create test client
    client = get_test_client()
    
    if should_succeed:
        # Setup for success
        mock_get_labels.return_value = ['app', 'env']
        mock_query_logs.return_value = []
    else:
        # Setup for error
        mock_get_labels.side_effect = LokiClientError("Connection failed")
        mock_query_logs.side_effect = LokiClientError("Connection failed")
    
    # Execute: Call the appropriate endpoint
    if endpoint == 'labels':
        response = client.get('/api/v1/loki/label')
    else:  # logs
        response = client.post(
            '/api/v1/loki/logs',
            data=json.dumps({'label': label}),
            content_type='application/json'
        )
    
    # Verify: Response should be valid JSON
    try:
        data = json.loads(response.data)
    except json.JSONDecodeError:
        pytest.fail("Backend response should be valid JSON")
    
    # Verify: Response should have status field
    assert 'status' in data, \
        "Backend response should contain 'status' field"
    
    assert data['status'] in ['success', 'error'], \
        "Status field should be either 'success' or 'error'"
    
    # Verify: Success responses should have data field
    if data['status'] == 'success':
        assert 'data' in data, \
            "Success responses should contain 'data' field"
    
    # Verify: Error responses should have message field
    if data['status'] == 'error':
        assert 'message' in data, \
            "Error responses should contain 'message' field"
