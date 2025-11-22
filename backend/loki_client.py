"""
Loki client module for interacting with Grafana Loki API.

This module provides functions to:
- Fetch available labels from Loki
- Query logs with label and timestamp filters
- Push log entries to Loki
"""

import requests
from typing import List, Dict, Optional, Any
from datetime import datetime
from config import config


class LokiClientError(Exception):
    """Custom exception for Loki client errors."""
    pass


def get_labels() -> List[str]:
    """
    Fetch all available labels from Loki.
    
    Returns:
        List[str]: List of available label names
        
    Raises:
        LokiClientError: If the request to Loki fails
    """
    try:
        url = config.get_loki_labels_url()
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Loki returns labels in data field
        if 'data' in data:
            return data['data']
        
        return []
        
    except requests.exceptions.RequestException as e:
        raise LokiClientError(f"Failed to fetch labels from Loki: {str(e)}")
    except (KeyError, ValueError) as e:
        raise LokiClientError(f"Invalid response format from Loki: {str(e)}")


def get_label_values(label_name: str) -> List[str]:
    """
    Fetch all available values for a specific label from Loki.
    
    Args:
        label_name: Name of the label to fetch values for
    
    Returns:
        List[str]: List of available values for the label
        
    Raises:
        LokiClientError: If the request to Loki fails
    """
    try:
        url = config.get_loki_label_values_url(label_name)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Loki returns values in data field
        if 'data' in data:
            return data['data']
        
        return []
        
    except requests.exceptions.RequestException as e:
        raise LokiClientError(f"Failed to fetch label values from Loki: {str(e)}")
    except (KeyError, ValueError) as e:
        raise LokiClientError(f"Invalid response format from Loki: {str(e)}")


def query_logs(
    label: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Query logs from Loki with label and optional timestamp filters.
    
    Args:
        label: Label selector in format "key:value" (e.g., "app:main")
        start_time: Optional start timestamp (ISO 8601 or Unix timestamp)
        end_time: Optional end timestamp (ISO 8601 or Unix timestamp)
        
    Returns:
        List[Dict[str, Any]]: List of log entries with timestamp, message, and labels
        
    Raises:
        LokiClientError: If the request to Loki fails
    """
    try:
        url = config.get_loki_query_url()
        
        # Build LogQL query from label
        # Convert "app:main" to {app="main"}
        if ':' in label:
            key, value = label.split(':', 1)
            logql_query = f'{{{key}="{value}"}}'
        else:
            logql_query = f'{{{label}}}'
        
        # Build query parameters
        params = {
            'query': logql_query
        }
        
        # Add timestamp parameters if provided
        if start_time:
            params['start'] = start_time
        if end_time:
            params['end'] = end_time
            
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse Loki response format
        logs = []
        if 'data' in data and 'result' in data['data']:
            for stream in data['data']['result']:
                stream_labels = stream.get('stream', {})
                values = stream.get('values', [])
                
                for value in values:
                    # Loki returns [timestamp_ns, log_line]
                    timestamp_ns = value[0]
                    message = value[1]
                    
                    # Convert nanosecond timestamp to ISO format
                    timestamp_sec = int(timestamp_ns) / 1e9
                    timestamp_iso = datetime.fromtimestamp(timestamp_sec).isoformat()
                    
                    logs.append({
                        'timestamp': timestamp_iso,
                        'message': message,
                        'labels': stream_labels
                    })
        
        return logs
        
    except requests.exceptions.RequestException as e:
        raise LokiClientError(f"Failed to query logs from Loki: {str(e)}")
    except (KeyError, ValueError, IndexError) as e:
        raise LokiClientError(f"Invalid response format from Loki: {str(e)}")


def push_log(
    message: str,
    level: str = 'INFO',
    labels: Optional[Dict[str, str]] = None
) -> bool:
    """
    Push a log entry to Loki.
    
    Args:
        message: Log message content
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        labels: Optional dictionary of labels (defaults to app:main)
        
    Returns:
        bool: True if push was successful, False otherwise
        
    Raises:
        LokiClientError: If the request to Loki fails
    """
    try:
        url = config.get_loki_push_url()
        
        # Use default label if none provided
        if labels is None:
            # Parse default label "app:main" into dict
            key, value = config.DEFAULT_LABEL.split(':', 1)
            labels = {key: value}
        
        # Build Loki push payload
        # Timestamp in nanoseconds
        timestamp_ns = str(int(datetime.now().timestamp() * 1e9))
        
        # Format log line with level
        log_line = f"[{level}] {message}"
        
        payload = {
            'streams': [
                {
                    'stream': labels,
                    'values': [
                        [timestamp_ns, log_line]
                    ]
                }
            ]
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        return True
        
    except requests.exceptions.RequestException as e:
        raise LokiClientError(f"Failed to push log to Loki: {str(e)}")
