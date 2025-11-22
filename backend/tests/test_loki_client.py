"""
Unit tests for Loki client module.

These tests verify specific behaviors and edge cases using mocked responses.
Tests cover: get_labels(), query_logs(), push_log(), and error handling.
"""

import pytest
import requests
from unittest.mock import Mock, patch
from backend.loki_client import get_labels, query_logs, push_log, LokiClientError


class TestGetLabels:
    """Unit tests for get_labels() function."""
    
    @patch('backend.loki_client.requests.get')
    def test_get_labels_success(self, mock_get):
        """Test successful label retrieval from Loki."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': ['app', 'environment', 'host']
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Execute
        result = get_labels()
        
        # Verify
        assert result == ['app', 'environment', 'host']
        mock_get.assert_called_once()
    
    @patch('backend.loki_client.requests.get')
    def test_get_labels_empty_response(self, mock_get):
        """Test get_labels with empty label list."""
        # Setup mock response with empty data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Execute
        result = get_labels()
        
        # Verify
        assert result == []
    
    @patch('backend.loki_client.requests.get')
    def test_get_labels_missing_data_field(self, mock_get):
        """Test get_labels when response is missing data field."""
        # Setup mock response without data field
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Execute
        result = get_labels()
        
        # Verify - should return empty list
        assert result == []
    
    @patch('backend.loki_client.requests.get')
    def test_get_labels_network_error(self, mock_get):
        """Test get_labels handles network failures."""
        # Setup mock to raise network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
        
        # Execute and verify exception
        with pytest.raises(LokiClientError) as exc_info:
            get_labels()
        
        assert "Failed to fetch labels from Loki" in str(exc_info.value)
    
    @patch('backend.loki_client.requests.get')
    def test_get_labels_timeout_error(self, mock_get):
        """Test get_labels handles timeout errors."""
        # Setup mock to raise timeout
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        # Execute and verify exception
        with pytest.raises(LokiClientError) as exc_info:
            get_labels()
        
        assert "Failed to fetch labels from Loki" in str(exc_info.value)
    
    @patch('backend.loki_client.requests.get')
    def test_get_labels_http_error(self, mock_get):
        """Test get_labels handles HTTP errors."""
        # Setup mock to raise HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_get.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(LokiClientError) as exc_info:
            get_labels()
        
        assert "Failed to fetch labels from Loki" in str(exc_info.value)
    
    @patch('backend.loki_client.requests.get')
    def test_get_labels_invalid_json(self, mock_get):
        """Test get_labels handles invalid JSON response."""
        # Setup mock with invalid JSON
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(LokiClientError) as exc_info:
            get_labels()
        
        assert "Invalid response format from Loki" in str(exc_info.value)


class TestQueryLogs:
    """Unit tests for query_logs() function."""
    
    @patch('backend.loki_client.requests.get')
    def test_query_logs_with_label_only(self, mock_get):
        """Test query_logs with only label parameter."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'result': [
                    {
                        'stream': {'app': 'main'},
                        'values': [
                            ['1640000000000000000', 'Test log message']
                        ]
                    }
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Execute
        result = query_logs(label='app:main')
        
        # Verify
        assert len(result) == 1
        assert result[0]['message'] == 'Test log message'
        assert result[0]['labels'] == {'app': 'main'}
        assert 'timestamp' in result[0]
        
        # Verify request parameters
        call_kwargs = mock_get.call_args[1]
        params = call_kwargs['params']
        assert params['query'] == '{app="main"}'
        assert 'start' not in params
        assert 'end' not in params
    
    @patch('backend.loki_client.requests.get')
    def test_query_logs_with_timestamps(self, mock_get):
        """Test query_logs with label and timestamp parameters."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'result': []
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Execute
        result = query_logs(
            label='app:main',
            start_time='2024-01-01T00:00:00Z',
            end_time='2024-01-01T23:59:59Z'
        )
        
        # Verify request parameters include timestamps
        call_kwargs = mock_get.call_args[1]
        params = call_kwargs['params']
        assert params['start'] == '2024-01-01T00:00:00Z'
        assert params['end'] == '2024-01-01T23:59:59Z'
    
    @patch('backend.loki_client.requests.get')
    def test_query_logs_with_start_time_only(self, mock_get):
        """Test query_logs with only start_time parameter."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': {'result': []}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Execute
        result = query_logs(label='app:main', start_time='2024-01-01T00:00:00Z')
        
        # Verify
        call_kwargs = mock_get.call_args[1]
        params = call_kwargs['params']
        assert params['start'] == '2024-01-01T00:00:00Z'
        assert 'end' not in params
    
    @patch('backend.loki_client.requests.get')
    def test_query_logs_with_end_time_only(self, mock_get):
        """Test query_logs with only end_time parameter."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': {'result': []}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Execute
        result = query_logs(label='app:main', end_time='2024-01-01T23:59:59Z')
        
        # Verify
        call_kwargs = mock_get.call_args[1]
        params = call_kwargs['params']
        assert 'start' not in params
        assert params['end'] == '2024-01-01T23:59:59Z'
    
    @patch('backend.loki_client.requests.get')
    def test_query_logs_multiple_streams(self, mock_get):
        """Test query_logs with multiple log streams."""
        # Setup mock response with multiple streams
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'result': [
                    {
                        'stream': {'app': 'main', 'env': 'prod'},
                        'values': [
                            ['1640000000000000000', 'Log 1'],
                            ['1640000001000000000', 'Log 2']
                        ]
                    },
                    {
                        'stream': {'app': 'main', 'env': 'dev'},
                        'values': [
                            ['1640000002000000000', 'Log 3']
                        ]
                    }
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Execute
        result = query_logs(label='app:main')
        
        # Verify
        assert len(result) == 3
        assert result[0]['message'] == 'Log 1'
        assert result[1]['message'] == 'Log 2'
        assert result[2]['message'] == 'Log 3'
    
    @patch('backend.loki_client.requests.get')
    def test_query_logs_empty_result(self, mock_get):
        """Test query_logs with no matching logs."""
        # Setup mock response with empty result
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'result': []
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Execute
        result = query_logs(label='app:test')
        
        # Verify
        assert result == []
    
    @patch('backend.loki_client.requests.get')
    def test_query_logs_label_without_colon(self, mock_get):
        """Test query_logs with label format without colon."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': {'result': []}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Execute
        result = query_logs(label='app')
        
        # Verify LogQL query format
        call_kwargs = mock_get.call_args[1]
        params = call_kwargs['params']
        assert params['query'] == '{app}'
    
    @patch('backend.loki_client.requests.get')
    def test_query_logs_network_error(self, mock_get):
        """Test query_logs handles network failures."""
        # Setup mock to raise network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
        
        # Execute and verify exception
        with pytest.raises(LokiClientError) as exc_info:
            query_logs(label='app:main')
        
        assert "Failed to query logs from Loki" in str(exc_info.value)
    
    @patch('backend.loki_client.requests.get')
    def test_query_logs_http_error(self, mock_get):
        """Test query_logs handles HTTP errors."""
        # Setup mock to raise HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(LokiClientError) as exc_info:
            query_logs(label='app:main')
        
        assert "Failed to query logs from Loki" in str(exc_info.value)
    
    @patch('backend.loki_client.requests.get')
    def test_query_logs_invalid_response_format(self, mock_get):
        """Test query_logs handles invalid response format."""
        # Setup mock with malformed response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'invalid': 'format'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Execute - should handle gracefully and return empty list
        result = query_logs(label='app:main')
        
        # Verify
        assert result == []


class TestPushLog:
    """Unit tests for push_log() function."""
    
    @patch('backend.loki_client.requests.post')
    def test_push_log_success(self, mock_post):
        """Test successful log push to Loki."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        # Execute
        result = push_log(message='Test log message', level='INFO')
        
        # Verify
        assert result is True
        mock_post.assert_called_once()
        
        # Verify payload structure
        call_kwargs = mock_post.call_args[1]
        payload = call_kwargs['json']
        assert 'streams' in payload
        assert len(payload['streams']) == 1
        assert payload['streams'][0]['stream'] == {'app': 'main'}
    
    @patch('backend.loki_client.requests.post')
    def test_push_log_with_custom_labels(self, mock_post):
        """Test push_log with custom labels."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        # Execute with custom labels
        custom_labels = {'service': 'api', 'env': 'prod'}
        result = push_log(message='Test message', level='ERROR', labels=custom_labels)
        
        # Verify
        assert result is True
        
        # Verify custom labels are used
        call_kwargs = mock_post.call_args[1]
        payload = call_kwargs['json']
        assert payload['streams'][0]['stream'] == custom_labels
    
    @patch('backend.loki_client.requests.post')
    def test_push_log_different_levels(self, mock_post):
        """Test push_log with different log levels."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        # Test each log level
        for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            result = push_log(message=f'Test {level}', level=level)
            assert result is True
            
            # Verify log line includes level
            call_kwargs = mock_post.call_args[1]
            payload = call_kwargs['json']
            log_line = payload['streams'][0]['values'][0][1]
            assert f'[{level}]' in log_line
    
    @patch('backend.loki_client.requests.post')
    def test_push_log_payload_format(self, mock_post):
        """Test push_log creates correct payload format."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        # Execute
        message = 'Test message'
        level = 'INFO'
        result = push_log(message=message, level=level)
        
        # Verify payload structure
        call_kwargs = mock_post.call_args[1]
        payload = call_kwargs['json']
        
        # Check streams structure
        assert 'streams' in payload
        assert isinstance(payload['streams'], list)
        assert len(payload['streams']) == 1
        
        stream = payload['streams'][0]
        assert 'stream' in stream
        assert 'values' in stream
        
        # Check values structure
        assert isinstance(stream['values'], list)
        assert len(stream['values']) == 1
        
        value = stream['values'][0]
        assert len(value) == 2  # [timestamp, log_line]
        
        timestamp_ns = value[0]
        log_line = value[1]
        
        # Verify timestamp is numeric string
        assert isinstance(timestamp_ns, str)
        assert timestamp_ns.isdigit()
        
        # Verify log line format
        assert log_line == f'[{level}] {message}'
    
    @patch('backend.loki_client.requests.post')
    def test_push_log_network_error(self, mock_post):
        """Test push_log handles network failures."""
        # Setup mock to raise network error
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")
        
        # Execute and verify exception
        with pytest.raises(LokiClientError) as exc_info:
            push_log(message='Test message')
        
        assert "Failed to push log to Loki" in str(exc_info.value)
    
    @patch('backend.loki_client.requests.post')
    def test_push_log_timeout_error(self, mock_post):
        """Test push_log handles timeout errors."""
        # Setup mock to raise timeout
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
        
        # Execute and verify exception
        with pytest.raises(LokiClientError) as exc_info:
            push_log(message='Test message')
        
        assert "Failed to push log to Loki" in str(exc_info.value)
    
    @patch('backend.loki_client.requests.post')
    def test_push_log_http_error(self, mock_post):
        """Test push_log handles HTTP errors."""
        # Setup mock to raise HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_post.return_value = mock_response
        
        # Execute and verify exception
        with pytest.raises(LokiClientError) as exc_info:
            push_log(message='Test message')
        
        assert "Failed to push log to Loki" in str(exc_info.value)
    
    @patch('backend.loki_client.requests.post')
    def test_push_log_default_label_parsing(self, mock_post):
        """Test push_log correctly parses default label."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        # Execute without custom labels
        result = push_log(message='Test message')
        
        # Verify default label is parsed correctly
        call_kwargs = mock_post.call_args[1]
        payload = call_kwargs['json']
        labels = payload['streams'][0]['stream']
        
        # Should parse "app:main" into {'app': 'main'}
        assert labels == {'app': 'main'}
