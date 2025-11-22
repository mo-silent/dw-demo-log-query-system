# Implementation Plan

- [x] 1. Set up project structure and dependencies
  - Create backend directory structure (routes, loki_client, logger, config, tests)
  - Create frontend directory structure (components, services, types)
  - Set up Python Flask project with requirements.txt
  - Set up Vue.js 3.0 project with TypeScript
  - Install testing frameworks: pytest, Hypothesis for backend; Vitest, fast-check for frontend
  - _Requirements: 5.1, 5.2_

- [x] 2. Implement backend configuration module
  - Create config.py with Loki URL and endpoint configurations
  - Define default label constant (app:main)
  - Add environment variable support for configuration
  - _Requirements: 7.1, 7.2_

- [ ] 3. Implement Loki client module
- [x] 3.1 Create loki_client.py with basic structure
  - Implement get_labels() function to fetch labels from Loki
  - Implement query_logs() function with label and timestamp parameters
  - Implement push_log() function to send logs to Loki
  - Add error handling for Loki API failures
  - _Requirements: 1.2, 3.4, 4.2_

- [x] 3.2 Write property test for Loki client
  - **Property 2: Backend queries Loki for labels**
  - **Property 8: Backend forwards queries to Loki**
  - **Property 11: Logs pushed to correct endpoint**
  - **Validates: Requirements 1.2, 3.4, 4.2**

- [x] 3.3 Write unit tests for Loki client
  - Test get_labels() with mocked Loki responses
  - Test query_logs() with various parameter combinations
  - Test push_log() success and failure scenarios
  - Test error handling for network failures
  - _Requirements: 1.2, 3.4, 4.2_

- [x] 4. Implement backend logger module
- [x] 4.1 Create logger.py with async log pushing
  - Implement logger that pushes to Loki with "app: main" label
  - Add fallback to local logging if Loki is unavailable
  - Support log levels: DEBUG, INFO, WARNING, ERROR
  - Implement async push to avoid blocking operations
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 4.2 Write property test for logger module
  - **Property 10: Backend operations generate logs**
  - **Property 12: Backend logs labeled correctly**
  - **Validates: Requirements 4.1, 4.3**

- [x] 4.3 Write unit tests for logger module
  - Test log generation for different log levels
  - Test async log pushing behavior
  - Test fallback to local logging on Loki failure
  - Test label attachment to all logs
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [-] 5. Implement backend API routes
- [x] 5.1 Create routes.py with Flask blueprint
  - Implement GET /api/v1/loki/label endpoint
  - Implement POST /api/v1/loki/logs endpoint
  - Add request validation for required parameters
  - Add logging for all API operations
  - Implement error response formatting
  - _Requirements: 1.2, 1.3, 3.3, 3.4, 3.5, 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 5.2 Write property test for API routes
  - **Property 3: Label data round-trip**
  - **Property 7: Label parameter validation**
  - **Property 9: Log data round-trip from Loki**
  - **Property 15: Request body parameter parsing**
  - **Property 16: HTTP status code correctness**
  - **Property 17: JSON response format**
  - **Validates: Requirements 1.3, 3.3, 3.5, 7.3, 7.4, 7.5**

- [x] 5.3 Write unit tests for API routes
  - Test GET /api/v1/loki/label success and error cases
  - Test POST /api/v1/loki/logs with valid parameters
  - Test POST /api/v1/loki/logs with missing label parameter
  - Test POST /api/v1/loki/logs with timestamp parameters
  - Test error response formatting
  - Test HTTP status codes for different scenarios
  - _Requirements: 1.2, 1.3, 3.3, 3.4, 3.5, 7.3, 7.4, 7.5_

- [x] 6. Create Flask application entry point
  - Create app.py with Flask app initialization
  - Register routes blueprint
  - Configure CORS for frontend communication
  - Add startup logging
  - _Requirements: 4.1_

- [x] 7. Implement frontend data models and types
  - Create TypeScript interfaces: SearchCriteria, LogEntry, ApiResponse
  - Define type guards for API responses
  - _Requirements: 3.1, 3.2_

- [-] 8. Implement frontend API service
- [x] 8.1 Create api.ts service module
  - Implement fetchLabels() function
  - Implement fetchLogs() function with SearchCriteria parameter
  - Add error handling for network failures
  - Add response validation
  - _Requirements: 1.1, 3.1, 3.2_

- [ ]* 8.2 Write property test for API service
  - **Property 1: Label retrieval triggers backend query**
  - **Property 5: Search submission sends POST with label**
  - **Property 6: Timestamp inclusion in requests**
  - **Validates: Requirements 1.1, 3.1, 3.2**

- [ ]* 8.3 Write unit tests for API service
  - Test fetchLabels() with mocked responses
  - Test fetchLogs() with various search criteria
  - Test error handling for failed requests
  - Test request body formatting
  - _Requirements: 1.1, 3.1, 3.2_

- [ ] 9. Implement SearchBox component
- [x] 9.1 Create SearchBox.vue component
  - Add label selector dropdown
  - Add timestamp input fields (start and end)
  - Add search button
  - Emit search event with SearchCriteria
  - Add form validation
  - _Requirements: 3.1, 3.2, 6.1, 6.2, 6.3_

- [ ]* 9.2 Write unit tests for SearchBox component
  - Test component rendering with props
  - Test search event emission
  - Test form validation
  - Test timestamp input handling
  - _Requirements: 3.1, 3.2, 6.1, 6.2, 6.3_

- [x] 10. Implement LogDisplay component
- [x] 10.1 Create LogDisplay.vue component
  - Display log entries with formatted timestamps
  - Add syntax highlighting for log content
  - Implement auto-scroll to latest logs
  - Add loading state indicator
  - Handle empty log state
  - _Requirements: 2.4, 6.4, 6.5_

- [ ]* 10.2 Write property test for LogDisplay component
  - **Property 4: Log display renders received data**
  - **Property 14: Log entry formatting**
  - **Validates: Requirements 2.4, 6.5**

- [ ]* 10.3 Write unit tests for LogDisplay component
  - Test rendering with log data
  - Test loading state display
  - Test empty state display
  - Test timestamp formatting
  - _Requirements: 2.4, 6.4, 6.5_

- [x] 11. Implement App root component
- [x] 11.1 Create App.vue component
  - Add state management for labels, logs, and loading
  - Implement onMounted lifecycle to fetch labels and default logs
  - Connect SearchBox and LogDisplay components
  - Handle search event from SearchBox
  - Add error handling and display
  - _Requirements: 1.1, 2.1, 2.4, 3.6_

- [ ]* 11.2 Write property test for App component
  - Test default log loading on mount
  - Test search flow integration
  - **Validates: Requirements 1.1, 2.1**

- [ ]* 11.3 Write unit tests for App component
  - Test component initialization
  - Test label fetching on mount
  - Test default log fetching with "app: main"
  - Test search handling
  - Test error state handling
  - _Requirements: 1.1, 2.1, 2.4_

- [x] 12. Add frontend styling and UI polish
  - Add CSS for layout and component styling
  - Ensure search box is at top of interface
  - Ensure log display area is below search box
  - Add responsive design
  - Add loading spinners
  - _Requirements: 6.1, 6.4_

- [x] 13. Configure test logging to Loki
- [x] 13.1 Update test configuration
  - Configure pytest to push test logs to Loki
  - Add test execution logging with "app: main" label
  - Ensure test logs include test names and results
  - _Requirements: 5.3_

- [x] 13.2 Write property test for test logging
  - **Property 13: Test execution generates logs**
  - **Validates: Requirements 5.3**

- [x] 14. Create project documentation
  - Write README with setup instructions
  - Document API endpoints
  - Document environment variables
  - Add development and testing instructions
  - _Requirements: All_

- [ ]* 15. Final checkpoint - Ensure all tests pass
  - Run all backend unit tests and property tests
  - Run all frontend unit tests and property tests
  - Verify integration between frontend and backend
  - Test with actual Loki instance
  - Ensure all tests pass, ask the user if questions arise
