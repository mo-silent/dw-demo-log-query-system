"""
API routes module for the Log Query System backend.

This module provides RESTful API endpoints for:
- Retrieving available labels from Loki
- Querying logs with label and timestamp filters

All operations are logged to Loki for observability.
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
from loki_client import get_labels, get_label_values, query_logs, LokiClientError
from logger import logger


# Create Flask blueprint for API routes
api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1')


def create_success_response(data: Any) -> Dict[str, Any]:
    """
    Create a standardized success response.
    
    Args:
        data: Response data payload
        
    Returns:
        Dict[str, Any]: Formatted success response
    """
    return {
        'status': 'success',
        'data': data
    }


def create_error_response(message: str, code: str = 'ERROR') -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        code: Error code identifier
        
    Returns:
        Dict[str, Any]: Formatted error response
    """
    return {
        'status': 'error',
        'message': message,
        'code': code
    }


@api_blueprint.route('/loki/label', methods=['GET'])
def get_loki_labels():
    """
    GET /api/v1/loki/label
    
    Retrieve all available labels from Loki.
    
    Returns:
        JSON response with label list or error message
        
    Response format (success):
        {
            "status": "success",
            "data": ["app", "environment", "host"]
        }
        
    Response format (error):
        {
            "status": "error",
            "message": "Failed to retrieve labels",
            "code": "LOKI_ERROR"
        }
    """
    try:
        # Log the operation
        logger.info("Fetching labels from Loki")
        
        # Fetch labels from Loki
        labels = get_labels()
        
        # Log success
        logger.info(f"Successfully retrieved {len(labels)} labels from Loki")
        
        # Return success response
        return jsonify(create_success_response(labels)), 200
        
    except LokiClientError as e:
        # Log error
        logger.error(f"Failed to fetch labels from Loki: {str(e)}")
        
        # Return error response
        return jsonify(create_error_response(
            "Failed to retrieve labels",
            "LOKI_ERROR"
        )), 500
        
    except Exception as e:
        # Log unexpected error
        logger.error(f"Unexpected error in get_loki_labels: {str(e)}")
        
        # Return error response
        return jsonify(create_error_response(
            "Internal server error",
            "INTERNAL_ERROR"
        )), 500


@api_blueprint.route('/loki/label/<label_name>/values', methods=['GET'])
def get_loki_label_values(label_name: str):
    """
    GET /api/v1/loki/label/<label_name>/values
    
    Retrieve all available values for a specific label from Loki.
    
    Args:
        label_name: Name of the label to fetch values for
    
    Returns:
        JSON response with label values list or error message
        
    Response format (success):
        {
            "status": "success",
            "data": ["main", "test", "prod"]
        }
        
    Response format (error):
        {
            "status": "error",
            "message": "Failed to retrieve label values",
            "code": "LOKI_ERROR"
        }
    """
    try:
        # Log the operation
        logger.info(f"Fetching values for label '{label_name}' from Loki")
        
        # Fetch label values from Loki
        values = get_label_values(label_name)
        
        # Log success
        logger.info(f"Successfully retrieved {len(values)} values for label '{label_name}' from Loki")
        
        # Return success response
        return jsonify(create_success_response(values)), 200
        
    except LokiClientError as e:
        # Log error
        logger.error(f"Failed to fetch label values from Loki: {str(e)}")
        
        # Return error response
        return jsonify(create_error_response(
            "Failed to retrieve label values",
            "LOKI_ERROR"
        )), 500
        
    except Exception as e:
        # Log unexpected error
        logger.error(f"Unexpected error in get_loki_label_values: {str(e)}")
        
        # Return error response
        return jsonify(create_error_response(
            "Internal server error",
            "INTERNAL_ERROR"
        )), 500


@api_blueprint.route('/loki/logs', methods=['POST'])
def query_loki_logs():
    """
    POST /api/v1/loki/logs
    
    Query logs from Loki with label and optional timestamp filters.
    
    Request body:
        {
            "label": "app:main",
            "start_time": "2024-01-01T00:00:00Z",  // optional
            "end_time": "2024-01-01T23:59:59Z"     // optional
        }
    
    Returns:
        JSON response with log entries or error message
        
    Response format (success):
        {
            "status": "success",
            "data": [
                {
                    "timestamp": "2024-01-01T12:00:00Z",
                    "message": "Log message content",
                    "labels": {"app": "main"}
                }
            ]
        }
        
    Response format (error):
        {
            "status": "error",
            "message": "Label parameter is required",
            "code": "VALIDATION_ERROR"
        }
    """
    try:
        # Parse request body
        try:
            request_data = request.get_json()
        except Exception as e:
            logger.warning(f"Failed to parse request body: {str(e)}")
            return jsonify(create_error_response(
                "Invalid JSON in request body",
                "VALIDATION_ERROR"
            )), 400
        
        # Validate request data exists
        if not request_data:
            logger.warning("Received log query request with no body")
            return jsonify(create_error_response(
                "Request body is required",
                "VALIDATION_ERROR"
            )), 400
        
        # Validate required label parameter
        label = request_data.get('label')
        if not label:
            logger.warning("Received log query request without label parameter")
            return jsonify(create_error_response(
                "Label parameter is required",
                "VALIDATION_ERROR"
            )), 400
        
        # Extract optional timestamp parameters
        start_time = request_data.get('start_time')
        end_time = request_data.get('end_time')
        
        # Log the operation
        log_msg = f"Querying logs from Loki with label={label}"
        if start_time or end_time:
            log_msg += f", start_time={start_time}, end_time={end_time}"
        logger.info(log_msg)
        
        # Query logs from Loki
        logs = query_logs(label, start_time, end_time)
        
        # Log success
        logger.info(f"Successfully retrieved {len(logs)} log entries from Loki")
        
        # Return success response
        return jsonify(create_success_response(logs)), 200
        
    except LokiClientError as e:
        # Log error
        logger.error(f"Failed to query logs from Loki: {str(e)}")
        
        # Return error response
        return jsonify(create_error_response(
            "Failed to query logs",
            "LOKI_ERROR"
        )), 500
        
    except Exception as e:
        # Log unexpected error
        logger.error(f"Unexpected error in query_loki_logs: {str(e)}")
        
        # Return error response
        return jsonify(create_error_response(
            "Internal server error",
            "INTERNAL_ERROR"
        )), 500
