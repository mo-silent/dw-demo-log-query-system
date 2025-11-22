# Design Document

## Overview

The Log Query System is a full-stack web application that provides a user-friendly interface for querying logs from Grafana Loki. The system follows a client-server architecture with a Vue.js 3.0 frontend and a Python Flask backend. The backend acts as a proxy between the frontend and Loki, handling API requests, managing authentication, and logging its own operations back to Loki for observability.

## Architecture

### High-Level Architecture

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

### Component Interaction Flow

1. **Initial Load**: Frontend → Backend (GET labels) → Loki → Backend → Frontend
2. **Default Logs**: Frontend → Backend (POST logs with app:main) → Loki → Backend → Frontend
3. **User Search**: Frontend → Backend (POST logs with filters) → Loki → Backend → Frontend
4. **Backend Logging**: Backend operations → Loki Push API (async)

## Components and Interfaces

### Frontend Components (Vue.js 3.0)

#### 1. SearchBox Component
- **Responsibility**: Capture user search input including label selection and timestamp range
- **Props**: 
  - `availableLabels: string[]` - List of available labels from backend
- **Emits**:
  - `search(criteria: SearchCriteria)` - Emitted when user submits search
- **State**:
  - `selectedLabel: string` - Currently selected label
  - `startTime: string` - Optional start timestamp
  - `endTime: string` - Optional end timestamp

#### 2. LogDisplay Component
- **Responsibility**: Render log entries in a readable format
- **Props**:
  - `logs: LogEntry[]` - Array of log entries to display
  - `loading: boolean` - Loading state indicator
- **Features**:
  - Formatted timestamps
  - Syntax highlighting for log content
  - Auto-scroll to latest logs

#### 3. App Component (Root)
- **Responsibility**: Orchestrate data flow between components and backend
- **State**:
  - `labels: string[]` - Available labels from Loki
  - `logs: LogEntry[]` - Current log entries
  - `loading: boolean` - Loading state
- **Lifecycle**:
  - `onMounted`: Fetch labels and default logs

### Backend Components (Python Flask)

#### 1. API Routes Module (`routes.py`)

**GET /api/v1/loki/label**
- **Purpose**: Retrieve all available labels from Loki
- **Request**: None
- **Response**: 
  ```json
  {
    "status": "success",
    "data": ["app", "environment", "host"]
  }
  ```
- **Error Response**:
  ```json
  {
    "status": "error",
    "message": "Failed to retrieve labels"
  }
  ```

**POST /api/v1/loki/logs**
- **Purpose**: Query logs from Loki with filters
- **Request Body**:
  ```json
  {
    "label": "app:main",
    "start_time": "2024-01-01T00:00:00Z",
    "end_time": "2024-01-01T23:59:59Z"
  }
  ```
- **Response**:
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

#### 2. Loki Client Module (`loki_client.py`)
- **Responsibility**: Handle all communication with Loki API
- **Functions**:
  - `get_labels() -> List[str]`: Fetch labels from Loki
  - `query_logs(label: str, start_time: Optional[str], end_time: Optional[str]) -> List[Dict]`: Query logs
  - `push_log(message: str, level: str, labels: Dict[str, str]) -> bool`: Push log entry to Loki

#### 3. Logger Module (`logger.py`)
- **Responsibility**: Provide logging functionality that pushes to Loki
- **Features**:
  - Async log pushing to avoid blocking main operations
  - Automatic labeling with "app: main"
  - Fallback to local logging if Loki is unavailable
  - Log levels: DEBUG, INFO, WARNING, ERROR

#### 4. Configuration Module (`config.py`)
- **Responsibility**: Centralize configuration settings
- **Settings**:
  - `LOKI_URL`: Base URL for Loki (default: http://localhost:3100)
  - `LOKI_PUSH_ENDPOINT`: Push endpoint path
  - `LOKI_QUERY_ENDPOINT`: Query endpoint path
  - `DEFAULT_LABEL`: Default label for queries (app:main)
  - `LOG_LEVEL`: Application log level

## Data Models

### Frontend Data Models (TypeScript)

```typescript
interface SearchCriteria {
  label: string;
  startTime?: string;
  endTime?: string;
}

interface LogEntry {
  timestamp: string;
  message: string;
  labels: Record<string, string>;
  level?: string;
}

interface ApiResponse<T> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
}
```

### Backend Data Models (Python)

```python
from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class LogQuery:
    label: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None

@dataclass
class LogEntry:
    timestamp: str
    message: str
    labels: Dict[str, str]
    level: Optional[str] = None
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Label retrieval triggers backend query
*For any* frontend load event, the frontend should send a request to the backend to retrieve available labels.
**Validates: Requirements 1.1**

### Property 2: Backend queries Loki for labels
*For any* label request received by the backend, the backend should make an API call to Loki's api/v1/loki/label endpoint.
**Validates: Requirements 1.2**

### Property 3: Label data round-trip
*For any* label data received from Loki, the backend should return the same label list to the frontend without modification.
**Validates: Requirements 1.3**

### Property 4: Log display renders received data
*For any* log data received by the frontend, the logs should be rendered in the content area of the DOM.
**Validates: Requirements 2.4**

### Property 5: Search submission sends POST with label
*For any* search criteria submitted by the user, the frontend should send a POST request to the backend containing the specified label.
**Validates: Requirements 3.1**

### Property 6: Timestamp inclusion in requests
*For any* search criteria that includes a timestamp range, the frontend should include both start_time and end_time parameters in the POST request body.
**Validates: Requirements 3.2**

### Property 7: Label parameter validation
*For any* log query request received by the backend, if the label parameter is missing, the backend should return a validation error response.
**Validates: Requirements 3.3**

### Property 8: Backend forwards queries to Loki
*For any* valid log query received by the backend, the backend should send a request to Loki at api/v1/loki/logs with all provided parameters (label, start_time, end_time).
**Validates: Requirements 3.4**

### Property 9: Log data round-trip from Loki
*For any* log results received from Loki, the backend should return the log data to the frontend without modification.
**Validates: Requirements 3.5**

### Property 10: Backend operations generate logs
*For any* backend operation (API request, Loki query, error), the backend should generate a corresponding log entry.
**Validates: Requirements 4.1**

### Property 11: Logs pushed to correct endpoint
*For any* log entry generated by the backend, the log should be pushed to Loki at http://localhost:3100/loki/api/v1/push.
**Validates: Requirements 4.2**

### Property 12: Backend logs labeled correctly
*For any* log pushed by the backend to Loki, the log should include the label "app: main".
**Validates: Requirements 4.3**

### Property 13: Test execution generates logs
*For any* unit test execution, the backend should push test execution logs to Loki with label "app: main".
**Validates: Requirements 5.3**

### Property 14: Log entry formatting
*For any* log entry displayed by the frontend, the rendered output should contain both a formatted timestamp and the log message content.
**Validates: Requirements 6.5**

### Property 15: Request body parameter parsing
*For any* log query request with parameters in the body, the backend should correctly parse and extract all parameters.
**Validates: Requirements 7.3**

### Property 16: HTTP status code correctness
*For any* backend response, the HTTP status code should be 200 for success, 400 for validation errors, and 500 for server errors.
**Validates: Requirements 7.4**

### Property 17: JSON response format
*For any* backend response, the response body should be valid JSON with a "status" field and appropriate "data" or "message" fields.
**Validates: Requirements 7.5**

## Error Handling

### Frontend Error Handling
- **Network Errors**: Display user-friendly error messages when backend is unreachable
- **Invalid Responses**: Handle malformed JSON responses gracefully
- **Empty Results**: Show appropriate message when no logs match the query
- **Loading States**: Provide visual feedback during API calls

### Backend Error Handling
- **Loki Unavailable**: Return 503 Service Unavailable with descriptive message
- **Invalid Requests**: Return 400 Bad Request with validation error details
- **Missing Parameters**: Return 400 with specific parameter requirements
- **Loki API Errors**: Log error details and return 500 Internal Server Error
- **Log Push Failures**: Log locally and continue operation without blocking

### Error Response Format
```json
{
  "status": "error",
  "message": "Descriptive error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

## Testing Strategy

### Unit Testing
The system will use comprehensive unit testing to verify specific behaviors and edge cases:

**Frontend Unit Tests (Vitest + Vue Test Utils)**:
- Component rendering and prop handling
- Event emission and handling
- API service functions
- Error state handling
- UI component examples (search box, label selector, timestamp inputs exist)

**Backend Unit Tests (pytest)**:
- API endpoint responses and status codes
- Request validation logic
- Loki client functions
- Logger module functionality
- Configuration loading
- Error handling paths

### Property-Based Testing
The system will use property-based testing to verify universal properties across all inputs:

**Frontend Property Tests (fast-check)**:
- Library: fast-check (JavaScript/TypeScript property-based testing)
- Minimum iterations: 100 per property
- Each test tagged with: `// Feature: log-query-system, Property X: [property text]`

**Backend Property Tests (Hypothesis)**:
- Library: Hypothesis (Python property-based testing)
- Minimum iterations: 100 per property
- Each test tagged with: `# Feature: log-query-system, Property X: [property text]`

**Property Test Coverage**:
- Label retrieval and data flow (Properties 1-3)
- Log querying with various parameters (Properties 5-9)
- Backend logging behavior (Properties 10-13)
- Response formatting and validation (Properties 14-17)

### Integration Testing
- End-to-end tests for complete user workflows
- Frontend-Backend integration tests
- Backend-Loki integration tests with test Loki instance

### Test Data Strategy
- Use property-based testing generators for random valid inputs
- Include edge cases: empty strings, special characters, boundary timestamps
- Mock Loki responses for isolated backend testing
- Use test Loki instance for integration tests
