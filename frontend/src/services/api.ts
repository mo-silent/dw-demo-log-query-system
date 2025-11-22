import type { SearchCriteria, LogEntry } from '../types';
import { isApiResponse, isStringArray, isLogEntryArray } from '../types';

const API_BASE_URL = 'http://localhost:8081';

/**
 * Fetch available labels from the backend
 * @returns Promise resolving to array of label strings
 * @throws Error if the request fails or response is invalid
 */
export async function fetchLabels(): Promise<string[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/loki/label`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const json: unknown = await response.json();

    // Validate response structure
    if (!isApiResponse<string[]>(json)) {
      throw new Error('Invalid response format from server');
    }

    if (json.status === 'error') {
      throw new Error(json.message || 'Failed to fetch labels');
    }

    if (!json.data || !isStringArray(json.data)) {
      throw new Error('Invalid label data format');
    }

    return json.data;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to fetch labels: ${error.message}`);
    }
    throw new Error('Failed to fetch labels: Unknown error');
  }
}

/**
 * Fetch available values for a specific label from the backend
 * @param labelName - Name of the label to fetch values for
 * @returns Promise resolving to array of value strings
 * @throws Error if the request fails or response is invalid
 */
export async function fetchLabelValues(labelName: string): Promise<string[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/loki/label/${labelName}/values`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const json: unknown = await response.json();

    // Validate response structure
    if (!isApiResponse<string[]>(json)) {
      throw new Error('Invalid response format from server');
    }

    if (json.status === 'error') {
      throw new Error(json.message || 'Failed to fetch label values');
    }

    if (!json.data || !isStringArray(json.data)) {
      throw new Error('Invalid label values data format');
    }

    return json.data;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to fetch label values: ${error.message}`);
    }
    throw new Error('Failed to fetch label values: Unknown error');
  }
}

/**
 * Fetch logs from the backend based on search criteria
 * @param criteria - Search criteria including label and optional timestamps
 * @returns Promise resolving to array of log entries
 * @throws Error if the request fails or response is invalid
 */
export async function fetchLogs(criteria: SearchCriteria): Promise<LogEntry[]> {
  try {
    const requestBody: Record<string, string> = {
      label: criteria.label,
    };

    // Include optional timestamp parameters if provided
    if (criteria.startTime) {
      requestBody.start_time = criteria.startTime;
    }

    if (criteria.endTime) {
      requestBody.end_time = criteria.endTime;
    }

    const response = await fetch(`${API_BASE_URL}/api/v1/loki/logs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const json: unknown = await response.json();

    // Validate response structure
    if (!isApiResponse<LogEntry[]>(json)) {
      throw new Error('Invalid response format from server');
    }

    if (json.status === 'error') {
      throw new Error(json.message || 'Failed to fetch logs');
    }

    if (!json.data || !isLogEntryArray(json.data)) {
      throw new Error('Invalid log data format');
    }

    return json.data;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to fetch logs: ${error.message}`);
    }
    throw new Error('Failed to fetch logs: Unknown error');
  }
}
