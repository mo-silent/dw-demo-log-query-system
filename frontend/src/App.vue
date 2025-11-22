<template>
  <div id="app">
    <header class="app-header">
      <h1>Log Query System</h1>
    </header>

    <main class="app-main">
      <!-- Error display -->
      <div v-if="error" class="error-banner">
        <span class="error-icon">⚠️</span>
        <span class="error-text">{{ error }}</span>
        <button @click="dismissError" class="error-dismiss">×</button>
      </div>

      <!-- Search box component -->
      <SearchBox 
        :available-labels="labels" 
        @search="handleSearch"
      />

      <!-- Log display component -->
      <LogDisplay 
        :logs="logs" 
        :loading="loading"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import SearchBox from './components/SearchBox.vue';
import LogDisplay from './components/LogDisplay.vue';
import { fetchLabels, fetchLogs } from './services/api';
import type { SearchCriteria, LogEntry } from './types';

// State management
const labels = ref<string[]>([]);
const logs = ref<LogEntry[]>([]);
const loading = ref<boolean>(false);
const error = ref<string>('');

/**
 * Fetch labels from backend
 */
async function loadLabels(): Promise<void> {
  try {
    labels.value = await fetchLabels();
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Failed to load labels';
    error.value = errorMessage;
    console.error('Error loading labels:', err);
  }
}

/**
 * Fetch logs based on search criteria
 */
async function loadLogs(criteria: SearchCriteria): Promise<void> {
  loading.value = true;
  error.value = '';

  try {
    logs.value = await fetchLogs(criteria);
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Failed to load logs';
    error.value = errorMessage;
    console.error('Error loading logs:', err);
    logs.value = [];
  } finally {
    loading.value = false;
  }
}

/**
 * Handle search event from SearchBox component
 */
function handleSearch(criteria: SearchCriteria): void {
  loadLogs(criteria);
}

/**
 * Dismiss error banner
 */
function dismissError(): void {
  error.value = '';
}

/**
 * Initialize app on mount
 * - Fetch available labels
 * - Load default logs with "app:main" label
 */
onMounted(async () => {
  // Fetch labels first
  await loadLabels();

  // Load default logs with "app:main" label
  const defaultCriteria: SearchCriteria = {
    label: 'app:main',
  };
  
  await loadLogs(defaultCriteria);
});
</script>

<style>
/* Global styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
  background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 50%, #ffffff 100%);
  background-attachment: fixed;
  min-height: 100vh;
  color: #1e293b;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  color: #0f172a;
  padding: 24px 40px;
  box-shadow: 0 2px 16px rgba(59, 130, 246, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.app-header h1 {
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.8px;
  background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 50%, #06b6d4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: inline-block;
}

.app-main {
  flex: 1;
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
  padding: 40px 32px;
}

/* Error banner */
.error-banner {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 24px;
  margin-bottom: 28px;
  background: rgba(254, 226, 226, 0.9);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 16px;
  color: #dc2626;
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.1);
  backdrop-filter: blur(10px);
  animation: slideDown 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.error-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.error-text {
  flex: 1;
  font-size: 15px;
  line-height: 1.6;
  font-weight: 500;
  color: #991b1b;
}

.error-dismiss {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  font-size: 24px;
  color: #dc2626;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
}

.error-dismiss:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.4);
  transform: scale(1.05);
}

.error-dismiss:active {
  transform: scale(0.95);
}

/* Responsive design */
@media (max-width: 768px) {
  .app-header {
    padding: 20px 24px;
  }

  .app-header h1 {
    font-size: 26px;
  }

  .app-main {
    padding: 28px 20px;
  }

  .error-banner {
    padding: 16px 20px;
    gap: 12px;
    border-radius: 12px;
  }

  .error-icon {
    font-size: 22px;
  }

  .error-text {
    font-size: 14px;
  }

  .error-dismiss {
    width: 28px;
    height: 28px;
    font-size: 22px;
  }
}

@media (max-width: 480px) {
  .app-header {
    padding: 18px 20px;
  }

  .app-header h1 {
    font-size: 22px;
  }

  .app-main {
    padding: 20px 16px;
  }

  .error-banner {
    padding: 14px 16px;
    gap: 10px;
  }
}
</style>
