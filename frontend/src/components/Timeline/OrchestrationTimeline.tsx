/**
 * Orchestration Timeline - Main swimlane timeline component
 * Fixed version with smooth drag-and-drop - NO STACKING!
 */

import React, { useState } from 'react';
import { useOrchestrationStore } from '../../store/orchestrationStore';
import { InstantiatedActivity, GapPValueInfo, getPlaneColor, formatTime, formatPValue } from '../../types/domain';
import { useDrop, useDrag } from 'react-dnd';
import './OrchestrationTimeline.css';

// Activity name abbreviations based on the original QML
const getActivityAbbreviation = (name: string): string => {
  const abbreviations: Record<string, string> = {
    'TellTheClass': 'TellTheClass',
    'DesirableDifficultyProblem': 'DDProblem',
    'PracticeMemory': 'PMemory',
    'PracticeApplication': 'PApplication',
    'PracticeAnalyse': 'PAnalyse',
    'PracticeEvaluate': 'PEvaluate',
    'PracticeCreate': 'PCreate',
    'AdvancedOrganiser': 'AOrganiser',
    'Introduction': 'Intro',
    'ExplainClass': 'ExplainClass',
  };
  return abbreviations[name] || name;
};

interface DropZoneProps {
  position: number;
  isHard: boolean;
  plane: number;
  gapInfo?: GapPValueInfo;
  onDrop: (actIdx: number, position: number, plane: number) => void;
}

const DropZone: React.FC<DropZoneProps> = ({ position, isHard, plane, gapInfo, onDrop }) => {
  const { selectedGap, selectGap } = useOrchestrationStore();
  const isSelected = selectedGap === position;
  const [showTooltip, setShowTooltip] = useState(false);

  const [{ isOver, canDrop }, drop] = useDrop(() => ({
    accept: 'LIBRARY_ACTIVITY',
    drop: (item: { actIdx: number }) => {
      onDrop(item.actIdx, position, plane);
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
      canDrop: monitor.canDrop(),
    }),
  }));

  const handleClick = () => {
    selectGap(position);
  };

  const isActive = isOver && canDrop;

  return (
    <div
      ref={drop as any}
      className={`drop-zone ${isSelected ? 'selected' : ''} ${isActive ? 'active' : ''}`}
      onClick={handleClick}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
      style={{
        width: isActive ? '80px' : isSelected ? '60px' : '30px',
        minWidth: isActive ? '80px' : isSelected ? '60px' : '30px',
        background: isActive ? '#bfdbfe' : isSelected ? '#e0f2fe' : 'transparent',
        borderLeft: isActive ? '3px solid #0ea5e9' : isSelected ? '2px solid #0ea5e9' : '1px dashed #d1d5db',
        borderRight: isActive ? '3px solid #0ea5e9' : isSelected ? '2px solid #0ea5e9' : '1px dashed #d1d5db',
        cursor: 'pointer',
        transition: 'all 0.15s ease-in-out',
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        flexShrink: 0,
      }}
    >
      {isHard && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            color: '#ef4444',
            fontSize: '24px',
            fontWeight: 'bold',
            pointerEvents: 'none',
          }}
        >
          !
        </div>
      )}
      {isActive && (
        <div
          style={{
            color: '#0ea5e9',
            fontSize: '32px',
            fontWeight: 'bold',
            pointerEvents: 'none',
          }}
        >
          +
        </div>
      )}
      {showTooltip && gapInfo && plane === 0 && (
        <div
          style={{
            position: 'absolute',
            bottom: '100%',
            left: '50%',
            transform: 'translateX(-50%)',
            background: 'rgba(17, 24, 39, 0.95)',
            color: 'white',
            padding: '8px 12px',
            borderRadius: '6px',
            fontSize: '11px',
            whiteSpace: 'nowrap',
            zIndex: 1000,
            marginBottom: '4px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
            pointerEvents: 'none',
          }}
        >
          <div style={{ fontWeight: 'bold', marginBottom: '4px', color: '#60a5fa' }}>
            Gap {position}
          </div>
          <div style={{ marginBottom: '2px' }}>
            <span style={{ color: '#9ca3af' }}>From:</span> {formatPValue(gapInfo.fromPValue)}
          </div>
          <div style={{ marginBottom: '2px' }}>
            <span style={{ color: '#9ca3af' }}>To:</span> {formatPValue(gapInfo.toPValue)}
          </div>
          <div style={{ marginTop: '4px', paddingTop: '4px', borderTop: '1px solid rgba(156, 163, 175, 0.3)' }}>
            <span style={{ color: '#9ca3af' }}>Distance:</span>{' '}
            <span style={{ color: gapInfo.isHard ? '#ef4444' : '#10b981', fontWeight: 'bold' }}>
              {gapInfo.distance.toFixed(3)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

interface ActivityBlockProps {
  activity: InstantiatedActivity;
  position: number;
  pixelsPerMinute: number;
  onRemove: (position: number) => void;
  onHover?: (activity: InstantiatedActivity | null) => void;
}

const ActivityBlock: React.FC<ActivityBlockProps> = ({ activity, position, pixelsPerMinute, onRemove, onHover }) => {
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseEnter = () => {
    setIsHovered(true);
    if (onHover) onHover(activity);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    if (onHover) onHover(null);
  };

  const width = activity.time * pixelsPerMinute; // Exact width based on time
  const planeColor = getPlaneColor(activity.plane);

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm(`Remove ${activity.activityName}?`)) {
      onRemove(position);
    }
  };

  // Drag for reordering (optional - can be added later)
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'TIMELINE_ACTIVITY',
    item: { position },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }));

  return (
    <div
      ref={drag as any}
      className="activity-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      style={{
        width: `${width}px`,
        minWidth: `${width}px`,
        maxWidth: `${width}px`,
        background: planeColor,
        color: 'white',
        padding: '8px 12px',
        borderRadius: '6px',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        cursor: isDragging ? 'grabbing' : 'grab',
        boxShadow: isHovered ? '0 4px 12px rgba(0,0,0,0.2)' : '0 2px 4px rgba(0,0,0,0.1)',
        transform: isHovered ? 'translateY(-2px)' : 'translateY(0)',
        transition: 'all 0.2s ease-in-out',
        opacity: isDragging ? 0.5 : 1,
        border: '1px solid rgba(255, 255, 255, 0.2)',
        flexShrink: 0,
      }}
    >
      <div style={{
        fontSize: '12px',
        fontWeight: 'bold',
        marginBottom: '2px',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        paddingRight: '20px',
      }}>
        {getActivityAbbreviation(activity.activityName)}
      </div>
      <div style={{ fontSize: '10px', opacity: 0.9 }}>
        {formatTime(activity.time)}
      </div>

      {/* Remove button - always visible on hover */}
      {isHovered && (
        <button
          onClick={handleRemove}
          style={{
            position: 'absolute',
            top: '4px',
            right: '4px',
            background: 'rgba(0, 0, 0, 0.3)',
            border: 'none',
            borderRadius: '50%',
            width: '20px',
            height: '20px',
            fontSize: '14px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 'bold',
            transition: 'all 0.15s',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(239, 68, 68, 0.9)';
            e.currentTarget.style.transform = 'scale(1.1)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'rgba(0, 0, 0, 0.3)';
            e.currentTarget.style.transform = 'scale(1)';
          }}
        >
          ×
        </button>
      )}
    </div>
  );
};

interface TimelineLaneProps {
  planeName: string;
  planeIdx: number;
  planeActivities: { act: InstantiatedActivity; idx: number }[];
  allActivities: InstantiatedActivity[];
  hardGapsList: number[];
  gapPValueInfo: GapPValueInfo[];
  pixelsPerMinute: number;
  tBudget: number;
  minTimelineWidth: number;
  onRemove: (position: number) => void;
  onChangePlane: (position: number, plane: number) => Promise<void>;
  onDrop: (actIdx: number, position: number, plane: number) => void;
  onHover?: (activity: InstantiatedActivity | null) => void;
}

const TimelineLane: React.FC<TimelineLaneProps> = ({
  planeName,
  planeIdx,
  planeActivities,
  allActivities,
  hardGapsList,
  gapPValueInfo,
  pixelsPerMinute,
  tBudget,
  minTimelineWidth,
  onRemove,
  onChangePlane,
  onDrop,
  onHover,
}) => {
  // Create drop zone for entire lane to accept activity drags
  const [{ isOver, canDrop }, laneDrop] = useDrop(() => ({
    accept: 'TIMELINE_ACTIVITY',
    drop: async (item: { position: number }) => {
      // Change the plane of the dragged activity
      try {
        await onChangePlane(item.position, planeIdx);
      } catch (error) {
        console.error('Failed to change plane:', error);
      }
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
      canDrop: monitor.canDrop(),
    }),
  }));

  const isLaneActive = isOver && canDrop;

  return (
    <div
      ref={laneDrop as any}
      style={{
        height: '80px',
        borderBottom: planeIdx < 2 ? '1px solid #e5e7eb' : 'none',
        display: 'flex',
        alignItems: 'center',
        padding: '8px 0',
        position: 'relative',
        background: isLaneActive ? '#e0f2fe' : (planeIdx % 2 === 0 ? '#ffffff' : '#fafafa'),
        overflow: 'visible',
        minWidth: `${Math.max(tBudget * pixelsPerMinute, minTimelineWidth)}px`,
        transition: 'background 0.2s ease',
      }}
    >
      {/* Time grid lines */}
      {Array.from({ length: Math.ceil(tBudget / 10) + 1 }, (_, i) => i * 10).map(minute => (
        <div
          key={`grid-${minute}`}
          style={{
            position: 'absolute',
            left: `${minute * pixelsPerMinute}px`,
            top: 0,
            bottom: 0,
            width: '1px',
            background: minute === 0 ? '#94a3b8' : '#e2e8f0',
            pointerEvents: 'none',
          }}
        />
      ))}
      {/* Render activities - use backend's startsAfter (already sequential!) */}
      {planeActivities.map(({ act, idx }) => {
        const leftPosition = act.startsAfter * pixelsPerMinute;
        const width = act.time * pixelsPerMinute;

        return (
          <div
            key={idx}
            style={{
              position: 'absolute',
              left: `${leftPosition}px`,
              width: `${width}px`,
            }}
          >
            <ActivityBlock
              activity={act}
              position={idx}
              pixelsPerMinute={pixelsPerMinute}
              onRemove={onRemove}
              onHover={onHover}
            />
          </div>
        );
      })}

      {/* Drop zones: Show ALL global drop zones in each plane */}
      {/* Drop zone at position 0 (before first activity) */}
      <div style={{
        position: 'absolute',
        left: '0px',
        height: '100%',
        zIndex: 1,
      }}>
        <DropZone
          position={0}
          isHard={hardGapsList.includes(0)}
          plane={planeIdx}
          gapInfo={gapPValueInfo.find(g => g.position === 0)}
          onDrop={onDrop}
        />
      </div>

      {/* Drop zones after each activity (globally) */}
      {allActivities.map((act, idx) => {
        const dropZonePosition = act.endsAfter * pixelsPerMinute;

        return (
          <div
            key={`drop-${idx}`}
            style={{
              position: 'absolute',
              left: `${dropZonePosition}px`,
              height: '100%',
              zIndex: 1,
            }}
          >
            <DropZone
              position={idx + 1}
              isHard={hardGapsList.includes(idx + 1)}
              plane={planeIdx}
              gapInfo={gapPValueInfo.find(g => g.position === idx + 1)}
              onDrop={onDrop}
            />
          </div>
        );
      })}

      {/* Empty lane indicator */}
      {planeActivities.length === 0 && allActivities.length > 0 && (
        <div style={{
          flex: 1,
          textAlign: 'center',
          color: '#d1d5db',
          fontSize: '12px',
          fontStyle: 'italic',
          padding: '0 20px',
        }}>
          No activities in {planeName} yet
        </div>
      )}
    </div>
  );
};

interface OrchestrationTimelineProps {
  onActivityHover?: (activity: InstantiatedActivity | null) => void;
}

const OrchestrationTimeline: React.FC<OrchestrationTimelineProps> = ({ onActivityHover }) => {
  const { graphState, insertActivity, removeActivity, changePlane, selectedGap } = useOrchestrationStore();

  const handleActivityHover = (activity: InstantiatedActivity | null) => {
    if (onActivityHover) onActivityHover(activity);
  };

  // Debug: Log activities to check for overlaps
  React.useEffect(() => {
    if (graphState) {
    }
  }, [graphState]);

  if (!graphState) {
    return (
      <div className="timeline-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <div style={{ textAlign: 'center', color: '#9ca3af' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
          <div>Loading graph state...</div>
        </div>
      </div>
    );
  };

  const pixelsPerMinute = 6;
  const minTimelineWidth = 1200;

  const handleDrop = async (actIdx: number, position: number, plane: number) => {
    try {
      await insertActivity(actIdx, position, plane);
    } catch (error) {
      console.error('Failed to insert activity:', error);
      alert('Failed to add activity. Check console for details.');
    }
  };

  const handleRemove = async (position: number) => {
    try {
      await removeActivity(position);
    } catch (error) {
      console.error('Failed to remove activity:', error);
      alert('Failed to remove activity. Check console for details.');
    }
  };

  const planeNames = ['Indiv.', 'Team', 'Class'];
  const isEmpty = graphState.activities.length === 0;

  const selectedGapInfo = selectedGap !== null ? graphState.gapPValueInfo.find(g => g.position === selectedGap) : null;

  return (
    <div className="timeline-container">
      {/* Header with stats */}
      <div style={{
        padding: '20px 24px',
        borderBottom: '1px solid #e5e7eb',
        background: 'linear-gradient(to bottom, #ffffff, #f9fafb)',
      }}>
        <h2 style={{ margin: '0 0 12px 0', fontSize: '20px', color: '#111827' }}>
          Orchestration Timeline
        </h2>
        <div style={{ display: 'flex', gap: '24px', fontSize: '14px', marginBottom: selectedGapInfo ? '16px' : '0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ color: '#6b7280' }}>Time:</span>
            <span style={{
              fontWeight: 'bold',
              color: graphState.totTime > graphState.tBudget ? '#ef4444' : '#10b981',
              fontSize: '16px',
            }}>
              {graphState.totTime}
            </span>
            <span style={{ color: '#9ca3af' }}>/</span>
            <span style={{ color: '#6b7280' }}>{graphState.tBudget} min</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ color: '#6b7280' }}>Hard gaps:</span>
            <span style={{
              fontWeight: 'bold',
              color: graphState.hardGapsCount > 0 ? '#ef4444' : '#10b981',
              fontSize: '16px',
            }}>
              {graphState.hardGapsCount}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ color: '#6b7280' }}>Current:</span>
            <span style={{
              fontWeight: 'bold',
              color: '#3b82f6',
              fontSize: '14px',
              fontFamily: 'monospace',
            }}>
              {formatPValue(graphState.reached)}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ color: '#6b7280' }}>Goal:</span>
            <span style={{
              fontWeight: 'bold',
              color: graphState.goalReached ? '#10b981' : '#f59e0b',
              fontSize: '16px',
            }}>
              {graphState.goalReached ? ' Reached' : ' Not Yet'}
            </span>
            <span style={{
              fontSize: '14px',
              fontFamily: 'monospace',
              color: '#6b7280',
              marginLeft: '4px'
            }}>
              {formatPValue(graphState.goal)}
            </span>
          </div>
        </div>

        {/* Selected Gap P-Value Information Panel */}
        {selectedGapInfo && (
          <div style={{
            marginTop: '12px',
            padding: '12px 16px',
            background: selectedGapInfo.isHard ? '#fef2f2' : '#f0f9ff',
            border: selectedGapInfo.isHard ? '2px solid #fca5a5' : '2px solid #93c5fd',
            borderRadius: '8px',
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '8px'
            }}>
              <div style={{
                fontSize: '14px',
                fontWeight: 'bold',
                color: selectedGapInfo.isHard ? '#dc2626' : '#0ea5e9'
              }}>
                Selected Gap {selectedGap} {selectedGapInfo.isHard ? '(Hard Gap)' : ''}
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>
                Distance: <span style={{
                  fontWeight: 'bold',
                  color: selectedGapInfo.isHard ? '#dc2626' : '#059669'
                }}>
                  {selectedGapInfo.distance.toFixed(3)}
                </span>
              </div>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '12px',
              fontSize: '12px'
            }}>
              <div style={{
                padding: '8px',
                background: 'white',
                borderRadius: '4px',
                border: '1px solid #e5e7eb'
              }}>
                <div style={{ color: '#6b7280', marginBottom: '4px', fontWeight: '500' }}>
                  Current State (From)
                </div>
                <div style={{
                  fontFamily: 'monospace',
                  fontSize: '13px',
                  color: '#111827',
                  fontWeight: 'bold'
                }}>
                  {formatPValue(selectedGapInfo.fromPValue)}
                </div>
                <div style={{ fontSize: '11px', color: '#9ca3af', marginTop: '2px' }}>
                  Fluency: {selectedGapInfo.fromPValue.v[0].toFixed(2)} |
                  Depth: {selectedGapInfo.fromPValue.v[1].toFixed(2)}
                </div>
              </div>

              <div style={{
                padding: '8px',
                background: 'white',
                borderRadius: '4px',
                border: '1px solid #e5e7eb'
              }}>
                <div style={{ color: '#6b7280', marginBottom: '4px', fontWeight: '500' }}>
                  Target State (To)
                </div>
                <div style={{
                  fontFamily: 'monospace',
                  fontSize: '13px',
                  color: '#111827',
                  fontWeight: 'bold'
                }}>
                  {formatPValue(selectedGapInfo.toPValue)}
                </div>
                <div style={{ fontSize: '11px', color: '#9ca3af', marginTop: '2px' }}>
                  Fluency: {selectedGapInfo.toPValue.v[0].toFixed(2)} |
                  Depth: {selectedGapInfo.toPValue.v[1].toFixed(2)}
                </div>
              </div>
            </div>

            <div style={{
              marginTop: '8px',
              fontSize: '11px',
              color: '#6b7280',
              fontStyle: 'italic',
              textAlign: 'center'
            }}>
              Hover over gap zones in the timeline to see all gap information
            </div>
          </div>
        )}
      </div>

      {/* Timeline area */}
      <div style={{
        padding: '24px',
        overflowX: 'auto',
        overflowY: 'hidden',
        height: 'calc(100% - 100px)',
      }}>
        <div style={{
          position: 'relative',
          minWidth: `${minTimelineWidth}px`,
          height: '100%',
        }}>
          {/* Plane labels column */}
          <div style={{
            position: 'absolute',
            left: '0',
            top: '0',
            width: '80px',
            height: '100%',
            background: '#f9fafb',
            borderRight: '2px solid #e5e7eb',
            zIndex: 10,
          }}>
            {planeNames.map((name, idx) => (
              <div
                key={idx}
                style={{
                  height: '80px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#374151',
                  borderBottom: idx < planeNames.length - 1 ? '1px solid #e5e7eb' : 'none',
                }}
              >
                {name}
              </div>
            ))}
          </div>

          {/* Timeline lanes */}
          <div style={{
            marginLeft: '80px',
            paddingLeft: '16px',
            height: '100%',
          }}>
            {isEmpty ? (
              // Empty state - show lanes with instructions
              <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                <div style={{
                  textAlign: 'center',
                  padding: '16px',
                  background: '#f0f9ff',
                  borderBottom: '2px solid #bfdbfe',
                  marginBottom: '8px',
                }}>
                  <div style={{ fontSize: '16px', fontWeight: '600', color: '#1e40af' }}>
                    Drag activities from the library to start building your lesson
                  </div>
                </div>
                {planeNames.map((planeName, planeIdx) => (
                  <div
                    key={planeIdx}
                    style={{
                      height: '80px',
                      borderBottom: planeIdx < planeNames.length - 1 ? '1px solid #e5e7eb' : 'none',
                      display: 'flex',
                      alignItems: 'center',
                      padding: '8px 0',
                      background: planeIdx % 2 === 0 ? '#ffffff' : '#fafafa',
                    }}
                  >
                    <DropZone
                      position={0}
                      isHard={graphState.hardGapsList.includes(0)}
                      plane={planeIdx}
                      gapInfo={graphState.gapPValueInfo.find(g => g.position === 0)}
                      onDrop={handleDrop}
                    />
                  </div>
                ))}
              </div>
            ) : (
              <>
                {/* Time ruler at the top */}
                <div style={{
                  height: '30px',
                  borderBottom: '2px solid #cbd5e1',
                  position: 'relative',
                  background: '#f8fafc',
                  minWidth: `${Math.max(graphState.tBudget * pixelsPerMinute, minTimelineWidth)}px`,
                }}>
                  {Array.from({ length: Math.ceil(graphState.tBudget / 10) + 1 }, (_, i) => i * 10).map(minute => (
                    <div
                      key={minute}
                      style={{
                        position: 'absolute',
                        left: `${minute * pixelsPerMinute}px`,
                        top: 0,
                        height: '100%',
                        display: 'flex',
                        alignItems: 'center',
                      }}
                    >
                      <div style={{
                        fontSize: '11px',
                        color: '#64748b',
                        fontWeight: '500',
                        background: '#f8fafc',
                        padding: '0 4px',
                      }}>
                        {minute}'
                      </div>
                    </div>
                  ))}
                </div>

                {/* Timeline with activities - X-axis = TIME, activities positioned by startsAfter */}
                {planeNames.map((planeName, planeIdx) => {
                  // Get activities for this plane ONLY
                  const planeActivities = graphState.activities
                    .map((act, idx) => ({ act, idx }))
                    .filter(({ act }) => act.plane === planeIdx);

                  return (
                    <TimelineLane
                      key={planeIdx}
                      planeName={planeName}
                      planeIdx={planeIdx}
                      planeActivities={planeActivities}
                      allActivities={graphState.activities}
                      hardGapsList={graphState.hardGapsList}
                      gapPValueInfo={graphState.gapPValueInfo}
                      pixelsPerMinute={pixelsPerMinute}
                      tBudget={graphState.tBudget}
                      minTimelineWidth={minTimelineWidth}
                      onRemove={handleRemove}
                      onChangePlane={changePlane}
                      onDrop={handleDrop}
                      onHover={handleActivityHover}
                    />
                  );
                })}

              </>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default OrchestrationTimeline;
