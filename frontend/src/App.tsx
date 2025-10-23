/**
 * Main App Component - Orchestration Graph Scheduler
 * Complete reimplementation in React TypeScript
 */

import React, { useEffect, useState } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { useOrchestrationStore, useIsConnected, useIsLoading, useError } from './store/orchestrationStore';
import OrchestrationTimeline from './components/Timeline/OrchestrationTimeline';
import ActivityLibraryPanel from './components/Library/ActivityLibraryPanel';
import ToolbarPanel from './components/Toolbar/ToolbarPanel';
import { ActivityData, InstantiatedActivity } from './types/domain';
import './App.css';

const App: React.FC = () => {
  const { initialize, clearError } = useOrchestrationStore();
  const isConnected = useIsConnected();
  const isLoading = useIsLoading();
  const error = useError();
  const [hoveredActivity, setHoveredActivity] = useState<{
    name: string;
    description?: string;
    time?: number;
    minTime?: number;
    maxTime?: number;
    plane?: number;
    planeName?: string;
    startsAfter?: number;
    endsAfter?: number;
  } | null>(null);

  const handleLibraryHover = (activity: ActivityData | null) => {
    if (activity) {
      setHoveredActivity({
        name: activity.name,
        description: activity.description,
        time: activity.defT,
        minTime: activity.minT,
        maxTime: activity.maxT,
        plane: activity.defPlane,
        planeName: activity.planeName,
      });
    } else {
      setHoveredActivity(null);
    }
  };

  const handleTimelineHover = (activity: InstantiatedActivity | null) => {
    if (activity) {
      setHoveredActivity({
        name: activity.activityName,
        description: activity.activityDescription,
        time: activity.time,
        plane: activity.plane,
        startsAfter: activity.startsAfter,
        endsAfter: activity.endsAfter,
      });
    } else {
      setHoveredActivity(null);
    }
  };

  // Initialize on mount
  useEffect(() => {
    initialize();
  }, [initialize]);

  // Loading state
  if (isLoading && !isConnected) {
    return (
      <div className="app-loading">
        <div className="loading-spinner" />
        <div style={{ marginTop: '16px', fontSize: '16px', color: '#6b7280' }}>
          Connecting to backend...
        </div>
      </div>
    );
  }

  // Error state
  if (error && !isConnected) {
    return (
      <div className="app-error">
        <div style={{ fontSize: '48px', marginBottom: '16px' }}></div>
        <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '8px' }}>
          Connection Error
        </div>
        <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '16px' }}>
          {error}
        </div>
        <button
          onClick={() => {
            clearError();
            initialize();
          }}
          style={{
            padding: '8px 16px',
            background: '#0ea5e9',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="app-container">
        {/* Header */}
        <header className="app-header">
          <div>
            <h1>Orchestration Graph Scheduler</h1>
            <div className="header-subtitle">
              Build optimized lesson plans with activity orchestration
            </div>
          </div>
          <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
            <div className="status-indicator" />
            {isConnected ? 'Connected' : 'Disconnected'}
          </div>
        </header>

        {/* Toolbar */}
        <ToolbarPanel />

        {/* Main Content */}
        <div className="app-body">
          {/* Timeline (Main Area) */}
          <div className="timeline-area">
            <OrchestrationTimeline onActivityHover={handleTimelineHover} />
          </div>

          {/* Library (Right Panel) */}
          <div className="library-area">
            <ActivityLibraryPanel onActivityHover={handleLibraryHover} />
          </div>
        </div>

        {/* Activity Hover Tooltip */}
        {hoveredActivity && (
          <div
            style={{
              position: 'fixed',
              bottom: '20px',
              left: '50%',
              transform: 'translateX(-50%)',
              background: 'rgba(0, 0, 0, 0.9)',
              color: 'white',
              padding: '12px 16px',
              borderRadius: '8px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
              zIndex: 1000,
              maxWidth: '500px',
              pointerEvents: 'none',
            }}
          >
            <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '4px' }}>
              {hoveredActivity.name}
            </div>
            {hoveredActivity.description && (
              <div style={{ fontSize: '13px', opacity: 0.9, marginBottom: '8px' }}>
                {hoveredActivity.description}
              </div>
            )}
            <div style={{ fontSize: '12px', opacity: 0.7 }}>
              {hoveredActivity.time && `Duration: ${hoveredActivity.time} min`}
              {hoveredActivity.planeName && ` • Plane: ${hoveredActivity.planeName}`}
              {hoveredActivity.minTime !== undefined && hoveredActivity.maxTime !== undefined &&
                hoveredActivity.minTime !== hoveredActivity.maxTime &&
                ` • Time: ${hoveredActivity.minTime}' - ${hoveredActivity.maxTime}'`}
              {hoveredActivity.startsAfter !== undefined && ` | Starts at: ${hoveredActivity.startsAfter} min`}
              {hoveredActivity.endsAfter !== undefined && ` | Ends at: ${hoveredActivity.endsAfter} min`}
            </div>
          </div>
        )}

        {/* Error Toast */}
        {error && isConnected && (
          <div className="error-toast">
            <div style={{ flex: 1 }}>{error}</div>
            <button
              onClick={clearError}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'white',
                cursor: 'pointer',
                fontSize: '18px',
              }}
            >
              ×
            </button>
          </div>
        )}

        {/* Loading Overlay */}
        {isLoading && (
          <div className="loading-overlay">
            <div className="loading-spinner" />
          </div>
        )}
      </div>
    </DndProvider>
  );
};

export default App;
