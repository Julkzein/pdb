/**
 * Teacher Context Store
 * Manages LLM-enhanced orchestration state
 */

import { create } from 'zustand';
import { OrchestrationGraphState } from '../types/domain';
import { apiService } from '../services/apiService';

export interface TeacherContext {
  ageGroup: string;
  subject: string;
}

export interface ResourceItem {
  type: 'video' | 'worksheet' | 'tool' | 'simulation' | 'article' | 'reference' | 'community';
  title: string;
  description?: string;
  suggestedUrl?: string;
}

export interface ActivityEnhancement {
  activityPosition: number;
  activityName: string;
  concreteExample: string;
  resources: ResourceItem[];
  teachingTips: string;
  timeManagement?: string;
}

export interface OverallSuggestions {
  ageAdaptations: string;
  subjectContext: string;
  estimatedDifficulty: 'easy' | 'moderate' | 'challenging';
}

export interface EnhancementData {
  overallSuggestions: OverallSuggestions;
  activityEnhancements: ActivityEnhancement[];
  additionalResources: ResourceItem[];
}

export interface EnhancementMetadata {
  model: string;
  provider?: string;
  ageGroup: string;
  subject: string;
  inputTokens?: number;
  outputTokens?: number;
}

interface TeacherContextState {
  // Teacher context (age/subject)
  teacherContext: TeacherContext | null;

  // LLM enhancements
  enhancementData: EnhancementData | null;
  enhancementMetadata: EnhancementMetadata | null;

  // Loading and error states
  isLoading: boolean;
  error: string | null;

  // Modal visibility
  isModalOpen: boolean;

  // Actions
  setTeacherContext: (context: TeacherContext) => void;
  generateEnhancement: (orchestration: OrchestrationGraphState, context: TeacherContext) => Promise<void>;
  clearEnhancement: () => void;
  openModal: () => void;
  closeModal: () => void;
  regenerateEnhancement: (orchestration: OrchestrationGraphState) => Promise<void>;
}

export const useTeacherContextStore = create<TeacherContextState>((set, get) => ({
  teacherContext: null,
  enhancementData: null,
  enhancementMetadata: null,
  isLoading: false,
  error: null,
  isModalOpen: false,

  setTeacherContext: (context) => {
    set({ teacherContext: context });
  },

  generateEnhancement: async (orchestration, context) => {
    set({ isLoading: true, error: null });

    try {
      const result = await apiService.enhanceOrchestration(orchestration, context.ageGroup, context.subject);

      set({
        teacherContext: context,
        enhancementData: result.enhancements,
        enhancementMetadata: result.metadata,
        isLoading: false,
        error: null,
        isModalOpen: false,
      });
    } catch (err: any) {
      set({
        isLoading: false,
        error: err.message || 'Failed to generate enhancement',
      });
      throw err;
    }
  },

  regenerateEnhancement: async (orchestration) => {
    const { teacherContext } = get();

    if (!teacherContext) {
      throw new Error('No teacher context available for regeneration');
    }

    await get().generateEnhancement(orchestration, teacherContext);
  },

  clearEnhancement: () => {
    set({
      teacherContext: null,
      enhancementData: null,
      enhancementMetadata: null,
      error: null,
    });
  },

  openModal: () => {
    set({ isModalOpen: true, error: null });
  },

  closeModal: () => {
    set({ isModalOpen: false });
  },
}));
