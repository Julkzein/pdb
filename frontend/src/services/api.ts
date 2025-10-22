// frontend/src/services/api.ts
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 5000,
});

export const api = {
  healthCheck: async () => {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },
  
  getActivities: async () => {
    const response = await apiClient.get('/activities');
    return response.data;
  },
  
  createOrchestration: async (data: any) => {
    const response = await apiClient.post('/orchestration/create', data);
    return response.data;
  },
  
  validateOrchestration: async (data: any) => {
    const response = await apiClient.post('/orchestration/validate', data);
    return response.data;
  },
  
  exportOrchestration: async () => {
    const response = await apiClient.get('/orchestration/export');
    return response.data;
  },
  
  getRecommendation: async (gapIndex: number = 0) => {
    const response = await apiClient.post('/orchestration/recommend', { gapIndex });
    return response.data;
  },
  
  saveOrchestration: async (filename: string) => {
    const response = await apiClient.post('/orchestration/save', { filename });
    return response.data;
  },
  
  loadOrchestration: async (filename: string) => {
    const response = await apiClient.post('/orchestration/load', { filename });
    return response.data;
  },
  
  printOrchestration: async () => {
    const response = await apiClient.get('/orchestration/print');
    return response.data;
  },
  
  // New methods for gap-based recommendations
  getOrchestrationState: async () => {
    const response = await apiClient.get('/orchestration/state');
    return response.data;
  },
  
  setGapFocus: async (gapIndex: number) => {
    const response = await apiClient.post('/orchestration/set-gap-focus', { gapIndex });
    return response.data;
  },
  
  autoAddFromGap: async () => {
    const response = await apiClient.post('/orchestration/auto-add-from-gap', {});
    return response.data;
  },
  
  evaluateGaps: async () => {
    const response = await apiClient.post('/orchestration/evaluate-gaps', {});
    return response.data;
  },
  
  autoAdd: async () => {
    const response = await apiClient.post('/orchestration/auto-add', {});
    return response.data;
  },
  
  getActivitiesForGap: async (gapIndex: number) => {
    const response = await apiClient.post('/orchestration/activities-for-gap', { gapIndex });
    return response.data;
  },
};