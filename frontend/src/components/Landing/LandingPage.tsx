/**
 * Landing Page Component
 * First screen users see with option to auto-generate or use custom mode
 */

import React, { useState } from 'react';
import './LandingPage.css';

interface LandingPageProps {
  onGenerate: (ageGroup: string, subject: string) => void;
  onCustom: () => void;
  isLoading?: boolean;
  loadingMessage?: string;
}

const LandingPage: React.FC<LandingPageProps> = ({
  onGenerate,
  onCustom,
  isLoading = false,
  loadingMessage = 'Loading...'
}) => {
  const [ageGroup, setAgeGroup] = useState('');
  const [subject, setSubject] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!ageGroup.trim() || !subject.trim()) {
      return;
    }

    onGenerate(ageGroup.trim(), subject.trim());
  };

  const canGenerate = ageGroup.trim().length > 0 && subject.trim().length > 0;

  return (
    <div className="landing-container">
      <div className="landing-content">
        <div className="landing-header">
          <h1 className="landing-title">Orchestration Graph Scheduler</h1>
          <p className="landing-subtitle">
            Create AI-powered, pedagogically-grounded lesson plans in minutes
          </p>
        </div>

        <form onSubmit={handleSubmit} className="landing-form">
          <div className="landing-form-section">
            <h3 className="landing-section-title">Tell us about your class</h3>

            <div className="landing-form-group">
              <label htmlFor="ageGroup" className="landing-label">
                Age Group / Grade Level *
              </label>
              <input
                id="ageGroup"
                type="text"
                className="landing-input"
                value={ageGroup}
                onChange={(e) => setAgeGroup(e.target.value)}
                placeholder="e.g., '12-13 years old', 'high school seniors'"
                required
                disabled={isLoading}
                autoFocus
              />
            </div>

            <div className="landing-form-group">
              <label htmlFor="subject" className="landing-label">
                Subject / Topic *
              </label>
              <input
                id="subject"
                type="text"
                className="landing-input"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="e.g., 'Photosynthesis', 'Quadratic Equations'"
                required
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="landing-info-box">
            <strong>What you'll get:</strong>
            <ul className="landing-benefits-list">
              <li>Automatically optimized lesson sequence</li>
              <li>Concrete examples tailored to your subject</li>
              <li>Age-appropriate teaching resources and tips</li>
              <li>Ready-to-use teaching materials</li>
            </ul>
          </div>

          <div className="landing-actions">
            <button
              type="submit"
              className="landing-generate-button"
              disabled={!canGenerate || isLoading}
            >
              {isLoading ? (
                <>
                  <span className="landing-spinner"></span>
                  {loadingMessage}
                </>
              ) : (
                'Generate Lesson Plan'
              )}
            </button>

            <button
              type="button"
              className="landing-custom-button"
              onClick={onCustom}
              disabled={isLoading}
            >
              Custom Orchestration
            </button>
          </div>

          <p className="landing-hint">
            Want full control? Use <strong>Custom Orchestration</strong> to manually build your lesson
          </p>
        </form>
      </div>
    </div>
  );
};

export default LandingPage;
