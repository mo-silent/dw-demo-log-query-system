"""
Flask application entry point for the Log Query System backend.

This module initializes the Flask application, registers routes,
configures CORS for frontend communication, and sets up startup logging.
"""

from flask import Flask
from flask_cors import CORS
from routes import api_blueprint
from config import config
from logger import logger


def create_app():
    """
    Create and configure the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config)
    
    # Configure CORS for frontend communication
    # Allow all origins in development, should be restricted in production
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Register API routes blueprint
    app.register_blueprint(api_blueprint)
    
    # Log successful startup
    logger.info("Log Query System backend started successfully")
    logger.info(f"Loki URL configured: {config.LOKI_URL}")
    logger.info(f"Default label: {config.DEFAULT_LABEL}")
    
    return app


# Create the application instance
app = create_app()


if __name__ == '__main__':
    # Run the application
    # In production, use a proper WSGI server like gunicorn
    logger.info("Starting Flask development server")
    app.run(
        host='0.0.0.0',
        port=8081,
        debug=config.DEBUG
    )

