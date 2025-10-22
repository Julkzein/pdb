// frontend/src/components/LessonTimeline.tsx
import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

interface TimelineActivity {
  id: string;
  name: string;
  startTime: number;
  duration: number;
  color: string;
}

const LessonTimeline: React.FC = () => {
  const [timelineActivities, setTimelineActivities] = useState<TimelineActivity[]>([]);
  const [totalDuration, setTotalDuration] = useState(0);

  // Calculate total duration when activities change
  useEffect(() => {
    const total = timelineActivities.reduce((sum, act) => sum + act.duration, 0);
    setTotalDuration(total);
  }, [timelineActivities]);

  // This will be connected to your graph later
  // For now, it's a visual component showing the timeline
  const addActivityToTimeline = (activity: TimelineActivity) => {
    setTimelineActivities(prev => [...prev, activity]);
  };

  const removeActivityFromTimeline = (activityId: string) => {
    setTimelineActivities(prev => prev.filter(act => act.id !== activityId));
  };

  const exportTimeline = async () => {
    try {
      const data = await api.exportOrchestration();
      console.log('Exported timeline:', data);
      // Handle export (download file, etc.)
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  return (
    <div className="lesson-timeline" style={{
      marginTop: '20px',
      padding: '20px',
      background: '#f9fafb',
      borderRadius: '8px',
      minHeight: '200px',
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '15px' 
      }}>
        <h3 style={{ margin: '0', color: '#374151' }}>
          Lesson Timeline
        </h3>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <span style={{ color: '#6b7280', fontSize: '14px' }}>
            Total Duration: {totalDuration} min
          </span>
          <button
            onClick={exportTimeline}
            style={{
              padding: '6px 12px',
              background: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Export
          </button>
        </div>
      </div>
      
      {/* Timeline visualization */}
      <div style={{ 
        position: 'relative',
        background: 'white',
        borderRadius: '4px',
        padding: '20px',
        minHeight: '100px',
      }}>
        {/* Time ruler */}
        <div style={{
          position: 'absolute',
          top: '0',
          left: '20px',
          right: '20px',
          height: '20px',
          borderBottom: '1px solid #e5e7eb',
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '11px',
          color: '#9ca3af',
        }}>
          <span>0 min</span>
          <span>30 min</span>
          <span>60 min</span>
          <span>90 min</span>
          <span>120 min</span>
        </div>
        
        {/* Activities on timeline */}
        <div style={{ 
          marginTop: '30px',
          position: 'relative',
          minHeight: '60px',
          display: 'flex',
          alignItems: 'center',
        }}>
          {timelineActivities.length === 0 ? (
            <p style={{ 
              color: '#9ca3af', 
              margin: 'auto',
              textAlign: 'center',
              width: '100%',
            }}>
              Activities from the graph will appear here in chronological order
            </p>
          ) : (
            <div style={{ 
              display: 'flex', 
              gap: '2px',
              width: '100%',
            }}>
              {timelineActivities.map((activity, index) => {
                const widthPercentage = (activity.duration / 120) * 100; // Assuming 120 min max
                return (
                  <div
                    key={activity.id}
                    style={{
                      width: `${widthPercentage}%`,
                      minWidth: '60px',
                      padding: '8px',
                      background: activity.color || '#e5e7eb',
                      borderRadius: '4px',
                      fontSize: '12px',
                      color: 'white',
                      textAlign: 'center',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      cursor: 'pointer',
                      transition: 'transform 0.2s',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-2px)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                    }}
                    title={`${activity.name} - ${activity.duration} min`}
                  >
                    {activity.name}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
      
      {/* Legend */}
      <div style={{
        marginTop: '15px',
        padding: '10px',
        background: '#f3f4f6',
        borderRadius: '4px',
        fontSize: '12px',
        color: '#6b7280',
      }}>
        💡 Tip: Connect activities in the graph to see them arranged on the timeline
      </div>
    </div>
  );
};

export default LessonTimeline;