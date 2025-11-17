/**
 * Teacher Context Modal
 * Collects age group and subject information before generating enhanced view
 */

import React, { useState } from 'react';
import { useOrchestrationStore } from '../../store/orchestrationStore';
import { useTeacherContextStore } from '../../store/teacherContextStore';
import './TeacherContextModal.css';

interface TeacherContextModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const TeacherContextModal: React.FC<TeacherContextModalProps> = ({ isOpen, onClose }) => {
  const [ageGroup, setAgeGroup] = useState('');
  const [subject, setSubject] = useState('');
  const graphState = useOrchestrationStore(state => state.graphState);
  const { generateEnhancement, isLoading, error } = useTeacherContextStore();

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!ageGroup.trim() || !subject.trim()) {
      return;
    }

    if (!graphState) {
      alert('No orchestration available to enhance');
      return;
    }

    try {
      await generateEnhancement(graphState, {
        ageGroup: ageGroup.trim(),
        subject: subject.trim(),
      });
      // Modal will close automatically on success via store
    } catch (err) {
      // Error is handled in the store and displayed below
      console.error('Failed to generate enhancement:', err);
    }
  };

  const handleCancel = () => {
    setAgeGroup('');
    setSubject('');
    onClose();
  };

  const hasActivities = graphState && graphState.activities.length > 0;

  return (
    <div className="modal-overlay" onClick={handleCancel}>
      <div className="modal-content teacher-context-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Generate Teaching Plan</h2>
          <button className="close-button" onClick={handleCancel}>×</button>
        </div>

        {!hasActivities && (
          <div className="warning-message">
            <strong>Note:</strong> Your orchestration is empty. Add some activities to the timeline before generating a teaching plan.
          </div>
        )}

        <form onSubmit={handleSubmit} className="teacher-context-form">
          {error && (
            <div className="error-message">{error}</div>
          )}

          <div className="form-section">
            <h3>Tell us about your class</h3>
            <p className="form-description">
              This information will be used to generate age-appropriate resources and teaching suggestions.
            </p>

            <div className="form-group">
              <label htmlFor="ageGroup">Age Group / Grade Level *</label>
              <input
                id="ageGroup"
                type="text"
                value={ageGroup}
                onChange={(e) => setAgeGroup(e.target.value)}
                placeholder="e.g., '12-13 years old', 'high school seniors', 'university undergraduates'"
                required
                disabled={isLoading}
              />
              <div className="field-hint">
                Be specific to get the most relevant suggestions
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="subject">Subject / Topic *</label>
              <input
                id="subject"
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="e.g., 'Photosynthesis', 'Quadratic Equations', 'French Revolution'"
                required
                disabled={isLoading}
              />
              <div className="field-hint">
                The more specific, the better the recommendations
              </div>
            </div>
          </div>

          <div className="info-box">
            <div className="info-icon">ℹ️</div>
            <div className="info-content">
              <strong>What you'll get:</strong>
              <ul>
                <li>Concrete examples for each activity tailored to your subject</li>
                <li>Curated teaching resources (videos, worksheets, tools)</li>
                <li>Age-appropriate adaptations and teaching tips</li>
                <li>Time management suggestions</li>
              </ul>
            </div>
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={handleCancel}
              disabled={isLoading}
              className="secondary-button"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !hasActivities}
              className="primary-button"
            >
              {isLoading ? (
                <>
                  <span className="spinner"></span>
                  Generating...
                </>
              ) : (
                'Generate Teaching Plan'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TeacherContextModal;
