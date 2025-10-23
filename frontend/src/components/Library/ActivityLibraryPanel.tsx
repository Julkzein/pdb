/**
 * Activity Library Panel
 * Shows available activities with drag-and-drop support
 * Shows recommendations when a gap is selected
 */

import React from 'react';
import { useDrag } from 'react-dnd';
import { useOrchestrationStore, useActivities, useRecommendations } from '../../store/orchestrationStore';
import { ActivityData, ContextActivity, formatTime } from '../../types/domain';
import './ActivityLibraryPanel.css';

interface DraggableActivityProps {
  activity: ActivityData;
  contextInfo?: ContextActivity;
  onHover?: (activity: ActivityData | null) => void;
}

const DraggableActivity: React.FC<DraggableActivityProps> = ({ activity, contextInfo, onHover }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'LIBRARY_ACTIVITY',
    item: { actIdx: activity.idx },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }));

  const isBest = contextInfo?.isBest || false;
  const isInvalid = contextInfo && !contextInfo.okeyToTake;
  const flags = contextInfo?.flags;

  const handleMouseEnter = () => {
    if (onHover) onHover(activity);
  };

  const handleMouseLeave = () => {
    if (onHover) onHover(null);
  };

  return (
    <div
      ref={drag as any}
      className={`activity-card ${isBest ? 'best' : ''} ${isInvalid ? 'invalid' : ''}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      style={{
        opacity: isDragging ? 0.5 : 1,
        cursor: isDragging ? 'grabbing' : 'grab',
        background: isBest ? '#10b981' : isInvalid ? '#9ca3af' : '#4ade80',
        color: 'white',
        padding: '12px',
        margin: '8px 0',
        borderRadius: '6px',
        border: isBest ? '2px solid #059669' : '1px solid rgba(0,0,0,0.1)',
        position: 'relative',
      }}
    >
      {isBest && (
        <div style={{ position: 'absolute', top: '4px', right: '4px', fontSize: '16px' }}>
          
        </div>
      )}
      <div style={{ fontWeight: 'bold', marginBottom: '4px', fontSize: '14px' }}>
        {activity.name}
      </div>
      <div style={{ fontSize: '12px', opacity: 0.9 }}>
        {formatTime(activity.defT)} | {activity.planeName}
      </div>
      {contextInfo && (
        <div style={{ marginTop: '8px', fontSize: '11px' }}>
          {contextInfo.score !== null && (
            <div>Score: {contextInfo.score.toFixed(4)}</div>
          )}
          {flags && (flags.exhausted || flags.tooLong || flags.noProgress) && (
            <div style={{ display: 'flex', gap: '4px', marginTop: '4px', flexWrap: 'wrap' }}>
              {flags.exhausted && <span className="flag">Exhausted</span>}
              {flags.tooLong && <span className="flag">Too Long</span>}
              {flags.noProgress && <span className="flag">No Progress</span>}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

interface ActivityLibraryPanelProps {
  onActivityHover?: (activity: ActivityData | null) => void;
}

const ActivityLibraryPanel: React.FC<ActivityLibraryPanelProps> = ({ onActivityHover }) => {
  const activities = useActivities();
  const recommendations = useRecommendations();
  const { showRecommendations, selectedGap, clearGapSelection } = useOrchestrationStore();

  const displayActivities = showRecommendations
    ? recommendations.map(rec => rec.activity)
    : activities;

  return (
    <div className="library-panel">
      <div className="library-header">
        <h3>Activity Library</h3>
        <div style={{ fontSize: '12px', color: '#6b7280' }}>
          {activities.length} activities
        </div>
      </div>

      {showRecommendations && selectedGap !== null && (
        <div className="recommendation-header">
          <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '8px', color: '#0ea5e9' }}>
            Recommendations for Gap {selectedGap}
          </div>
          <button
            onClick={clearGapSelection}
            style={{
              background: '#e0f2fe',
              border: '1px solid #0ea5e9',
              borderRadius: '4px',
              padding: '4px 8px',
              fontSize: '12px',
              cursor: 'pointer',
            }}
          >
            Show All Activities
          </button>
        </div>
      )}

      <div className="activity-list">
        {showRecommendations ? (
          recommendations.length > 0 ? (
            recommendations.map((rec, idx) => (
              <DraggableActivity
                key={idx}
                activity={rec.activity}
                contextInfo={rec}
                onHover={onActivityHover}
              />
            ))
          ) : (
            <div style={{ padding: '20px', textAlign: 'center', color: '#9ca3af' }}>
              No recommendations available
            </div>
          )
        ) : (
          displayActivities.map((activity) => (
            <DraggableActivity
              key={activity.idx}
              activity={activity}
              onHover={onActivityHover}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default ActivityLibraryPanel;
