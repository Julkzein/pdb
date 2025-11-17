/**
 * Activity Editor Modal
 * Simple form for creating new activities
 */

import React, { useState } from 'react';
import './ActivityEditor.css';

interface ActivityEditorProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (activityData: NewActivityData) => Promise<void>;
}

export interface NewActivityData {
  name: string;
  description: string;
  pcond: [number, number];
  canChangeTime: boolean;
  minT?: number;
  maxT?: number;
  defT: number;
  minEffect?: [number, number];
  maxEffect: [number, number];
  maxRepetition: number;
  defPlane: number;
  explanation?: string;
  sources?: string;
}

const ActivityEditor: React.FC<ActivityEditorProps> = ({ isOpen, onClose, onSave }) => {
  const [formData, setFormData] = useState<NewActivityData>({
    name: '',
    description: '',
    pcond: [0, 0],
    canChangeTime: false,
    defT: 15,
    maxEffect: [0.1, 0.1],
    maxRepetition: 2,
    defPlane: 0,
  });

  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!formData.name.trim()) {
      setError('Activity name is required');
      return;
    }

    if (!formData.description.trim()) {
      setError('Description is required');
      return;
    }

    if (formData.canChangeTime && formData.minT && formData.maxT && formData.defT) {
      if (formData.minT > formData.defT || formData.defT > formData.maxT) {
        setError('Time must satisfy: minT ≤ defT ≤ maxT');
        return;
      }
    }

    setIsSaving(true);
    try {
      // Prepare data for backend
      const dataToSave: NewActivityData = {
        ...formData,
        name: formData.name.trim(),
        description: formData.description.trim(),
      };

      if (formData.canChangeTime) {
        dataToSave.minT = formData.minT || formData.defT;
        dataToSave.maxT = formData.maxT || formData.defT;
        dataToSave.minEffect = formData.minEffect || formData.maxEffect;
      }

      await onSave(dataToSave);

      // Reset form and close
      setFormData({
        name: '',
        description: '',
        pcond: [0, 0],
        canChangeTime: false,
        defT: 15,
        maxEffect: [0.1, 0.1],
        maxRepetition: 2,
        defPlane: 0,
      });
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save activity');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Activity</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="activity-form">
          {error && (
            <div className="error-message">{error}</div>
          )}

          {/* Basic Info */}
          <div className="form-section">
            <h3>Basic Information</h3>

            <div className="form-group">
              <label>Name *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                placeholder="e.g., PracticeSynthesis"
                required
              />
            </div>

            <div className="form-group">
              <label>Description *</label>
              <textarea
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                placeholder="Brief description of the activity's educational purpose"
                rows={3}
                required
              />
            </div>

            <div className="form-group">
              <label>Explanation (optional)</label>
              <textarea
                value={formData.explanation || ''}
                onChange={(e) => handleChange('explanation', e.target.value)}
                placeholder="Explain why one would use this activity (pedagogical rationale)"
                rows={3}
              />
            </div>

            <div className="form-group">
              <label>Sources (optional)</label>
              <textarea
                value={formData.sources || ''}
                onChange={(e) => handleChange('sources', e.target.value)}
                placeholder="Academic sources backing this activity (citations)"
                rows={2}
              />
            </div>
          </div>

          {/* Prerequisites */}
          <div className="form-section">
            <h3>Prerequisites (p-condition)</h3>
            <div className="inline-group">
              <div className="form-group">
                <label>Fluency</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="1"
                  value={formData.pcond[0]}
                  onChange={(e) => handleChange('pcond', [parseFloat(e.target.value), formData.pcond[1]])}
                />
              </div>
              <div className="form-group">
                <label>Depth</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="1"
                  value={formData.pcond[1]}
                  onChange={(e) => handleChange('pcond', [formData.pcond[0], parseFloat(e.target.value)])}
                />
              </div>
            </div>
          </div>

          {/* Effects */}
          <div className="form-section">
            <h3>Effect (Learning Gain)</h3>

            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={formData.canChangeTime}
                  onChange={(e) => handleChange('canChangeTime', e.target.checked)}
                />
                Flexible Time (allows duration range)
              </label>
            </div>

            <div className="inline-group">
              <div className="form-group">
                <label>Max Effect Fluency *</label>
                <input
                  type="number"
                  step="0.05"
                  min="0"
                  max="1"
                  value={formData.maxEffect[0]}
                  onChange={(e) => handleChange('maxEffect', [parseFloat(e.target.value), formData.maxEffect[1]])}
                  required
                />
              </div>
              <div className="form-group">
                <label>Max Effect Depth *</label>
                <input
                  type="number"
                  step="0.05"
                  min="0"
                  max="1"
                  value={formData.maxEffect[1]}
                  onChange={(e) => handleChange('maxEffect', [formData.maxEffect[0], parseFloat(e.target.value)])}
                  required
                />
              </div>
            </div>

            {formData.canChangeTime && (
              <div className="inline-group">
                <div className="form-group">
                  <label>Min Effect Fluency</label>
                  <input
                    type="number"
                    step="0.05"
                    min="0"
                    max="1"
                    value={formData.minEffect?.[0] || 0}
                    onChange={(e) => handleChange('minEffect', [parseFloat(e.target.value), formData.minEffect?.[1] || 0])}
                  />
                </div>
                <div className="form-group">
                  <label>Min Effect Depth</label>
                  <input
                    type="number"
                    step="0.05"
                    min="0"
                    max="1"
                    value={formData.minEffect?.[1] || 0}
                    onChange={(e) => handleChange('minEffect', [formData.minEffect?.[0] || 0, parseFloat(e.target.value)])}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Time Configuration */}
          <div className="form-section">
            <h3>Time Configuration</h3>

            {formData.canChangeTime ? (
              <div className="inline-group">
                <div className="form-group">
                  <label>Min Time (min)</label>
                  <input
                    type="number"
                    min="1"
                    value={formData.minT || formData.defT}
                    onChange={(e) => handleChange('minT', parseInt(e.target.value))}
                  />
                </div>
                <div className="form-group">
                  <label>Default Time (min) *</label>
                  <input
                    type="number"
                    min="1"
                    value={formData.defT}
                    onChange={(e) => handleChange('defT', parseInt(e.target.value))}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Max Time (min)</label>
                  <input
                    type="number"
                    min="1"
                    value={formData.maxT || formData.defT}
                    onChange={(e) => handleChange('maxT', parseInt(e.target.value))}
                  />
                </div>
              </div>
            ) : (
              <div className="form-group">
                <label>Duration (min) *</label>
                <input
                  type="number"
                  min="1"
                  value={formData.defT}
                  onChange={(e) => handleChange('defT', parseInt(e.target.value))}
                  required
                />
              </div>
            )}
          </div>

          {/* Other Settings */}
          <div className="form-section">
            <h3>Other Settings</h3>

            <div className="form-group">
              <label>Max Repetitions *</label>
              <input
                type="number"
                min="1"
                value={formData.maxRepetition}
                onChange={(e) => handleChange('maxRepetition', parseInt(e.target.value))}
                required
              />
            </div>

            <div className="form-group">
              <label>Default Plane *</label>
              <div className="radio-group">
                <label>
                  <input
                    type="radio"
                    name="defPlane"
                    value="0"
                    checked={formData.defPlane === 0}
                    onChange={() => handleChange('defPlane', 0)}
                  />
                  Individual
                </label>
                <label>
                  <input
                    type="radio"
                    name="defPlane"
                    value="1"
                    checked={formData.defPlane === 1}
                    onChange={() => handleChange('defPlane', 1)}
                  />
                  Team
                </label>
                <label>
                  <input
                    type="radio"
                    name="defPlane"
                    value="2"
                    checked={formData.defPlane === 2}
                    onChange={() => handleChange('defPlane', 2)}
                  />
                  Class
                </label>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="form-actions">
            <button type="button" onClick={onClose} disabled={isSaving}>
              Cancel
            </button>
            <button type="submit" disabled={isSaving} className="primary-button">
              {isSaving ? 'Saving...' : 'Create Activity'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ActivityEditor;
