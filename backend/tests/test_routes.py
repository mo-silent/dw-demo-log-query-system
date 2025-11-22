"""
Unit tests for API routes module.

These tests verify specific behaviors and edge cases for the Flask API endpoints.
Tests cover: GET /api/v1/loki/label, POST /api/v1/loki/logs, error handling,
and HTTP status codes.
"""

import pytest
import json
from unittest.mock import patch, Mock
from backend.app import create_app
from backend.loki_client import LokiClientError


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestGetLokiLabels:
    """Unit tests for GET /api/v1/loki/label endpoint."""
    
    @patch('backend.routes.get_labels')
    def test_get_labels_success(self, mock_get_labels, client):
        """Test successful label retrieval."""
        # Setup mock
        mock_get_labels.return_value = ['app', 'environment', 'host']
        
        # Execute
        response = client.get('/api/v1/loki/label')
        
        # Verify
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data'] == ['app', 'environment', 'host']
        
        # Verify mock was called
        mock_get_labels.assert_called_once()
    
    @patch('backend.routes.get_labels')
    def test_get_labels_empty_list(self, mock_get_labels, client):
        """Test label retrieval with empty result."""
        # Setup mock
        mock_get_labels.return_value = []
        
        # Execute
        response = client.get('/api/v1/loki/label')
        
        # Verify
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data'] == []
    
    @patch('backend.routes.get_labels')
    def test_get_labels_loki_error(self, mock_get_labels, client):
        """Test label retrieval when Loki is unavailable."""
        # Setup mock to raise LokiClientError
        mock_get_labels.side_effect = LokiClientError("Connection refused")
        
        # Execute
        response = client.get('/api/v1/loki/label')
        
        # Verify error response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['message'] == 'Failed to retrieve labels'
        assert data['code'] == 'LOKI_ERROR'
    
    @patch('backend.routes.get_labels')
    def test_get_labels_unexpected_error(self, mock_get_labels, client):
        """Test label retrieval with unexpected exception."""
        # Setup mock to raise unexpected error
        mock_get_labels.side_effect = RuntimeError("Unexpected error")
        
        # Execute
        response = client.get('/api/v1/loki/label')
        
        # Verify error response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['message'] == 'Internal server error'
        assert data['code'] == 'INTERNAL_ERROR'
    
    @patch('backend.routes.get_labels')
    def test_get_labels_response_format(self, mock_get_labels, client):
        """Test that response follows correct JSON format."""
        # Setup mock
        mock_get_labels.return_value = ['label1', 'label2']
        
        # Execute
        response = client.get('/api/v1/loki/label')
        
        # Verify response format
        assert response.content_type == 'application/json'
        data = json.loads(response.data)
        
        # Verify required fields
        assert 'status' in data
        assert 'data' in data
        assert isinstance(data['data'], list)


class TestQueryLokiLogs:
    """Unit tests for POST /api/v1/loki/logs endpoint."""
    
    @patch('backend.routes.query_logs')
    def test_query_logs_with_valid_label(self, mock_query_logs, client):
        """Test log query with valid label parameter."""
        # Setup mock
        mock_logs = [
            {
                'timestamp': '2024-01-01T12:00:00',
                'message': 'Test log message',
                'labels': {'app': 'main'}
            }
        ]
        mock_query_logs.return_value = mock_logs
        
        # Execute
        response = client.post(
            '/api/v1/loki/logs',
            data=json.dumps({'label': 'app:main'}),
            content_type='application/json'
        )
        
        # Verify
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data'] == mock_logs
        
        # Verify mock was called with correct parameters
        mock_query_logs.assert_called_once_with('app:main', None, None)
    
    @patch('backend.routes.query_logs')
    def test_query_logs_with_timestamps(self, mock_query_logs, client):
        """Test log query with label and timestamp parameters."""
        # Setup mock
        mock_query_logs.return_value = []
        
        # Execute
        request_body = {
            'label': 'app:main',
            'start_time': '2024-01-01T00:00:00Z',
            'end_time': '2024-01-01T23:59:59Z'
        }
        response = client.post(
            '/api/v1/loki/logs',
            data=json.dumps(request_body),
            content_type='application/json'
        )
        
        # Verify
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        # Verify mock was called with timestamp parameters
        mock_query_logs.assert_called_once_with(
            'app:main',
            '2024-01-01T00:00:00Z',
            '2024-01-01T23:59:59Z'
        )
    
    @patch('backend.routes.query_logs')
    def test_query_logs_with_start_time_only(self, mock_query_logs, client):
        """Test log query with only start_time parameter."""
        # Setup mock
        mock_query_logs.return_value = []
        
        # Execute
        request_body = {
            'label': 'app:main',
            'start_time': '2024-01-01T00:00:00Z'
        }
        response = client.post(
            '/api/v1/loki/logs',
            data=json.dumps(request_body),
            content_type='application/json'
        )
        
        # Verify
        assert response.status_code == 200
        
        # Verify mock was called with start_time but no end_time
        mock_query_logs.assert_called_once_with(
            'app:main',
            '2024-01-01T00:00:00Z',
            None
        )
    
    @patch('backend.routes.query_logs')
    def test_query_logs_with_end_time_only(self, mock_query_logs, client):
        """Test log query with only end_time parameter."""
        # Setup mock
        mock_query_logs.return_value = []
        
        # Execute
        request_body = {
            'label': 'app:main',
            'end_time': '2024-01-01T23:59:59Z'
        }
        response = client.post(
            '/api/v1/loki/logs',
            data=json.dumps(request_body),
            content_type='application/json'
        )
        
        # Verify
        assert response.status_code == 200
        
        # Verify mock was called with end_time but no start_time
        mock_query_logs.assert_called_once_with(
            'app:main',
            None,
            '2024-01-01T23:59:59Z'
        )
    
    def test_query_logs_missing_label_parameter(self, client):
        """Test log query without required label parameter."""
        # Execute with missing label
        request_body = {
            'start_time': '2024-01-01T00:00:00Z'
        }
        response = client.post(
            '/api/v1/loki/logs',
            data=json.dumps(request_body),
            content_type='application/json'
        )
        
        # Verify validation error
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['message'] == 'Label parameter is required'
        assert data['code'] == 'VALIDATION_ERROR'
    
    def test_query_logs_empty_request_body(self, client):
        """Test log query with empty request body."""
        # Execute with empty body
        response = client.post(
            '/api/v1/loki/logs',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        # Verify validation error
        # Empty JSON object {} is falsy in Python, so triggers "Request body is required"
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['message'] == 'Request body is required'
        assert data['code'] == 'VALIDATION_ERROR'
    
    def test_query_logs_no_request_body(self, client):
        """Test log query with no request body."""
        # Execute without body
        response = client.post(
            '/api/v1/loki/logs',
            content_type='application/json'
        )
        
        # Verify validation error
        # No body triggers JSON parsing error first
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['message'] == 'Invalid JSON in request body'
        assert data['code'] == 'VALIDATION_ERROR'
    
    def test_query_logs_invalid_json(self, client):
        """Test log query with invalid JSON in request body."""
        # Execute with invalid JSON
        response = client.post(
            '/api/v1/loki/logs',
            data='invalid json',
            content_type='application/json'
        )
        
        # Verify validation error
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['message'] == 'Invalid JSON in request body'
        assert data['code'] == 'VALIDATION_ERROR'
    
    @patch('backend.routes.query_logs')
    def test_query_logs_loki_error(self, mock_query_logs, client):
        """Test log query when Loki is unavailable."""
        # Setup mock to raise LokiClientError
        mock_query_logs.side_effect = LokiClientError("Connection refused")
        
        # Execute
        response = client.post(
            '/api/v1/loki/logs',
            data=json.dumps({'label': 'app:main'}),
            content_type='application/json'
        )
        
        # Verify error response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['message'] == 'Failed to query logs'
        assert data['code'] == 'LOKI_ERROR'
    
    @patch('backend.routes.query_logs')
    def test_query_logs_unexpected_error(self, mock_query_logs, client):
        """Test log query with unexpected exception."""
        # Setup mock to raise unexpected error
        mock_query_logs.side_effect = RuntimeError("Unexpected error")
        
        # Execute
        response = client.post(
            '/api/v1/loki/logs',
            data=json.dumps({'label': 'app:main'}),
            content_type='application/json'
        )
        
        # Verify error response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['message'] == 'Internal server error'
        assert data['code'] == 'INTERNAL_ERROR'
    
    @patch('backend.routes.query_logs')
    def test_query_logs_empty_result(self, mock_query_logs, client):
        """Test log query with no matching logs."""
        # Setup mock to return empty list
        mock_query_logs.return_value = []
        
        # Execute
        response = client.post(
            '/api/v1/loki/logs',
            data=json.dumps({'label': 'app:test'}),
            content_type='application/json'
        )
        
        # Verify
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data'] == []


class TestErrorResponseFormat:
    """Unit tests for error response formatting."""
    
    @patch('backend.routes.get_labels')
    def test_error_response_has_required_fields(self, mock_get_labels, client):
        """Test that error responses contain required fields."""
        # Setup mock to raise error
        mock_get_labels.side_effect = LokiClientError("Test error")
        
        # Execute
        response = client.get('/api/v1/loki/label')
        
        # Verify error response structure
        data = json.loads(response.data)
        assert 'status' in data
        assert 'message' in data
        assert 'code' in data
        assert data['status'] == 'error'
    
    def test_validation_error_format(self, client):
        """Test validation error response format."""
        # Execute request that triggers validation error
        response = client.post(
            '/api/v1/loki/logs',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        # Verify error format
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert isinstance(data['message'], str)
        assert data['code'] == 'VALIDATION_ERROR'


class TestHttpStatusCodes:
    """Unit tests for HTTP status code correctness."""
    
    @patch('backend.routes.get_labels')
    def test_success_returns_200(self, mock_get_labels, client):
        """Test that successful requests return 200 status code."""
        # Setup mock
        mock_get_labels.return_value = ['app']
        
        # Execute
        response = client.get('/api/v1/loki/label')
        
        # Verify
        assert response.status_code == 200
    
    def test_validation_error_returns_400(self, client):
        """Test that validation errors return 400 status code."""
        # Execute request with missing required parameter
        response = client.post(
            '/api/v1/loki/logs',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        # Verify
        assert response.status_code == 400
    
    @patch('backend.routes.get_labels')
    def test_server_error_returns_500(self, mock_get_labels, client):
        """Test that server errors return 500 status code."""
        # Setup mock to raise error
        mock_get_labels.side_effect = LokiClientError("Server error")
        
        # Execute
        response = client.get('/api/v1/loki/label')
        
        # Verify
        assert response.status_code == 500
    
    @patch('backend.routes.query_logs')
    def test_post_success_returns_200(self, mock_query_logs, client):
        """Test that successful POST requests return 200 status code."""
        # Setup mock
        mock_query_logs.return_value = []
        
        # Execute
        response = client.post(
            '/api/v1/loki/logs',
            data=json.dumps({'label': 'app:main'}),
            content_type='application/json'
        )
        
        # Verify
        assert response.status_code == 200


class TestJsonResponseFormat:
    """Unit tests for JSON response format."""
    
    @patch('backend.routes.get_labels')
    def test_success_response_json_format(self, mock_get_labels, client):
        """Test that success responses are valid JSON with correct structure."""
        # Setup mock
        mock_get_labels.return_value = ['app', 'env']
        
        # Execute
        response = client.get('/api/v1/loki/label')
        
        # Verify JSON format
        assert response.content_type == 'application/json'
        data = json.loads(response.data)
        
        # Verify structure
        assert 'status' in data
        assert data['status'] == 'success'
        assert 'data' in data
    
    @patch('backend.routes.get_labels')
    def test_error_response_json_format(self, mock_get_labels, client):
        """Test that error responses are valid JSON with correct structure."""
        # Setup mock to raise error
        mock_get_labels.side_effect = LokiClientError("Test error")
        
        # Execute
        response = client.get('/api/v1/loki/label')
        
        # Verify JSON format
        assert response.content_type == 'application/json'
        data = json.loads(response.data)
        
        # Verify structure
        assert 'status' in data
        assert data['status'] == 'error'
        assert 'message' in data
        assert 'code' in data
    
    @patch('backend.routes.query_logs')
    def test_post_response_json_format(self, mock_query_logs, client):
        """Test that POST responses are valid JSON."""
        # Setup mock
        mock_query_logs.return_value = [
            {'timestamp': '2024-01-01T12:00:00', 'message': 'test', 'labels': {}}
        ]
        
        # Execute
        response = client.post(
            '/api/v1/loki/logs',
            data=json.dumps({'label': 'app:main'}),
            content_type='application/json'
        )
        
        # Verify JSON format
        assert response.content_type == 'application/json'
        data = json.loads(response.data)
        
        # Verify can be parsed as JSON and has correct structure
        assert isinstance(data, dict)
        assert 'status' in data
        assert 'data' in data
