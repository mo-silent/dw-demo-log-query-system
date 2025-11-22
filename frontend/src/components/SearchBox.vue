<template>
  <div class="search-box">
    <form @submit.prevent="handleSubmit" class="search-form">
      <!-- Label Filters Section -->
      <div class="filters-section">
        <label class="section-label">Label filters</label>
        
        <div class="label-filters">
          <div class="filter-row">
            <!-- Label Key Dropdown -->
            <select 
              v-model="selectedLabelKey" 
              class="filter-select filter-key"
              @change="onLabelKeyChange"
            >
              <option value="">Select label</option>
              <option v-for="label in availableLabels" :key="label" :value="label">
                {{ label }}
              </option>
            </select>

            <!-- Operator (always =) -->
            <div class="filter-operator">=</div>

            <!-- Label Value Dropdown -->
            <select 
              v-model="selectedLabelValue"
              class="filter-select filter-value"
              :disabled="!selectedLabelKey || loadingValues"
              @change="onFilterChange"
            >
              <option value="">{{ loadingValues ? 'Loading...' : 'Select value' }}</option>
              <option v-for="value in availableValues" :key="value" :value="value">
                {{ value }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- Time Range Section -->
      <div class="time-section">
        <div class="form-group">
          <label for="start-time">Start Time (optional):</label>
          <input 
            id="start-time"
            v-model="startTime"
            type="datetime-local"
            class="form-control"
            :max="endTime"
          />
        </div>

        <div class="form-group">
          <label for="end-time">End Time (optional):</label>
          <input 
            id="end-time"
            v-model="endTime"
            type="datetime-local"
            class="form-control"
            :min="startTime"
          />
        </div>
      </div>

      <!-- Search Button -->
      <div class="search-button-container">
        <button type="submit" class="btn-search" :disabled="!isFormValid">
          <span class="btn-icon">🔍</span>
          <span>Search</span>
        </button>
      </div>

      <div v-if="validationError" class="error-message">
        {{ validationError }}
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { fetchLabelValues } from '../services/api';
import type { SearchCriteria } from '../types';

interface Props {
  availableLabels: string[];
}

defineProps<Props>();

const emit = defineEmits<{
  search: [criteria: SearchCriteria];
}>();

const selectedLabelKey = ref<string>('app');
const selectedLabelValue = ref<string>('main');
const availableValues = ref<string[]>([]);
const loadingValues = ref<boolean>(false);
const startTime = ref<string>('');
const endTime = ref<string>('');
const validationError = ref<string>('');

const isFormValid = computed(() => {
  if (!selectedLabelKey.value || !selectedLabelValue.value) {
    return false;
  }

  if (startTime.value && endTime.value) {
    const start = new Date(startTime.value);
    const end = new Date(endTime.value);
    if (start >= end) {
      return false;
    }
  }

  return true;
});

async function onLabelKeyChange() {
  selectedLabelValue.value = '';
  availableValues.value = [];
  validationError.value = '';
  
  if (!selectedLabelKey.value) {
    return;
  }

  // Fetch values for the selected label
  loadingValues.value = true;
  try {
    availableValues.value = await fetchLabelValues(selectedLabelKey.value);
    
    // Auto-select first value if available
    if (availableValues.value.length > 0) {
      selectedLabelValue.value = availableValues.value[0];
    }
  } catch (error) {
    validationError.value = error instanceof Error ? error.message : 'Failed to load label values';
    console.error('Error loading label values:', error);
  } finally {
    loadingValues.value = false;
  }
}

function onFilterChange() {
  validationError.value = '';
}

function handleSubmit() {
  validationError.value = '';

  if (!selectedLabelKey.value || !selectedLabelValue.value) {
    validationError.value = 'Please select both label and value';
    return;
  }

  if (startTime.value && endTime.value) {
    const start = new Date(startTime.value);
    const end = new Date(endTime.value);
    
    if (start >= end) {
      validationError.value = 'Start time must be before end time';
      return;
    }
  }

  const criteria: SearchCriteria = {
    label: `${selectedLabelKey.value}:${selectedLabelValue.value}`,
  };

  if (startTime.value) {
    criteria.startTime = new Date(startTime.value).toISOString();
  }

  if (endTime.value) {
    criteria.endTime = new Date(endTime.value).toISOString();
  }

  emit('search', criteria);
}

// Load initial values for default label
onLabelKeyChange();
</script>


<style scoped>
.search-box {
  padding: 28px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 20px;
  margin-bottom: 28px;
  box-shadow: 0 4px 24px rgba(59, 130, 246, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-box:hover {
  box-shadow: 0 8px 32px rgba(59, 130, 246, 0.12);
  border-color: rgba(59, 130, 246, 0.3);
}

.search-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Label Filters Section */
.filters-section {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.section-label {
  font-weight: 600;
  color: #475569;
  font-size: 15px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  font-size: 12px;
}

.label-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%);
  backdrop-filter: blur(10px);
  padding: 10px 16px;
  border-radius: 12px;
  border: 1px solid rgba(14, 165, 233, 0.2);
  box-shadow: 0 2px 12px rgba(14, 165, 233, 0.08);
  transition: all 0.2s ease;
}

.filter-row:hover {
  border-color: rgba(14, 165, 233, 0.4);
  box-shadow: 0 4px 20px rgba(14, 165, 233, 0.15);
}

.filter-select,
.filter-input {
  padding: 8px 12px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 8px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.9);
  color: #1e293b;
  font-family: inherit;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.filter-select:hover,
.filter-input:hover {
  border-color: rgba(14, 165, 233, 0.5);
  background: #ffffff;
}

.filter-select:focus,
.filter-input:focus {
  outline: none;
  border-color: #0ea5e9;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

.filter-key,
.filter-value {
  min-width: 140px;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23475569' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 34px;
}

.filter-value {
  min-width: 160px;
}

.filter-value:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2394a3b8' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
}

.filter-operator {
  color: #0ea5e9;
  font-weight: 700;
  font-size: 18px;
  padding: 0 6px;
}

/* Time Section */
.time-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.form-group label {
  margin-bottom: 10px;
  font-weight: 600;
  color: #475569;
  font-size: 14px;
  letter-spacing: 0.3px;
}

.form-control {
  padding: 12px 16px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 12px;
  font-size: 14px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(255, 255, 255, 0.9);
  color: #1e293b;
  font-family: inherit;
}

.form-control:hover {
  border-color: rgba(14, 165, 233, 0.5);
  background: #ffffff;
}

.form-control:focus {
  outline: none;
  border-color: #0ea5e9;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

/* Search Button */
.search-button-container {
  display: flex;
  justify-content: flex-end;
}

.btn-search {
  padding: 14px 40px;
  background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 50%, #06b6d4 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(14, 165, 233, 0.3);
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  position: relative;
  overflow: hidden;
}

.btn-search::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.btn-search:hover::before {
  left: 100%;
}

.btn-search .btn-icon {
  font-size: 18px;
  width: auto;
  height: auto;
}

.btn-search:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(14, 165, 233, 0.4);
}

.btn-search:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 12px rgba(14, 165, 233, 0.3);
}

.btn-search:disabled {
  background: rgba(148, 163, 184, 0.5);
  cursor: not-allowed;
  box-shadow: none;
  opacity: 0.5;
}

.error-message {
  padding: 16px 20px;
  background: rgba(254, 226, 226, 0.9);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #dc2626;
  border-radius: 12px;
  font-size: 14px;
  backdrop-filter: blur(10px);
  animation: shake 0.4s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

/* Responsive design */
@media (max-width: 768px) {
  .search-box {
    padding: 24px;
    border-radius: 16px;
  }

  .label-filters {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-row {
    flex-wrap: wrap;
  }

  .time-section {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .search-button-container {
    justify-content: stretch;
  }

  .btn-search {
    width: 100%;
    padding: 12px 32px;
  }
}

@media (max-width: 480px) {
  .search-box {
    padding: 20px;
    border-radius: 14px;
    margin-bottom: 20px;
  }

  .filter-key,
  .filter-value {
    min-width: 110px;
    font-size: 13px;
    padding: 7px 10px;
  }

  .form-control {
    padding: 10px 14px;
    font-size: 13px;
  }

  .btn-search {
    padding: 11px 28px;
    font-size: 14px;
  }
}
</style>
