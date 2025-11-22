<template>
  <div class="log-display">
    <!-- Loading state -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading logs...</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="logs.length === 0" class="empty-state">
      <p>No logs found</p>
      <p class="empty-hint">Try adjusting your search criteria</p>
    </div>

    <!-- Log entries -->
    <div v-else class="log-entries" ref="logContainer">
      <div 
        v-for="(log, index) in logs" 
        :key="`${log.timestamp}-${index}`"
        class="log-entry"
        :class="getLogLevelClass(log.level)"
      >
        <span class="log-timestamp">{{ formatTimestamp(log.timestamp) }}</span>
        <span class="log-level" v-if="log.level">{{ log.level }}</span>
        <span class="log-labels">{{ formatLabels(log.labels) }}</span>
        <pre class="log-message">{{ log.message }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import type { LogEntry } from '../types';

interface Props {
  logs: LogEntry[];
  loading: boolean;
}

const props = defineProps<Props>();

const logContainer = ref<HTMLElement | null>(null);

// Format timestamp to readable format
function formatTimestamp(timestamp: string): string {
  try {
    const date = new Date(timestamp);
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
      return timestamp;
    }
    
    // Format: YYYY-MM-DD HH:MM:SS
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  } catch (error) {
    return timestamp;
  }
}

// Format labels object to string
function formatLabels(labels: Record<string, string>): string {
  return Object.entries(labels)
    .map(([key, value]) => `${key}:${value}`)
    .join(', ');
}

// Get CSS class based on log level
function getLogLevelClass(level?: string): string {
  if (!level) return '';
  
  const levelLower = level.toLowerCase();
  
  if (levelLower === 'error') return 'log-level-error';
  if (levelLower === 'warning' || levelLower === 'warn') return 'log-level-warning';
  if (levelLower === 'info') return 'log-level-info';
  if (levelLower === 'debug') return 'log-level-debug';
  
  return '';
}

// Auto-scroll to latest logs when new logs are added
watch(() => props.logs, async () => {
  if (props.logs.length > 0 && logContainer.value) {
    await nextTick();
    logContainer.value.scrollTop = logContainer.value.scrollHeight;
  }
}, { deep: true });
</script>

<style scoped>
.log-display {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 20px;
  padding: 24px;
  min-height: 500px;
  max-height: 700px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 24px rgba(59, 130, 246, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.log-display:hover {
  box-shadow: 0 8px 32px rgba(59, 130, 246, 0.12);
  border-color: rgba(59, 130, 246, 0.3);
}

/* Loading state */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 450px;
  color: #64748b;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(14, 165, 233, 0.2);
  border-top-color: #0ea5e9;
  border-radius: 50%;
  animation: spin 0.8s cubic-bezier(0.4, 0, 0.2, 1) infinite;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(14, 165, 233, 0.2);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-state p {
  font-size: 16px;
  font-weight: 500;
  color: #475569;
}

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 450px;
  color: #64748b;
}

.empty-state p {
  margin: 6px 0;
  font-size: 17px;
  color: #475569;
  font-weight: 500;
}

.empty-hint {
  font-size: 15px;
  color: #94a3b8;
}

/* Log entries container */
.log-entries {
  overflow-y: auto;
  flex: 1;
}

/* Scrollbar styling */
.log-entries::-webkit-scrollbar {
  width: 12px;
}

.log-entries::-webkit-scrollbar-track {
  background: rgba(226, 232, 240, 0.5);
  border-radius: 6px;
}

.log-entries::-webkit-scrollbar-thumb {
  background: rgba(14, 165, 233, 0.3);
  border-radius: 6px;
  transition: background 0.3s ease;
}

.log-entries::-webkit-scrollbar-thumb:hover {
  background: rgba(14, 165, 233, 0.5);
}

/* Individual log entry */
.log-entry {
  padding: 14px 16px;
  margin-bottom: 10px;
  background: rgba(248, 250, 252, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 10px;
  border-left: 3px solid #0ea5e9;
  font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', Consolas, Monaco, monospace;
  font-size: 13px;
  line-height: 1.6;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(148, 163, 184, 0.15);
}

.log-entry:hover {
  background: #ffffff;
  transform: translateX(4px);
  border-color: rgba(14, 165, 233, 0.3);
  box-shadow: 0 2px 12px rgba(14, 165, 233, 0.1);
}

.log-entry:last-child {
  margin-bottom: 0;
}

/* Log level specific colors */
.log-level-error {
  border-left-color: #ef4444;
  background: rgba(254, 226, 226, 0.5);
}

.log-level-error:hover {
  background: rgba(254, 226, 226, 0.8);
}

.log-level-warning {
  border-left-color: #f59e0b;
  background: rgba(254, 243, 199, 0.5);
}

.log-level-warning:hover {
  background: rgba(254, 243, 199, 0.8);
}

.log-level-info {
  border-left-color: #3b82f6;
  background: rgba(219, 234, 254, 0.5);
}

.log-level-info:hover {
  background: rgba(219, 234, 254, 0.8);
}

.log-level-debug {
  border-left-color: #6b7280;
  background: rgba(243, 244, 246, 0.5);
}

.log-level-debug:hover {
  background: rgba(243, 244, 246, 0.8);
}

/* Log entry components */
.log-timestamp {
  color: #64748b;
  margin-right: 14px;
  font-weight: 500;
  font-size: 12px;
}

.log-level {
  display: inline-block;
  padding: 4px 10px;
  margin-right: 14px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.log-level-error .log-level {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.log-level-warning .log-level {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.log-level-info .log-level {
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
}

.log-level-debug .log-level {
  background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%);
  color: white;
}

.log-labels {
  color: #0ea5e9;
  margin-right: 14px;
  font-size: 12px;
  font-weight: 600;
}

.log-message {
  color: #334155;
  margin: 10px 0 0 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', Consolas, Monaco, monospace;
  font-size: 13px;
  line-height: 1.6;
}


/* Responsive design */
@media (max-width: 768px) {
  .log-display {
    padding: 16px;
    border-radius: 12px;
    min-height: 350px;
    max-height: 500px;
  }

  .loading-state,
  .empty-state {
    height: 350px;
  }

  .spinner {
    width: 36px;
    height: 36px;
    border-width: 3px;
  }

  .loading-state p {
    font-size: 14px;
  }

  .empty-state p {
    font-size: 15px;
  }

  .empty-hint {
    font-size: 13px;
  }

  .log-entry {
    padding: 10px 12px;
    margin-bottom: 6px;
    font-size: 12px;
    border-left-width: 3px;
  }

  .log-timestamp {
    margin-right: 10px;
    font-size: 11px;
  }

  .log-level {
    padding: 2px 6px;
    margin-right: 10px;
    font-size: 10px;
  }

  .log-labels {
    margin-right: 10px;
    font-size: 11px;
  }

  .log-message {
    font-size: 12px;
    margin-top: 6px;
  }
}

@media (max-width: 480px) {
  .log-display {
    padding: 12px;
    border-radius: 10px;
    min-height: 300px;
    max-height: 450px;
  }

  .loading-state,
  .empty-state {
    height: 300px;
  }

  .spinner {
    width: 32px;
    height: 32px;
    border-width: 3px;
    margin-bottom: 12px;
  }

  .loading-state p {
    font-size: 13px;
  }

  .empty-state p {
    font-size: 14px;
  }

  .empty-hint {
    font-size: 12px;
  }

  .log-entry {
    padding: 8px 10px;
    margin-bottom: 6px;
    font-size: 11px;
    border-left-width: 3px;
    border-radius: 6px;
  }

  .log-timestamp {
    display: block;
    margin-right: 0;
    margin-bottom: 4px;
    font-size: 10px;
  }

  .log-level {
    padding: 2px 5px;
    margin-right: 8px;
    font-size: 9px;
  }

  .log-labels {
    display: block;
    margin-right: 0;
    margin-bottom: 4px;
    font-size: 10px;
  }

  .log-message {
    font-size: 11px;
    margin-top: 4px;
    line-height: 1.4;
  }
}
</style>
