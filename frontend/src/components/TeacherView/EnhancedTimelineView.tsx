/**
 * Enhanced Timeline View
 * Displays orchestration timeline with LLM-generated teaching resources
 */

import React, { useState } from 'react';
import { useOrchestrationStore } from '../../store/orchestrationStore';
import { useTeacherContextStore } from '../../store/teacherContextStore';
import { formatTime, formatPValue, getPlaneName } from '../../types/domain';
import './EnhancedTimelineView.css';

interface EnhancedTimelineViewProps {
  onBackToLanding?: () => void;
}

const EnhancedTimelineView: React.FC<EnhancedTimelineViewProps> = ({ onBackToLanding }) => {
  const graphState = useOrchestrationStore(state => state.graphState);
  const {
    teacherContext,
    enhancementData,
    enhancementMetadata,
    clearEnhancement,
    regenerateEnhancement,
    isLoading,
  } = useTeacherContextStore();

  const [expandedActivities, setExpandedActivities] = useState<Set<number>>(new Set([0])); // First activity expanded by default

  if (!graphState || !enhancementData || !teacherContext) {
    return null;
  }

  const toggleActivity = (position: number) => {
    setExpandedActivities(prev => {
      const next = new Set(prev);
      if (next.has(position)) {
        next.delete(position);
      } else {
        next.add(position);
      }
      return next;
    });
  };

  const expandAll = () => {
    const all = new Set(graphState.activities.map((_, idx) => idx));
    setExpandedActivities(all);
  };

  const collapseAll = () => {
    setExpandedActivities(new Set());
  };

  const handleRegenerate = async () => {
    try {
      await regenerateEnhancement(graphState);
    } catch (err) {
      alert('Failed to regenerate enhancement. Check console for details.');
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return '#10b981';
      case 'moderate': return '#f59e0b';
      case 'challenging': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getResourceIcon = (type: string) => {
    switch (type) {
      case 'video': return '🎥';
      case 'worksheet': return '📝';
      case 'tool': return '🔧';
      case 'simulation': return '🧪';
      case 'article': return '📄';
      case 'reference': return '📚';
      case 'community': return '👥';
      default: return '📌';
    }
  };

  return (
    <div className="enhanced-timeline-view">
      {/* Header */}
      <div className="enhanced-header">
        <div className="enhanced-title-section">
          <h2>Teaching Plan</h2>
          <div className="context-badges">
            <span className="context-badge age">{teacherContext.ageGroup}</span>
            <span className="context-badge subject">{teacherContext.subject}</span>
          </div>
        </div>

        <div className="header-actions">
          <button onClick={handleRegenerate} disabled={isLoading} className="regenerate-button">
            {isLoading ? 'Regenerating...' : 'Regenerate'}
          </button>
          {onBackToLanding && (
            <button onClick={onBackToLanding} className="back-button">
              ← Start Over
            </button>
          )}
          <button onClick={clearEnhancement} className="back-button">
            ← Back to Timeline
          </button>
        </div>
      </div>

      {/* Overall Stats */}
      <div className="stats-bar">
        <div className="stat-item">
          <span className="stat-label">Total Time:</span>
          <span className="stat-value">{formatTime(graphState.totTime)}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Activities:</span>
          <span className="stat-value">{graphState.activities.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Goal:</span>
          <span className="stat-value">{formatPValue(graphState.goal)}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Difficulty:</span>
          <span
            className="stat-value"
            style={{ color: getDifficultyColor(enhancementData.overallSuggestions.estimatedDifficulty) }}
          >
            {enhancementData.overallSuggestions.estimatedDifficulty}
          </span>
        </div>
      </div>

      {/* Overall Suggestions */}
      <div className="overall-suggestions">
        <h3>Overall Suggestions</h3>

        <div className="suggestion-grid">
          <div className="suggestion-card">
            <div className="suggestion-header">
              <span className="suggestion-icon">👥</span>
              <h4>Age Adaptations</h4>
            </div>
            <p>{enhancementData.overallSuggestions.ageAdaptations}</p>
          </div>

          <div className="suggestion-card">
            <div className="suggestion-header">
              <span className="suggestion-icon">📚</span>
              <h4>Subject Context</h4>
            </div>
            <p>{enhancementData.overallSuggestions.subjectContext}</p>
          </div>
        </div>
      </div>

      {/* Activity Enhancements */}
      <div className="activities-section">
        <div className="activities-header">
          <h3>Activity-Specific Resources</h3>
          <div className="expand-controls">
            <button onClick={expandAll} className="expand-control-btn">Expand All</button>
            <button onClick={collapseAll} className="expand-control-btn">Collapse All</button>
          </div>
        </div>

        <div className="activities-list">
          {graphState.activities.map((activity, idx) => {
            const enhancement = enhancementData.activityEnhancements.find(
              e => e.activityPosition === idx
            );

            if (!enhancement) return null;

            const isExpanded = expandedActivities.has(idx);

            return (
              <div key={idx} className={`activity-enhancement ${isExpanded ? 'expanded' : ''}`}>
                <div className="activity-enhancement-header" onClick={() => toggleActivity(idx)}>
                  <div className="activity-info">
                    <span className="activity-number">{idx + 1}</span>
                    <div className="activity-details">
                      <h4>{activity.activityName}</h4>
                      <div className="activity-meta">
                        {formatTime(activity.time)} • {getPlaneName(activity.plane)}
                      </div>
                    </div>
                  </div>
                  <button className="expand-toggle">
                    {isExpanded ? '▼' : '▶'}
                  </button>
                </div>

                {isExpanded && (
                  <div className="activity-enhancement-content">
                    {/* Concrete Example */}
                    <div className="enhancement-section">
                      <h5>Concrete Example</h5>
                      <p className="example-text">{enhancement.concreteExample}</p>
                    </div>

                    {/* Teaching Tips */}
                    <div className="enhancement-section">
                      <h5>Teaching Tips</h5>
                      <p>{enhancement.teachingTips}</p>
                    </div>

                    {/* Time Management */}
                    {enhancement.timeManagement && (
                      <div className="enhancement-section">
                        <h5>Time Management</h5>
                        <p>{enhancement.timeManagement}</p>
                      </div>
                    )}

                    {/* Resources */}
                    {enhancement.resources.length > 0 && (
                      <div className="enhancement-section">
                        <h5>Resources</h5>
                        <div className="resources-list">
                          {enhancement.resources.map((resource, resIdx) => (
                            <div key={resIdx} className="resource-item">
                              <span className="resource-icon">{getResourceIcon(resource.type)}</span>
                              <div className="resource-info">
                                <div className="resource-title">{resource.title}</div>
                                {resource.description && (
                                  <div className="resource-description">{resource.description}</div>
                                )}
                                {resource.suggestedUrl && (
                                  <div className="resource-url">
                                    {resource.suggestedUrl.startsWith('http') ? (
                                      <a href={resource.suggestedUrl} target="_blank" rel="noopener noreferrer">
                                        Open resource →
                                      </a>
                                    ) : (
                                      <span className="search-hint">Search: {resource.suggestedUrl}</span>
                                    )}
                                  </div>
                                )}
                              </div>
                              <span className="resource-type">{resource.type}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Additional Resources */}
      {enhancementData.additionalResources.length > 0 && (
        <div className="additional-resources">
          <h3>Additional Resources</h3>
          <div className="resources-grid">
            {enhancementData.additionalResources.map((resource, idx) => (
              <div key={idx} className="resource-card">
                <span className="resource-card-icon">{getResourceIcon(resource.type)}</span>
                <div className="resource-card-content">
                  <h4>{resource.title}</h4>
                  {resource.description && <p>{resource.description}</p>}
                  {resource.suggestedUrl && (
                    <div className="resource-card-link">
                      {resource.suggestedUrl.startsWith('http') ? (
                        <a href={resource.suggestedUrl} target="_blank" rel="noopener noreferrer">
                          Visit →
                        </a>
                      ) : (
                        <span className="search-hint">Search: {resource.suggestedUrl}</span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer with metadata */}
      {enhancementMetadata && (
        <div className="enhancement-footer">
          <div className="metadata-info">
            Generated by {enhancementMetadata.model}
            {enhancementMetadata.inputTokens && enhancementMetadata.outputTokens && (
              <span className="token-info">
                {' '}• {enhancementMetadata.inputTokens + enhancementMetadata.outputTokens} tokens
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedTimelineView;
