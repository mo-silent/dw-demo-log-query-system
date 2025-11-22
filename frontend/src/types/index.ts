// TypeScript type definitions
export interface SearchCriteria {
  label: string;
  startTime?: string;
  endTime?: string;
}

export interface LogEntry {
  timestamp: string;
  message: string;
  labels: Record<string, string>;
  level?: string;
}

export interface ApiResponse<T> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
}

// Type guards for API responses
export function isApiResponse<T>(value: unknown): value is ApiResponse<T> {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  
  const obj = value as Record<string, unknown>;
  
  // Check required status field
  if (typeof obj.status !== 'string' || (obj.status !== 'success' && obj.status !== 'error')) {
    return false;
  }
  
  // Check optional data field exists when status is success
  if (obj.status === 'success' && !('data' in obj)) {
    return false;
  }
  
  // Check optional message field is string if present
  if ('message' in obj && typeof obj.message !== 'string') {
    return false;
  }
  
  return true;
}

export function isLogEntry(value: unknown): value is LogEntry {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  
  const obj = value as Record<string, unknown>;
  
  // Check required fields
  if (typeof obj.timestamp !== 'string') {
    return false;
  }
  
  if (typeof obj.message !== 'string') {
    return false;
  }
  
  if (typeof obj.labels !== 'object' || obj.labels === null || Array.isArray(obj.labels)) {
    return false;
  }
  
  // Validate labels is a Record<string, string>
  const labels = obj.labels as Record<string, unknown>;
  for (const key in labels) {
    if (typeof labels[key] !== 'string') {
      return false;
    }
  }
  
  // Check optional level field
  if ('level' in obj && typeof obj.level !== 'string') {
    return false;
  }
  
  return true;
}

export function isLogEntryArray(value: unknown): value is LogEntry[] {
  if (!Array.isArray(value)) {
    return false;
  }
  
  return value.every(item => isLogEntry(item));
}

export function isStringArray(value: unknown): value is string[] {
  if (!Array.isArray(value)) {
    return false;
  }
  
  return value.every(item => typeof item === 'string');
}
