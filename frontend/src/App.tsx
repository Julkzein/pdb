// frontend/src/App.tsx
import React, { useEffect, useState, useCallback } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import ActivityLibrary from './components/ActivityLibrary';
import GraphCanvas from './components/GraphCanvas';
import LessonTimeline from './components/LessonTimeline';
import Toolbar from './components/Toolbar';
import { api } from './services/api';
import GapSelector from './components/GapSelector';
import RecommendationPanel from './components/RecommendationPanel';
import { Activity } from './types';
import './App.css';

function App() {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [totalTime, setTotalTime] = useState(0);
  const [budgetTime] = useState(120);
  const [orchestrationState, setOrchestrationState] = useState<any>(null);
  const [selectedGap, setSelectedGap] = useState<number | null>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);

  const checkBackendConnection = useCallback(async () => {
    try {
      const result = await api.healthCheck();
      console.log('Backend connected:', result);
      setIsConnected(true);
    } catch (error) {
      console.error('Backend not connected:', error);
      setIsConnected(false);
    }
  }, []);

  const loadActivities = useCallback(async () => {
    try {
      const data = await api.getActivities();
      setActivities(data);
      console.log('Loaded activities:', data);
    } catch (error) {
      console.error('Failed to load activities:', error);
      setActivities([
        { id: '1', name: 'Introduction', type: 'general', duration: 15, color: '#4CAF50' },
        { id: '2', name: 'Main Activity', type: 'general', duration: 30, color: '#2196F3' },
        { id: '3', name: 'Discussion', type: 'general', duration: 20, color: '#FF9800' },
        { id: '4', name: 'Conclusion', type: 'general', duration: 10, color: '#9C27B0' },
      ]);
    }
  }, []);

  useEffect(() => {
    const initializeApp = async () => {
      setLoading(true);
      await checkBackendConnection();
      await loadActivities();
      setLoading(false);
    };
    
    initializeApp();
  }, [checkBackendConnection, loadActivities]);

  const handleGapSelect = async (gapIndex: number) => {
    setSelectedGap(gapIndex);
    try {
      const result = await api.setGapFocus(gapIndex);
      setRecommendations(result.recommendations || []);
    } catch (error) {
      console.error('Error selecting gap:', error);
    }
  };

  const handleAutoAddFromGap = async () => {
    try {
      const result = await api.autoAddFromGap();
      if (result) {
        setOrchestrationState(result);
        // Refresh recommendations
        if (selectedGap !== null) {
          handleGapSelect(selectedGap);
        }
      }
    } catch (error) {
      console.error('Error auto-adding:', error);
    }
  };

  const handleRecommend = async () => {
    try {
      // Get current orchestration state
      const state = await api.getOrchestrationState();
      setOrchestrationState(state);
      
      if (state.hardGapsCount > 0) {
        // Select the first hard gap
        const firstGap = state.hardGapsList[0];
        handleGapSelect(firstGap);
      } else {
        alert('✅ No gaps to fill - orchestration is complete!');
      }
    } catch (error) {
      console.error('Recommendation failed:', error);
      // Fallback to simple recommendation
      const randomActivity = activities[Math.floor(Math.random() * activities.length)];
      if (window.confirm(`Add recommended activity: ${randomActivity.name}?`)) {
        // You can implement adding the activity here
        console.log('Add activity:', randomActivity);
      }
    }
  };

  const handleSave = async () => {
    const filename = prompt('Enter filename:', 'my_orchestration.json');
    if (filename) {
      try {
        const result = await api.saveOrchestration(filename);
        alert(result.message);
      } catch (error) {
        console.error('Save failed:', error);
        alert('Could not save orchestration');
      }
    }
  };

  const handleLoad = async () => {
    const filename = prompt('Enter filename to load:', 'my_orchestration.json');
    if (filename) {
      try {
        const result = await api.loadOrchestration(filename);
        alert(result.message);
      } catch (error) {
        console.error('Load failed:', error);
        alert('Could not load orchestration');
      }
    }
  };

  const handlePrint = async () => {
    try {
      const result = await api.printOrchestration();
      const printWindow = window.open('', '_blank');
      if (printWindow) {
        printWindow.document.write('<pre>' + result.content + '</pre>');
        printWindow.document.close();
        printWindow.print();
      }
    } catch (error) {
      console.error('Print failed:', error);
      alert('Could not print orchestration');
    }
  };

  const handleReset = () => {
    if (window.confirm('Reset all activities?')) {
      window.location.reload();
    }
  };

  const handleValidate = async () => {
    try {
      const result = await api.validateOrchestration({});
      if (result.valid) {
        alert('✅ Orchestration is valid!');
      } else {
        alert(`❌ Validation errors:\n${result.errors.join('\n')}`);
      }
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  const handleGraphUpdate = (nodes: any[]) => {
    // Update orchestration state based on graph changes
    console.log('Graph updated with nodes:', nodes);
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <div>Loading...</div>
      </div>
    );
  }

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="App">
        <header className="App-header">
          <h1>🎯 Orchestration Graph Scheduler</h1>
          <span className={isConnected ? 'connected' : 'disconnected'}>
            Backend: {isConnected ? '✅ Connected' : '❌ Disconnected'}
          </span>
        </header>
        
        <Toolbar
          onSave={handleSave}
          onLoad={handleLoad}
          onPrint={handlePrint}
          onRecommend={handleRecommend}
          onReset={handleReset}
          onValidate={handleValidate}
          totalTime={totalTime}
          budgetTime={budgetTime}
        />
        
        <div className="App-body">
          <div className="sidebar">
            <ActivityLibrary activities={activities} />
            {orchestrationState && (
              <GapSelector 
                gaps={orchestrationState.hardGapsList || []}
                selectedGap={selectedGap}
                onGapSelect={handleGapSelect}
              />
            )}
            {recommendations.length > 0 && (
              <RecommendationPanel
                recommendations={recommendations}
                onSelectActivity={(idx) => {
                  console.log('Add activity:', idx);
                }}
                onAutoAdd={handleAutoAddFromGap}
              />
            )}
          </div>
          
          <div className="main-content">
            <GraphCanvas 
              onTimeUpdate={setTotalTime}
              onGraphUpdate={handleGraphUpdate}
            />
            <LessonTimeline />
          </div>
        </div>
      </div>
    </DndProvider>
  );
}

export default App;