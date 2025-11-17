/**
 * Teacher View - Printable Lesson Plan
 * Clean, professional format for teachers to use during lessons
 */

import React from 'react';
import { OrchestrationGraphState, formatTime, getPlaneName } from '../../types/domain';
import './TeacherView.css';

interface TeacherViewProps {
  isOpen: boolean;
  onClose: () => void;
  graphState: OrchestrationGraphState;
}

const TeacherView: React.FC<TeacherViewProps> = ({ isOpen, onClose, graphState }) => {
  if (!isOpen) return null;

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadHTML = () => {
    // Generate standalone HTML document
    const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lesson Plan - ${currentDate}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: Georgia, 'Times New Roman', serif;
      line-height: 1.6;
      color: #111827;
      padding: 40px;
      max-width: 900px;
      margin: 0 auto;
      background: white;
    }
    h1 { font-size: 32px; margin-bottom: 16px; text-align: center; }
    h2 { font-size: 22px; margin: 30px 0 16px 0; padding-bottom: 8px; border-bottom: 2px solid #e5e7eb; }
    h3 { font-size: 18px; margin: 16px 0 12px 0; }
    .header { text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 3px double #374151; }
    .meta { display: flex; justify-content: center; gap: 30px; font-size: 14px; flex-wrap: wrap; }
    .meta p { margin: 4px 0; }
    .warning { color: #dc2626; font-weight: 600; }
    .objectives-box { background: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 16px 20px; margin: 16px 0; }
    .objectives-box p { margin: 8px 0; }
    .activity-item { display: flex; gap: 16px; padding: 20px; background: #f9fafb; border-radius: 8px; border: 1px solid #e5e7eb; margin: 20px 0; page-break-inside: avoid; }
    .activity-number { flex-shrink: 0; width: 40px; height: 40px; background: #0ea5e9; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px; }
    .activity-details { flex: 1; }
    .activity-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .activity-header h3 { margin: 0; font-size: 18px; }
    .plane-badge { padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; text-transform: uppercase; }
    .plane-0 { background: #dbeafe; color: #1e40af; }
    .plane-1 { background: #e9d5ff; color: #6b21a8; }
    .plane-2 { background: #fce7f3; color: #9f1239; }
    .activity-description { margin: 8px 0; color: #4b5563; font-size: 14px; }
    .activity-timing { display: flex; gap: 20px; margin: 12px 0; font-size: 13px; color: #6b7280; }
    .activity-notes { margin-top: 12px; padding-top: 12px; border-top: 1px dashed #d1d5db; }
    .notes-space { margin-top: 8px; color: #9ca3af; }
    .activity-list { list-style: disc; padding-left: 24px; margin: 12px 0; }
    .activity-list li { margin: 8px 0; color: #4b5563; }
    .checklist-item { display: flex; align-items: center; gap: 12px; padding: 12px; margin: 8px 0; background: #f9fafb; border-radius: 6px; border: 1px solid #e5e7eb; }
    .checklist-item input { width: 20px; height: 20px; }
    .notes-area { background: #fefce8; padding: 20px; border-radius: 8px; border: 1px solid #fde047; margin: 16px 0; }
    .blank-line { margin: 12px 0; color: #9ca3af; }
    .footer { margin-top: 40px; padding-top: 20px; border-top: 2px solid #e5e7eb; text-align: center; color: #6b7280; font-size: 12px; }
    @media print {
      body { padding: 20px; }
      .activity-item { page-break-inside: avoid; }
    }
    .print-btn { position: fixed; top: 20px; right: 20px; padding: 12px 24px; background: #0ea5e9; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
    .print-btn:hover { background: #0284c7; }
    @media print { .print-btn { display: none; } }
  </style>
</head>
<body>
  <button class="print-btn" onclick="window.print()">🖨️ Print This Page</button>

  <div class="header">
    <h1>Orchestrated Lesson Plan</h1>
    <div class="meta">
      <p><strong>Date:</strong> ${currentDate}</p>
      <p><strong>Total Duration:</strong> ${formatTime(graphState.totTime)} / ${formatTime(graphState.tBudget)}</p>
      <p><strong>Goal Status:</strong> ${graphState.goalReached ? '✓ Achieved' : '○ In Progress'}</p>
      ${graphState.hardGapsCount > 0 ? `<p class="warning"><strong>Learning Gaps:</strong> ${graphState.hardGapsCount} gap(s) to address</p>` : ''}
    </div>
  </div>

  <div class="section">
    <h2>Learning Objectives</h2>
    <div class="objectives-box">
      <p><strong>Starting Point:</strong> Fluency ${graphState.start.v[0].toFixed(2)}, Depth ${graphState.start.v[1].toFixed(2)}</p>
      <p><strong>Target Goal:</strong> Fluency ${graphState.goal.v[0].toFixed(2)}, Depth ${graphState.goal.v[1].toFixed(2)}</p>
      <p><strong>Current Progress:</strong> Fluency ${graphState.reached.v[0].toFixed(2)}, Depth ${graphState.reached.v[1].toFixed(2)}</p>
    </div>
  </div>

  <div class="section">
    <h2>Lesson Timeline</h2>
    ${graphState.activities.map((activity, index) => `
      <div class="activity-item">
        <div class="activity-number">${index + 1}</div>
        <div class="activity-details">
          <div class="activity-header">
            <h3>${activity.activityName}</h3>
            <span class="plane-badge plane-${activity.plane}">${getPlaneName(activity.plane)}</span>
          </div>
          <p class="activity-description">${activity.activityDescription}</p>
          <div class="activity-timing">
            <span><strong>Duration:</strong> ${formatTime(activity.time)}</span>
            <span><strong>Starts:</strong> ${formatTime(activity.startsAfter)}</span>
            <span><strong>Ends:</strong> ${formatTime(activity.endsAfter)}</span>
          </div>
          <div class="activity-notes">
            <strong>Teacher Notes:</strong>
            <div class="notes-space">_______________________________________</div>
          </div>
        </div>
      </div>
    `).join('')}
  </div>

  <div class="section">
    <h2>Activities by Organization Mode</h2>
    ${activitiesByPlane.class.length > 0 ? `
      <h3>Whole Class Activities</h3>
      <ul class="activity-list">
        ${activitiesByPlane.class.map(act => `<li><strong>${act.activityName}</strong> (${formatTime(act.time)}) - ${act.activityDescription}</li>`).join('')}
      </ul>
    ` : ''}
    ${activitiesByPlane.team.length > 0 ? `
      <h3>Team-Based Activities</h3>
      <ul class="activity-list">
        ${activitiesByPlane.team.map(act => `<li><strong>${act.activityName}</strong> (${formatTime(act.time)}) - ${act.activityDescription}</li>`).join('')}
      </ul>
    ` : ''}
    ${activitiesByPlane.individual.length > 0 ? `
      <h3>Individual Work</h3>
      <ul class="activity-list">
        ${activitiesByPlane.individual.map(act => `<li><strong>${act.activityName}</strong> (${formatTime(act.time)}) - ${act.activityDescription}</li>`).join('')}
      </ul>
    ` : ''}
  </div>

  <div class="section">
    <h2>Preparation Checklist</h2>
    <div class="checklist-item">
      <input type="checkbox"> Review all activity descriptions and learning objectives
    </div>
    <div class="checklist-item">
      <input type="checkbox"> Prepare materials for team-based activities (${activitiesByPlane.team.length} activities)
    </div>
    <div class="checklist-item">
      <input type="checkbox"> Set up workstations for individual activities (${activitiesByPlane.individual.length} activities)
    </div>
    <div class="checklist-item">
      <input type="checkbox"> Ensure all technology/equipment is working
    </div>
    <div class="checklist-item">
      <input type="checkbox"> Review timing and transitions between activities
    </div>
  </div>

  <div class="section">
    <h2>Additional Notes & Reflections</h2>
    <div class="notes-area">
      <p>Use this space for observations, student feedback, or adjustments for next time:</p>
      <div class="blank-line">_________________________________________________________________</div>
      <div class="blank-line">_________________________________________________________________</div>
      <div class="blank-line">_________________________________________________________________</div>
      <div class="blank-line">_________________________________________________________________</div>
      <div class="blank-line">_________________________________________________________________</div>
      <div class="blank-line">_________________________________________________________________</div>
      <div class="blank-line">_________________________________________________________________</div>
      <div class="blank-line">_________________________________________________________________</div>
    </div>
  </div>

  <div class="footer">
    <p>Generated by Orchestration Graph Scheduler</p>
    <p>${new Date().toLocaleString()}</p>
  </div>
</body>
</html>
    `.trim();

    // Create blob and download
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `lesson-plan-${new Date().toISOString().split('T')[0]}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Group activities by plane for better organization
  const activitiesByPlane = {
    individual: graphState.activities.filter(act => act.plane === 0),
    team: graphState.activities.filter(act => act.plane === 1),
    class: graphState.activities.filter(act => act.plane === 2),
  };

  const currentDate = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  return (
    <>
      <style dangerouslySetInnerHTML={{__html: `
        @media print {
          @page {
            size: A4;
            margin: 15mm;
          }

          html, body {
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            background: white !important;
          }

          body > div#root,
          body > div#root > * {
            display: none !important;
          }

          .teacher-view-overlay {
            display: block !important;
            visibility: visible !important;
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 100% !important;
            height: auto !important;
            background: white !important;
            padding: 0 !important;
            margin: 0 !important;
            z-index: 999999 !important;
          }

          .teacher-view-overlay * {
            visibility: visible !important;
          }

          .teacher-view-header,
          .no-print {
            display: none !important;
          }

          .teacher-view-container {
            box-shadow: none !important;
            max-width: none !important;
            max-height: none !important;
            overflow: visible !important;
            background: white !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            border-radius: 0 !important;
          }

          .teacher-view-content {
            padding: 0 !important;
            font-size: 11pt !important;
            line-height: 1.4 !important;
            color: black !important;
          }
        }
      `}} />
      <div className="teacher-view-overlay" onClick={onClose}>
        <div className="teacher-view-container" onClick={(e) => e.stopPropagation()}>
          <div className="teacher-view-header no-print">
            <h2>Lesson Plan - Teacher View</h2>
            <div className="header-actions">
              <button onClick={handleDownloadHTML} className="print-button" style={{ marginRight: '8px' }}>
                📥 Download HTML
              </button>
              <button onClick={onClose} className="close-button">×</button>
            </div>
          </div>

          <div className="teacher-view-content">
          {/* Header for print */}
          <div className="lesson-header">
            <h1>Orchestrated Lesson Plan</h1>
            <div className="lesson-meta">
              <p><strong>Date:</strong> {currentDate}</p>
              <p><strong>Total Duration:</strong> {formatTime(graphState.totTime)} / {formatTime(graphState.tBudget)}</p>
              <p><strong>Goal Status:</strong> {graphState.goalReached ? '✓ Achieved' : '○ In Progress'}</p>
              {graphState.hardGapsCount > 0 && (
                <p className="warning"><strong>Learning Gaps:</strong> {graphState.hardGapsCount} gap(s) to address</p>
              )}
            </div>
          </div>

          {/* Learning Objectives */}
          <div className="section">
            <h2>Learning Objectives</h2>
            <div className="objectives-box">
              <p><strong>Starting Point:</strong> Fluency {graphState.start.v[0].toFixed(2)}, Depth {graphState.start.v[1].toFixed(2)}</p>
              <p><strong>Target Goal:</strong> Fluency {graphState.goal.v[0].toFixed(2)}, Depth {graphState.goal.v[1].toFixed(2)}</p>
              <p><strong>Current Progress:</strong> Fluency {graphState.reached.v[0].toFixed(2)}, Depth {graphState.reached.v[1].toFixed(2)}</p>
            </div>
          </div>

          {/* Timeline Overview */}
          <div className="section">
            <h2>Lesson Timeline</h2>
            <div className="timeline-summary">
              {graphState.activities.map((activity, index) => (
                <div key={index} className="activity-item">
                  <div className="activity-number">{index + 1}</div>
                  <div className="activity-details">
                    <div className="activity-header">
                      <h3>{activity.activityName}</h3>
                      <span className={`plane-badge plane-${activity.plane}`}>
                        {getPlaneName(activity.plane)}
                      </span>
                    </div>
                    <p className="activity-description">{activity.activityDescription}</p>
                    <div className="activity-timing">
                      <span><strong>Duration:</strong> {formatTime(activity.time)}</span>
                      <span><strong>Starts:</strong> {formatTime(activity.startsAfter)}</span>
                      <span><strong>Ends:</strong> {formatTime(activity.endsAfter)}</span>
                    </div>
                    <div className="activity-notes">
                      <strong>Teacher Notes:</strong>
                      <div className="notes-space">_______________________________________</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Activities by Organization Mode */}
          <div className="section page-break-before">
            <h2>Activities by Organization Mode</h2>

            {activitiesByPlane.class.length > 0 && (
              <div className="plane-section">
                <h3>Whole Class Activities</h3>
                <ul className="activity-list">
                  {activitiesByPlane.class.map((activity, idx) => (
                    <li key={idx}>
                      <strong>{activity.activityName}</strong> ({formatTime(activity.time)}) -
                      {activity.activityDescription}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {activitiesByPlane.team.length > 0 && (
              <div className="plane-section">
                <h3>Team-Based Activities</h3>
                <ul className="activity-list">
                  {activitiesByPlane.team.map((activity, idx) => (
                    <li key={idx}>
                      <strong>{activity.activityName}</strong> ({formatTime(activity.time)}) -
                      {activity.activityDescription}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {activitiesByPlane.individual.length > 0 && (
              <div className="plane-section">
                <h3>Individual Work</h3>
                <ul className="activity-list">
                  {activitiesByPlane.individual.map((activity, idx) => (
                    <li key={idx}>
                      <strong>{activity.activityName}</strong> ({formatTime(activity.time)}) -
                      {activity.activityDescription}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Materials & Preparation */}
          <div className="section page-break-before">
            <h2>Preparation Checklist</h2>
            <div className="checklist">
              <div className="checklist-item">
                <input type="checkbox" /> Review all activity descriptions and learning objectives
              </div>
              <div className="checklist-item">
                <input type="checkbox" /> Prepare materials for team-based activities ({activitiesByPlane.team.length} activities)
              </div>
              <div className="checklist-item">
                <input type="checkbox" /> Set up workstations for individual activities ({activitiesByPlane.individual.length} activities)
              </div>
              <div className="checklist-item">
                <input type="checkbox" /> Ensure all technology/equipment is working
              </div>
              <div className="checklist-item">
                <input type="checkbox" /> Review timing and transitions between activities
              </div>
            </div>
          </div>

          {/* Additional Notes */}
          <div className="section">
            <h2>Additional Notes & Reflections</h2>
            <div className="notes-area">
              <p>Use this space for observations, student feedback, or adjustments for next time:</p>
              <div className="blank-lines">
                {[...Array(8)].map((_, i) => (
                  <div key={i} className="blank-line">_________________________________________________________________</div>
                ))}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="lesson-footer">
            <p>Generated by Orchestration Graph Scheduler</p>
            <p>{new Date().toLocaleString()}</p>
          </div>
        </div>
      </div>
    </div>
    </>
  );
};

export default TeacherView;
