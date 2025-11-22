# Log Query System

A full-stack web application for querying logs from Grafana Loki. The system provides a user-friendly interface for searching and viewing logs with label-based filtering and optional timestamp ranges.

## Features

- **Label-based log filtering**: Search logs by Loki labels
- **Timestamp range queries**: Filter logs by time range
- **Real-time log display**: View logs with formatted timestamps
- **Default log view**: Automatically displays "app:main" logs on startup
- **Self-monitoring**: Backend logs all operations to Loki for observability
- **Comprehensive testing**: Unit tests and property-based tests for both frontend and backend

## Architecture

The system consists of three main components:

1. **Frontend (Vue.js 3.0 + TypeScript)**: User interface for searching and displaying logs
2. **Backend (Python Flask)**: REST API that proxies requests to Loki
3. **Grafana Loki**: Log aggregation system (external dependency)

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Vue.js 3.0    │  HTTP   │  Flask Backend  │  HTTP   │  Grafana Loki   │
│    Frontend     │◄───────►│   (Python)      │◄───────►│   (Port 3100)   │
└─────────────────┘         └─────────────────┘         └─────────────────┘
                                     │
                                     │ Push Logs
                                     ▼
                            ┌─────────────────┐
                            │  Loki Push API  │
                            │  /loki/api/v1/  │
                            │     push        │
                            └─────────────────┘
```

## Project Structure

```
.
├── backend/
│   ├── __init__.py
│   ├── app.py              # Flask application entry point
│   ├── config.py           # Configuration settings
│   ├── loki_client.py      # Loki API client
│   ├── logger.py           # Logging module
│   ├── routes.py           # API routes
│   ├── conftest.py         # Pytest configuration and fixtures
│   ├── requirements.txt    # Python dependencies
│   └── tests/              # Backend tests
│       ├── __init__.py
│       ├── test_logger.py
│       ├── test_logger_properties.py
│       ├── test_loki_client.py
│       ├── test_loki_client_properties.py
│       ├── test_routes.py
│       ├── test_routes_properties.py
│       └── test_conftest_properties.py
└── frontend/
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    └── src/
        ├── main.ts
        ├── App.vue
        ├── components/     # Vue components
        │   ├── SearchBox.vue
        │   └── LogDisplay.vue
        ├── services/       # API services
        │   └── api.ts
        └── types/          # TypeScript types
            └── index.ts
```

## Prerequisites

- **Python 3.8+**: For backend development
- **Node.js 18+**: For frontend development
- **Grafana Loki**: Running instance (default: http://localhost:3100)

### Setting up Grafana Loki

If you don't have Loki running, you can start it using Docker:

```bash
docker run -d --name=loki -p 3100:3100 grafana/loki:latest
```

Or follow the [official Loki installation guide](https://grafana.com/docs/loki/latest/setup/install/).

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Configure environment variables:
   ```bash
   export LOKI_URL=http://localhost:3100
   export LOG_LEVEL=INFO
   export FLASK_DEBUG=False
   ```

5. Run the Flask application:
   ```bash
   python app.py
   ```

   The backend will start on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

   The frontend will start on `http://localhost:5173` (or another port if 5173 is in use)

4. Open your browser and navigate to the frontend URL

## API Documentation

### Base URL

```
http://localhost:5000/api/v1
```

### Endpoints

#### GET /api/v1/loki/label

Retrieve all available labels from Loki.

**Request:**
```http
GET /api/v1/loki/label
```

**Response (Success - 200):**
```json
{
  "status": "success",
  "data": ["app", "environment", "host"]
}
```

**Response (Error - 500):**
```json
{
  "status": "error",
  "message": "Failed to retrieve labels",
  "code": "LOKI_ERROR"
}
```

#### POST /api/v1/loki/logs

Query logs from Loki with label and optional timestamp filters.

**Request:**
```http
POST /api/v1/loki/logs
Content-Type: application/json

{
  "label": "app:main",
  "start_time": "2024-01-01T00:00:00Z",  // optional
  "end_time": "2024-01-01T23:59:59Z"     // optional
}
```

**Parameters:**
- `label` (required): Label selector in format "key:value" (e.g., "app:main")
- `start_time` (optional): ISO 8601 timestamp for range start
- `end_time` (optional): ISO 8601 timestamp for range end

**Response (Success - 200):**
```json
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
```

**Response (Validation Error - 400):**
```json
{
  "status": "error",
  "message": "Label parameter is required",
  "code": "VALIDATION_ERROR"
}
```

**Response (Server Error - 500):**
```json
{
  "status": "error",
  "message": "Failed to query logs",
  "code": "LOKI_ERROR"
}
```

## Environment Variables

### Backend Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LOKI_URL` | Base URL for Grafana Loki instance | `http://localhost:3100` | No |
| `LOG_LEVEL` | Application log level (DEBUG, INFO, WARNING, ERROR) | `INFO` | No |
| `FLASK_DEBUG` | Enable Flask debug mode | `False` | No |

### Setting Environment Variables

**Linux/macOS:**
```bash
export LOKI_URL=http://localhost:3100
export LOG_LEVEL=DEBUG
export FLASK_DEBUG=True
```

**Windows (Command Prompt):**
```cmd
set LOKI_URL=http://localhost:3100
set LOG_LEVEL=DEBUG
set FLASK_DEBUG=True
```

**Windows (PowerShell):**
```powershell
$env:LOKI_URL="http://localhost:3100"
$env:LOG_LEVEL="DEBUG"
$env:FLASK_DEBUG="True"
```

## Development

### Backend Development

The backend uses Flask with a modular structure:

- **app.py**: Application entry point and initialization
- **config.py**: Configuration management with environment variable support
- **routes.py**: API endpoint definitions
- **loki_client.py**: Loki API client functions
- **logger.py**: Logging module that pushes logs to Loki

**Running in development mode:**
```bash
cd backend
export FLASK_DEBUG=True
python app.py
```

**Code style:**
- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Add docstrings for all modules, classes, and functions

### Frontend Development

The frontend uses Vue.js 3.0 with TypeScript and the Composition API:

- **App.vue**: Root component with state management
- **SearchBox.vue**: Search input component
- **LogDisplay.vue**: Log rendering component
- **api.ts**: API service for backend communication
- **types/index.ts**: TypeScript type definitions

**Development server with hot reload:**
```bash
cd frontend
npm run dev
```

**Building for production:**
```bash
cd frontend
npm run build
```

The production build will be in the `frontend/dist` directory.

## Testing

### Backend Tests

The backend includes comprehensive unit tests and property-based tests using pytest and Hypothesis.

**Running all tests:**
```bash
cd backend
pytest
```

**Running specific test types:**
```bash
# Run only unit tests
pytest tests/test_logger.py tests/test_loki_client.py tests/test_routes.py

# Run only property-based tests
pytest tests/test_logger_properties.py tests/test_loki_client_properties.py tests/test_routes_properties.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_logger.py
```

**Test Logging to Loki:**

All test executions automatically push logs to Loki with the "app:main" label. The test logging includes:
- Test session start/finish events
- Individual test start events
- Test results (passed/failed/skipped)
- Test execution details

This is configured in `backend/conftest.py` using pytest hooks. Test logs help monitor test execution and troubleshoot issues in the test suite itself.

**Property-Based Testing:**

The backend uses Hypothesis for property-based testing, which automatically generates test cases to verify properties hold across a wide range of inputs. Each property test runs 100 iterations by default.

### Frontend Tests

The frontend uses Vitest and Vue Test Utils for testing.

**Running tests:**
```bash
cd frontend
npm test
```

**Running tests in watch mode (development):**
```bash
cd frontend
npm run test:watch
```

**Running with coverage:**
```bash
cd frontend
npm run test:coverage
```

### Integration Testing

To test the complete system:

1. Start Loki (if not already running):
   ```bash
   docker run -d --name=loki -p 3100:3100 grafana/loki:latest
   ```

2. Start the backend:
   ```bash
   cd backend
   python app.py
   ```

3. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

4. Open the frontend in your browser and verify:
   - Labels load on startup
   - Default logs (app:main) display automatically
   - Search functionality works with different labels
   - Timestamp filtering works correctly
   - Error messages display appropriately

## Troubleshooting

### Backend Issues

**Issue: "Connection refused" when connecting to Loki**
- Verify Loki is running: `curl http://localhost:3100/ready`
- Check the `LOKI_URL` environment variable
- Ensure no firewall is blocking port 3100

**Issue: "Module not found" errors**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Issue: Tests failing**
- Ensure Loki is running and accessible
- Check that no other service is using port 5000
- Verify Python version is 3.8 or higher

### Frontend Issues

**Issue: "Cannot connect to backend"**
- Verify backend is running on port 5000
- Check browser console for CORS errors
- Ensure backend CORS is configured correctly

**Issue: "npm install" fails**
- Verify Node.js version is 18 or higher
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and `package-lock.json`, then reinstall

**Issue: Frontend not updating**
- Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
- Clear browser cache
- Restart Vite dev server

## Production Deployment

### Backend Deployment

For production, use a proper WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

**Production considerations:**
- Set `FLASK_DEBUG=False`
- Configure CORS to allow only specific origins
- Use environment variables for sensitive configuration
- Set up proper logging and monitoring
- Use a reverse proxy (nginx, Apache) in front of Gunicorn
- Enable HTTPS/TLS

### Frontend Deployment

Build the frontend for production:

```bash
cd frontend
npm run build
```

Serve the `dist` directory using a web server (nginx, Apache, or CDN).

**Example nginx configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## License

This project is provided as-is for educational and development purposes.

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request with a clear description

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the API documentation
- Check Grafana Loki documentation for Loki-specific issues
