/**
 * Toolbar Panel
 * Action buttons for orchestration graph operations
 */

import React, { useState } from 'react';
import { useOrchestrationStore, useGraphState, useIsLoading } from '../../store/orchestrationStore';
import { useTeacherContextStore } from '../../store/teacherContextStore';
import { apiService } from '../../services/apiService';
import TeacherContextModal from '../TeacherView/TeacherContextModal';
import './ToolbarPanel.css';

const ToolbarPanel: React.FC = () => {
  const graphState = useGraphState();
  const isLoading = useIsLoading();
  const { resetGraph, autoAdd, saveGraph, loadGraph } = useOrchestrationStore();
  const { openModal, isModalOpen, closeModal } = useTeacherContextStore();

  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [showLoadDialog, setShowLoadDialog] = useState(false);
  const [showVisualization, setShowVisualization] = useState(false);
  const [visualizationImage, setVisualizationImage] = useState<string>('');
  const [filename, setFilename] = useState('');
  const [savedFiles, setSavedFiles] = useState<string[]>([]);

  const handleReset = async () => {
    if (window.confirm('Reset the orchestration graph? This cannot be undone.')) {
      try {
        await resetGraph();
        alert('Graph reset successfully');
      } catch (error: any) {
        alert(`Failed to reset: ${error.message}`);
      }
    }
  };

  const handleAutoAdd = async () => {
    try {
      await autoAdd();
      alert('Added recommended activity');
    } catch (error: any) {
      alert(`${error.message}`);
    }
  };

  const handleComplete = async () => {
    try {
      const result = await apiService.autoComplete();
      if (result.goalReached) {
        alert(`Goal reached! Added ${result.activitiesAdded} activities to complete the orchestration.`);
      } else {
        alert(`Added ${result.activitiesAdded} activities, but goal not yet reached. You may need to adjust manually.`);
      }
      // Refresh the graph state
      const state = await apiService.getGraphState();
      useOrchestrationStore.setState({ graphState: state, isLoading: false });
    } catch (error: any) {
      alert(`Failed to complete: ${error.message}`);
    }
  };

  const handleSave = async () => {
    setShowSaveDialog(true);
  };

  const doSave = async () => {
    try {
      const savedFilename = await saveGraph(filename || undefined);
      alert(`Saved as ${savedFilename}`);
      setShowSaveDialog(false);
      setFilename('');
    } catch (error: any) {
      alert(` Failed to save: ${error.message}`);
    }
  };

  const handleLoad = async () => {
    try {
      const files = await apiService.getSavedFiles();
      setSavedFiles(files.map(f => f.filename));
      setShowLoadDialog(true);
    } catch (error: any) {
      alert(`Failed to load file list: ${error.message}`);
    }
  };

  const doLoad = async (selectedFile: string) => {
    try {
      await loadGraph(selectedFile);
      alert(`Loaded ${selectedFile}`);
      setShowLoadDialog(false);
    } catch (error: any) {
      alert(`Failed to load: ${error.message}`);
    }
  };

  const handlePrint = async () => {
    try {
      const result = await apiService.visualizeGraph();
      setVisualizationImage(result.image);
      setShowVisualization(true);
    } catch (error: any) {
      alert(`Failed to generate visualization: ${error.message}`);
    }
  };

  const hasActivities = graphState && graphState.activities.length > 0;
  const hasGaps = graphState && graphState.hardGapsCount > 0;

  return (
    <div className="toolbar-panel">
      <div className="toolbar-section">
        <button onClick={handleReset} disabled={isLoading || !hasActivities} className="toolbar-btn">
          Reset
        </button>
        <button onClick={handleLoad} disabled={isLoading} className="toolbar-btn">
          Load
        </button>
        <button onClick={handleSave} disabled={isLoading} className="toolbar-btn">
          Save
        </button>
        <button onClick={handlePrint} disabled={isLoading || !hasActivities} className="toolbar-btn">
          Print
        </button>
      </div>

      <div className="toolbar-section">
        <button
          onClick={handleAutoAdd}
          disabled={isLoading || !hasGaps}
          className="toolbar-btn primary"
        >
          Add Recommended
        </button>
        <button
          onClick={handleComplete}
          disabled={isLoading || !hasGaps}
          className="toolbar-btn primary"
          style={{
            background: '#8b5cf6',
          }}
        >
          Complete
        </button>
      </div>

      <div className="toolbar-section">
        <button
          onClick={openModal}
          disabled={isLoading || !hasActivities}
          className="toolbar-btn success"
          style={{
            background: '#10b981',
            color: 'white',
            fontWeight: '600',
          }}
        >
          Go Teach
        </button>
      </div>

      {/* Save Dialog */}
      {showSaveDialog && (
        <div className="modal-overlay" onClick={() => setShowSaveDialog(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>Save Orchestration</h3>
            <input
              type="text"
              placeholder="Enter filename (optional)"
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              style={{
                width: '100%',
                padding: '8px',
                marginBottom: '16px',
                border: '1px solid #d1d5db',
                borderRadius: '4px',
              }}
            />
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
              <button onClick={() => setShowSaveDialog(false)} className="toolbar-btn">
                Cancel
              </button>
              <button onClick={doSave} className="toolbar-btn primary">
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Load Dialog */}
      {showLoadDialog && (
        <div className="modal-overlay" onClick={() => setShowLoadDialog(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>Load Orchestration</h3>
            {savedFiles.length > 0 ? (
              <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                {savedFiles.map(file => (
                  <div
                    key={file}
                    onClick={() => doLoad(file)}
                    style={{
                      padding: '8px',
                      margin: '4px 0',
                      background: '#f9fafb',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      border: '1px solid #e5e7eb',
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#e5e7eb'}
                    onMouseLeave={(e) => e.currentTarget.style.background = '#f9fafb'}
                  >
                    {file}
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ padding: '20px', textAlign: 'center', color: '#9ca3af' }}>
                No saved files found
              </div>
            )}
            <div style={{ marginTop: '16px', textAlign: 'right' }}>
              <button onClick={() => setShowLoadDialog(false)} className="toolbar-btn">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Visualization Modal */}
      {showVisualization && (
        <div className="modal-overlay" onClick={() => setShowVisualization(false)}>
          <div
            className="modal-content"
            onClick={e => e.stopPropagation()}
            style={{
              maxWidth: '1200px',
              width: '90vw',
              maxHeight: '90vh',
              overflow: 'auto',
              padding: '20px'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ margin: 0 }}>State Space Visualization</h3>
              <button
                onClick={() => setShowVisualization(false)}
                style={{
                  background: '#ef4444',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  padding: '8px 16px',
                  cursor: 'pointer',
                  fontSize: '14px',
                }}
              >
                Close
              </button>
            </div>
            <div style={{ display: 'flex', justifyContent: 'center', background: '#f9fafb', padding: '20px', borderRadius: '8px' }}>
              <img
                src={`data:image/png;base64,${visualizationImage}`}
                alt="State Space Graph"
                style={{
                  maxWidth: '100%',
                  height: 'auto',
                  boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                }}
              />
            </div>
            <div style={{ marginTop: '16px', textAlign: 'right' }}>
              <button
                onClick={() => {
                  const link = document.createElement('a');
                  link.href = `data:image/png;base64,${visualizationImage}`;
                  link.download = 'orchestration-graph-visualization.png';
                  link.click();
                }}
                className="toolbar-btn primary"
              >
                Download PNG
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Teacher Context Modal */}
      <TeacherContextModal
        isOpen={isModalOpen}
        onClose={closeModal}
      />
    </div>
  );
};

export default ToolbarPanel;
