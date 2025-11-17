/**
 * Zustand Store for Orchestration Graph State
 * Single source of truth for app state
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
  ActivityData,
  OrchestrationGraphState,
  ContextActivity,
  PlaneInfo,
  AppConfig
} from '../types/domain';
import { apiService } from '../services/apiService';

interface OrchestrationStore {
  // ==================== STATE ==================== //

  // Connection
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;

  // Library
  activities: ActivityData[];
  planes: PlaneInfo[];
  config: AppConfig | null;

  // Graph State
  graphState: OrchestrationGraphState | null;

  // UI State
  selectedGap: number | null;
  recommendations: ContextActivity[];
  showRecommendations: boolean;

  // ==================== ACTIONS ==================== //

  // Initialization
  initialize: () => Promise<void>;
  checkConnection: () => Promise<boolean>;

  // Library
  loadActivities: () => Promise<void>;
  loadPlanes: () => Promise<void>;
  loadConfig: () => Promise<void>;
  createActivity: (activityData: any) => Promise<void>;

  // Graph State
  refreshGraphState: () => Promise<void>;
  resetGraph: () => Promise<void>;

  // Graph Manipulation
  insertActivity: (actIdx: number, position: number, plane?: number, time?: number) => Promise<void>;
  removeActivity: (position: number) => Promise<void>;
  changePlane: (position: number, plane: number) => Promise<void>;
  exchangeActivities: (posA: number, posB: number) => Promise<void>;

  // Gap Selection & Recommendations
  selectGap: (gapIndex: number) => Promise<void>;
  clearGapSelection: () => void;

  // Auto-add
  autoAdd: () => Promise<void>;
  autoAddFromGap: () => Promise<void>;

  // Save/Load
  saveGraph: (filename?: string) => Promise<string>;
  loadGraph: (filename: string) => Promise<void>;

  // Utility
  setError: (error: string | null) => void;
  clearError: () => void;
}

export const useOrchestrationStore = create<OrchestrationStore>()(
  devtools(
    (set, get) => ({
      // ==================== INITIAL STATE ==================== //

      isConnected: false,
      isLoading: false,
      error: null,

      activities: [],
      planes: [],
      config: null,

      graphState: null,

      selectedGap: null,
      recommendations: [],
      showRecommendations: false,

      // ==================== INITIALIZATION ==================== //

      initialize: async () => {
        set({ isLoading: true, error: null });

        try {
          // Check connection
          await get().checkConnection();

          // Load initial data in parallel
          await Promise.all([
            get().loadActivities(),
            get().loadPlanes(),
            get().loadConfig(),
            get().refreshGraphState()
          ]);

          set({ isLoading: false });
          console.log('Store initialized successfully');
        } catch (error: any) {
          set({
            error: error.message || 'Failed to initialize',
            isLoading: false
          });
          console.error('Store initialization failed:', error);
        }
      },

      checkConnection: async () => {
        try {
          const health = await apiService.healthCheck();
          const connected = health.status === 'healthy' && health.library_loaded;
          set({ isConnected: connected });
          return connected;
        } catch (error) {
          set({ isConnected: false });
          return false;
        }
      },

      // ==================== LIBRARY ==================== //

      loadActivities: async () => {
        try {
          const activities = await apiService.getActivities();
          set({ activities });
          console.log(`Loaded ${activities.length} activities`);
        } catch (error: any) {
          set({ error: error.message });
          throw error;
        }
      },

      loadPlanes: async () => {
        try {
          const planes = await apiService.getPlanes();
          set({ planes });
        } catch (error: any) {
          set({ error: error.message });
          throw error;
        }
      },

      loadConfig: async () => {
        try {
          const config = await apiService.getConfig();
          set({ config });
        } catch (error: any) {
          set({ error: error.message });
          throw error;
        }
      },

      createActivity: async (activityData: any) => {
        set({ isLoading: true });
        try {
          await apiService.createActivity(activityData);
          await get().loadActivities();
          set({ isLoading: false });
        } catch (error: any) {
          set({ error: error.message, isLoading: false });
          throw error;
        }
      },

      // ==================== GRAPH STATE ==================== //

      refreshGraphState: async () => {
        try {
          const graphState = await apiService.getGraphState();
          set({ graphState });
        } catch (error: any) {
          set({ error: error.message });
          throw error;
        }
      },

      resetGraph: async () => {
        set({ isLoading: true });
        try {
          const result = await apiService.resetGraph();
          set({
            graphState: result.state,
            selectedGap: null,
            recommendations: [],
            showRecommendations: false,
            isLoading: false
          });
          console.log('Graph reset');
        } catch (error: any) {
          set({ error: error.message, isLoading: false });
          throw error;
        }
      },

      // ==================== GRAPH MANIPULATION ==================== //

      insertActivity: async (actIdx, position, plane?, time?) => {
        set({ isLoading: true });
        try {
          const result = await apiService.insertActivity(actIdx, position, plane, time);
          set({
            graphState: result.state,
            isLoading: false
          });

          // If a gap is selected, refresh recommendations
          const { selectedGap } = get();
          if (selectedGap !== null) {
            await get().selectGap(selectedGap);
          }

          console.log(`Inserted activity ${actIdx} at position ${position}`);
        } catch (error: any) {
          set({ error: error.message, isLoading: false });
          throw error;
        }
      },

      changePlane: async (position, plane) => {
        set({ isLoading: true });
        try {
          const result = await apiService.changePlane(position, plane);
          set({
            graphState: result.state,
            isLoading: false
          });
          console.log(`Changed activity ${position} to plane ${plane}`);
        } catch (error: any) {
          set({ error: error.message, isLoading: false });
          throw error;
        }
      },

      removeActivity: async (position) => {
        set({ isLoading: true });
        try {
          const result = await apiService.removeActivity(position);
          set({
            graphState: result.state,
            isLoading: false
          });

          // Refresh recommendations if gap selected
          const { selectedGap } = get();
          if (selectedGap !== null) {
            await get().selectGap(selectedGap);
          }

          console.log(`Removed activity at position ${position}`);
        } catch (error: any) {
          set({ error: error.message, isLoading: false });
          throw error;
        }
      },

      exchangeActivities: async (posA, posB) => {
        set({ isLoading: true });
        try {
          const result = await apiService.exchangeActivities(posA, posB);
          set({
            graphState: result.state,
            isLoading: false
          });
          console.log(`Exchanged activities at ${posA} and ${posB}`);
        } catch (error: any) {
          set({ error: error.message, isLoading: false });
          throw error;
        }
      },

      // ==================== GAP SELECTION ==================== //

      selectGap: async (gapIndex) => {
        set({ isLoading: true, selectedGap: gapIndex });
        try {
          const result = await apiService.setGapFocus(gapIndex);
          set({
            recommendations: result.recommendations,
            showRecommendations: true,
            isLoading: false
          });
          console.log(`Selected gap ${gapIndex}, got ${result.recommendations.length} recommendations`);
        } catch (error: any) {
          set({ error: error.message, isLoading: false });
          throw error;
        }
      },

      clearGapSelection: () => {
        set({
          selectedGap: null,
          recommendations: [],
          showRecommendations: false
        });
      },

      // ==================== AUTO-ADD ==================== //

      autoAdd: async () => {
        set({ isLoading: true });
        try {
          const result = await apiService.autoAdd();
          if (result.success && result.state) {
            set({
              graphState: result.state,
              isLoading: false
            });
            console.log(`${result.message}`);
          } else {
            throw new Error(result.message || 'Auto-add failed');
          }
        } catch (error: any) {
          set({ error: error.message, isLoading: false });
          throw error;
        }
      },

      autoAddFromGap: async () => {
        set({ isLoading: true });
        try {
          const result = await apiService.autoAddFromGap();
          if (result.success && result.state) {
            set({
              graphState: result.state,
              isLoading: false
            });

            // Refresh recommendations for the selected gap
            const { selectedGap } = get();
            if (selectedGap !== null) {
              await get().selectGap(selectedGap);
            }

            console.log(`${result.message}`);
          } else {
            throw new Error(result.message || 'Auto-add failed');
          }
        } catch (error: any) {
          set({ error: error.message, isLoading: false });
          throw error;
        }
      },

      // ==================== SAVE/LOAD ==================== //

      saveGraph: async (filename?) => {
        set({ isLoading: true });
        try {
          const result = await apiService.saveGraph(filename);
          set({ isLoading: false });
          console.log(`${result.message}`);
          return result.filename;
        } catch (error: any) {
          set({ error: error.message, isLoading: false });
          throw error;
        }
      },

      loadGraph: async (filename) => {
        set({ isLoading: true });
        try {
          const result = await apiService.loadGraph(filename);
          set({
            graphState: result.state,
            selectedGap: null,
            recommendations: [],
            showRecommendations: false,
            isLoading: false
          });
          console.log(`${result.message}`);
        } catch (error: any) {
          set({ error: error.message, isLoading: false });
          throw error;
        }
      },

      // ==================== UTILITY ==================== //

      setError: (error) => {
        set({ error });
      },

      clearError: () => {
        set({ error: null });
      }
    }),
    { name: 'OrchestrationStore' }
  )
);

// Export selectors for convenience
export const useActivities = () => useOrchestrationStore(state => state.activities);
export const useGraphState = () => useOrchestrationStore(state => state.graphState);
export const useRecommendations = () => useOrchestrationStore(state => state.recommendations);
export const useIsConnected = () => useOrchestrationStore(state => state.isConnected);
export const useIsLoading = () => useOrchestrationStore(state => state.isLoading);
export const useError = () => useOrchestrationStore(state => state.error);
