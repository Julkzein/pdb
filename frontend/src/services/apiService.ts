/**
 * API Service for communicating with Flask backend
 * All API calls go through this service
 */

import axios, { AxiosInstance } from 'axios';
import {
  ActivityData,
  OrchestrationGraphState,
  RecommendationResponse,
  HealthResponse,
  SavedFileInfo,
  PlaneInfo,
  AppConfig
} from '../types/domain';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000/api';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // Increased to 30 seconds to handle backend restarts
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      response => response,
      error => {
        console.error('API Error:', error);
        if (error.response) {
          // Server responded with error status
          const message = error.response.data.message || error.response.data.error || 'Server error';
          const status = error.response.status;

          // Provide more specific error messages based on status code
          if (status === 504) {
            throw new Error(`Timeout: ${message}`);
          } else if (status === 503) {
            throw new Error(`Service unavailable: ${message}`);
          } else {
            throw new Error(message);
          }
        } else if (error.request) {
          // Request made but no response
          if (error.code === 'ECONNABORTED') {
            throw new Error('Request timeout - the operation took too long. Try with fewer activities.');
          }
          throw new Error('Cannot connect to backend - please check if the server is running');
        } else {
          // Something else happened
          throw new Error(error.message);
        }
      }
    );
  }

  // ==================== HEALTH & CONFIG ==================== //

  async healthCheck(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }

  async getConfig(): Promise<AppConfig> {
    const response = await this.client.get<AppConfig>('/config/params');
    return response.data;
  }

  async getPlanes(): Promise<PlaneInfo[]> {
    const response = await this.client.get<{ planes: PlaneInfo[] }>('/config/planes');
    return response.data.planes;
  }

  // ==================== ACTIVITIES ==================== //

  async getActivities(): Promise<ActivityData[]> {
    const response = await this.client.get<ActivityData[]>('/activities');
    return response.data;
  }

  async createActivity(activityData: any): Promise<{ success: boolean; message: string; activity: ActivityData }> {
    const response = await this.client.post('/activities/create', activityData);
    return response.data;
  }

  async reloadLibrary(): Promise<{ success: boolean; message: string; activity_count: number }> {
    const response = await this.client.post('/library/reload');
    return response.data;
  }

  // ==================== GRAPH STATE ==================== //

  async getGraphState(): Promise<OrchestrationGraphState> {
    const response = await this.client.get<OrchestrationGraphState>('/graph/state');
    return response.data;
  }

  async resetGraph(): Promise<{ success: boolean; state: OrchestrationGraphState }> {
    const response = await this.client.post('/graph/reset');
    return response.data;
  }

  // ==================== GRAPH MANIPULATION ==================== //

  async insertActivity(
    actIdx: number,
    position: number,
    plane?: number,
    time?: number
  ): Promise<{ success: boolean; state: OrchestrationGraphState }> {
    const response = await this.client.post('/graph/insert', {
      actIdx,
      position,
      plane,
      time
    });
    return response.data;
  }

  async removeActivity(position: number): Promise<{ success: boolean; state: OrchestrationGraphState }> {
    const response = await this.client.post('/graph/remove', { position });
    return response.data;
  }

  async changePlane(position: number, plane: number): Promise<{ success: boolean; state: OrchestrationGraphState }> {
    const response = await this.client.post('/graph/change-plane', { position, plane });
    return response.data;
  }

  async exchangeActivities(
    posA: number,
    posB: number
  ): Promise<{ success: boolean; state: OrchestrationGraphState }> {
    const response = await this.client.post('/graph/exchange', { posA, posB });
    return response.data;
  }

  // ==================== GAPS & RECOMMENDATIONS ==================== //

  async getGaps(): Promise<{
    hardGapsList: number[];
    hardGapsCount: number;
    remainingGapsDistance: number;
  }> {
    const response = await this.client.get('/graph/gaps');
    return response.data;
  }

  async setGapFocus(gapIndex: number): Promise<RecommendationResponse> {
    const response = await this.client.post<RecommendationResponse>('/graph/gap/focus', { gapIndex });
    return response.data;
  }

  async getGapRecommendations(gapIndex: number): Promise<RecommendationResponse> {
    const response = await this.client.post<RecommendationResponse>('/graph/gap/recommendations', { gapIndex });
    return response.data;
  }

  // ==================== AUTO-ADD ==================== //

  async autoAdd(): Promise<{ success: boolean; message: string; state?: OrchestrationGraphState }> {
    const response = await this.client.post('/graph/auto-add');
    return response.data;
  }

  async autoAddFromGap(): Promise<{ success: boolean; message: string; state?: OrchestrationGraphState }> {
    const response = await this.client.post('/graph/auto-add-from-gap');
    return response.data;
  }

  async autoComplete(): Promise<{
    success: boolean;
    message: string;
    activitiesAdded: number;
    goalReached: boolean;
    state: OrchestrationGraphState
  }> {
    const response = await this.client.post('/graph/auto-complete', {}, { timeout: 60000 });
    return response.data;
  }

  // ==================== SAVE/LOAD ==================== //

  async saveGraph(filename?: string): Promise<{ success: boolean; filename: string; message: string }> {
    const response = await this.client.post('/graph/save', { filename });
    return response.data;
  }

  async loadGraph(filename: string): Promise<{ success: boolean; message: string; state: OrchestrationGraphState }> {
    const response = await this.client.post('/graph/load', { filename });
    return response.data;
  }

  // ==================== VISUALIZATION ==================== //

  async visualizeGraph(): Promise<{ success: boolean; image: string; format: string }> {
    const response = await this.client.get('/graph/visualize');
    return response.data;
  }

  async getSavedFiles(): Promise<SavedFileInfo[]> {
    const response = await this.client.get<SavedFileInfo[]>('/graph/saved-files');
    return response.data;
  }

  // ==================== EXPORT/PRINT ==================== //

  async exportJSON(): Promise<OrchestrationGraphState> {
    const response = await this.client.get<OrchestrationGraphState>('/graph/export-json');
    return response.data;
  }

  async printText(): Promise<{ content: string; format: string }> {
    const response = await this.client.get('/graph/print-text');
    return response.data;
  }

  // ==================== LLM ENHANCEMENT ==================== //

  async enhanceOrchestration(
    orchestration: OrchestrationGraphState,
    ageGroup: string,
    subject: string
  ): Promise<any> {
    // Increase timeout for LLM requests (can be slow)
    // Based on ~10s per activity, allow up to 120s for 5+ activities
    const response = await this.client.post(
      '/enhance-orchestration',
      {
        orchestration,
        ageGroup,
        subject,
      },
      { timeout: 120000 } // 120 second (2 minute) timeout for LLM
    );
    return response.data;
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export helper function for enhance orchestration
export const enhanceOrchestration = (
  orchestration: OrchestrationGraphState,
  ageGroup: string,
  subject: string
) => apiService.enhanceOrchestration(orchestration, ageGroup, subject);

// Export class for testing
export default ApiService;
