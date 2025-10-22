// frontend/src/components/RecommendationPanel.tsx
import React from 'react';

interface Recommendation {
  idx: number;
  name: string;
  score: number | null;
  isBest: boolean;
  flags: {
    exhausted: boolean;
    tooLong: boolean;
    noProgress: boolean;
  };
  okeyToTake: boolean;
}

interface RecommendationPanelProps {
  recommendations: Recommendation[];
  onSelectActivity: (idx: number) => void;
  onAutoAdd: () => void;
}

const RecommendationPanel: React.FC<RecommendationPanelProps> = ({
  recommendations,
  onSelectActivity,
  onAutoAdd,
}) => {
  if (recommendations.length === 0) {
    return null;
  }

  const bestActivity = recommendations.find(r => r.isBest);

  return (
    <div style={{
      padding: '15px',
      background: '#f9fafb',
      borderRadius: '8px',
      marginTop: '10px',
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '10px' 
      }}>
        <h3 style={{ margin: 0 }}>Recommendations for Gap</h3>
        <button
          onClick={onAutoAdd}
          style={{
            padding: '8px 16px',
            background: '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 'bold',
          }}
        >
          + Add Best
        </button>
      </div>
      
      <div style={{ 
        maxHeight: '200px', 
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '5px',
      }}>
        {recommendations.map((rec) => (
          <div
            key={rec.idx}
            onClick={() => rec.okeyToTake && onSelectActivity(rec.idx)}
            style={{
              padding: '8px',
              background: rec.isBest ? '#10b981' : rec.okeyToTake ? '#fff' : '#f3f4f6',
              color: rec.isBest ? '#fff' : rec.okeyToTake ? '#000' : '#9ca3af',
              border: rec.isBest ? '2px solid #059669' : '1px solid #e5e7eb',
              borderRadius: '6px',
              cursor: rec.okeyToTake ? 'pointer' : 'not-allowed',
              opacity: rec.okeyToTake ? 1 : 0.6,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div>
              <div style={{ fontWeight: rec.isBest ? 'bold' : 'normal' }}>
                {rec.name}
                {rec.isBest && ' ⭐'}
              </div>
              <div style={{ fontSize: '11px', marginTop: '2px' }}>
                {rec.score !== null && `Score: ${rec.score.toFixed(2)}`}
                {rec.flags.exhausted && ' 🔄'}
                {rec.flags.tooLong && ' ⏰'}
                {rec.flags.noProgress && ' ❌'}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecommendationPanel;