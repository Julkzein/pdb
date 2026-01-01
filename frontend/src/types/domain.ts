/**
 * Domain types for Orchestration Graph
 * Mirrors the Python backend data structures
 */

// ==================== PARAMETRIC VALUES ==================== //

/**
 * Parametric Value - represents multi-dimensional understanding state
 * Typically 2D: [fluency, depth] both ranging from 0 to 1
 */
export interface PValue {
  v: number[];  // e.g., [0.5, 0.3]
}

/**
 * Interpolated Parametric Value - time-dependent effect
 */
export interface InterPValue {
  minEffect: PValue;
  maxEffect: PValue;
  minT: number;
  maxT: number;
  defT: number;
}

// ==================== ACTIVITIES ==================== //

/**
 * Activity template from the library
 */
export interface ActivityData {
  idx: number;
  name: string;
  description?: string;  // Brief description of the activity
  pcond: PValue;  // Prerequisite condition
  peffect: InterPValue;  // Effect (time-interpolated)
  minT: number;
  maxT: number;
  defT: number;
  canChangeTime: boolean;
  maxRepetition: number;
  defPlane: number;  // 0=Indiv, 1=Team, 2=Class
  planeName?: string;
  planeDescription?: string;
  explanation?: string;  // Explanation of why to use this activity
  sources?: string;  // Academic sources backing this activity
  llmPrompt?: string;  // Activity-specific LLM prompt template
}

/**
 * Instantiated activity - a specific occurrence in the timeline
 */
export interface InstantiatedActivity {
  activityIdx: number;
  activityName: string;
  activityDescription?: string;  // Brief description of the activity
  time: number;  // Chosen duration
  plane: number;  // Chosen plane (0/1/2)
  startsAfter: number;  // Cumulative start time
  endsAfter: number;  // Cumulative end time
  pValStart: PValue;  // State before activity
  pValEnd: PValue;  // State after activity
}

// ==================== CONTEXT & FLAGS ==================== //

/**
 * Flags indicating issues with an activity choice
 */
export interface ActivityFlags {
  exhausted: boolean;  // Used too many times
  tooLong: boolean;  // Too long for remaining time
  noProgress: boolean;  // Makes no progress toward goal
}

/**
 * Activity with evaluation context for recommendations
 */
export interface ContextActivity {
  activity: ActivityData;
  score: number | null;
  isBest: boolean;
  flags: ActivityFlags;
  okeyToTake: boolean;
}

// ==================== ORCHESTRATION GRAPH ==================== //

/**
 * Gap p-value information
 */
export interface GapPValueInfo {
  position: number;
  fromPValue: PValue;
  toPValue: PValue;
  distance: number;
  isHard: boolean;
}

/**
 * Complete orchestration graph state
 */
export interface OrchestrationGraphState {
  activities: InstantiatedActivity[];
  totTime: number;
  tBudget: number;
  start: PValue;
  goal: PValue;
  reached: PValue;
  hardGapsCount: number;
  hardGapsList: number[];
  remainingGapsDistance: number;
  goalReached: boolean;
  gapPValueInfo: GapPValueInfo[];
}

/**
 * Gap information
 */
export interface GapInfo {
  index: number;
  isHard: boolean;
  distance?: number;
}

/**
 * Recommendation response
 */
export interface RecommendationResponse {
  gapIndex: number;
  recommendations: ContextActivity[];
  isHardGap: boolean;
}

// ==================== PLANES ==================== //

export interface PlaneInfo {
  index: number;
  name: string;
  description: string;
}

export const PLANE_NAMES = ["Indiv.", "Team", "Class"];
export const PLANE_DESCRIPTIONS = ["individually", "in teams", "as a class"];

// ==================== UI STATE ==================== //

/**
 * UI interaction state
 */
export interface UIState {
  selectedGap: number | null;
  selectedActivity: number | null;  // Position in timeline
  isDragging: boolean;
  showRecommendations: boolean;
  isLoading: boolean;
}

/**
 * App configuration
 */
export interface AppConfig {
  timeBudget: number;
  start: number[];
  goal: number[];
  threshold: number;
  precision: number;
}

// ==================== API RESPONSES ==================== //

export interface ApiResponse<T = any> {
  success?: boolean;
  message?: string;
  error?: string;
  data?: T;
}

export interface HealthResponse {
  status: string;
  message: string;
  library_loaded: boolean;
  library_size: number;
  graph_initialized: boolean;
}

export interface SavedFileInfo {
  filename: string;
  size: number;
  modified: string;
}

// ==================== UTILITY TYPES ==================== //

export type PlaneIndex = 0 | 1 | 2;

export interface Position {
  x: number;
  y: number;
}

// ==================== TYPE GUARDS ==================== //

export function isPValue(obj: any): obj is PValue {
  return obj && Array.isArray(obj.v);
}

export function isActivityData(obj: any): obj is ActivityData {
  return obj && typeof obj.idx === 'number' && typeof obj.name === 'string';
}

export function isInstantiatedActivity(obj: any): obj is InstantiatedActivity {
  return obj && typeof obj.activityIdx === 'number' && typeof obj.time === 'number';
}

// ==================== UTILITY FUNCTIONS ==================== //

/**
 * Format a PValue for display
 */
export function formatPValue(pval: PValue): string {
  return `(${pval.v.map(v => v.toFixed(2)).join(', ')})`;
}

/**
 * Get plane name by index
 */
export function getPlaneName(index: number): string {
  return PLANE_NAMES[index] || 'Unknown';
}

/**
 * Get plane description by index
 */
export function getPlaneDescription(index: number): string {
  return PLANE_DESCRIPTIONS[index] || 'unknown';
}

/**
 * Format time in minutes
 */
export function formatTime(minutes: number): string {
  return `${minutes}'`;
}

/**
 * Calculate percentage of time budget used
 */
export function calculateTimePercentage(used: number, budget: number): number {
  return (used / budget) * 100;
}

/**
 * Check if time budget is exceeded
 */
export function isOverBudget(used: number, budget: number): boolean {
  return used > budget;
}

/**
 * Get color for time budget display
 */
export function getTimeBudgetColor(used: number, budget: number): string {
  const percentage = calculateTimePercentage(used, budget);
  if (percentage >= 100) return '#ef4444';  // red
  if (percentage >= 80) return '#f59e0b';   // amber
  return '#10b981';  // green
}

/**
 * Get color for plane
 */
export function getPlaneColor(plane: number): string {
  const colors = ['#06b6d4', '#a855f7', '#f43f5e'];  // cyan, purple, rose
  return colors[plane] || '#6b7280';
}
