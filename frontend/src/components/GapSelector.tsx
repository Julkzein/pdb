// frontend/src/components/GapSelector.tsx
import React, { useState, useEffect } from 'react';

interface Gap {
  index: number;
  isHard: boolean;
  distance?: number;
}

interface GapSelectorProps {
  gaps: number[];
  selectedGap: number | null;
  onGapSelect: (gapIndex: number) => void;
}

const GapSelector: React.FC<GapSelectorProps> = ({ gaps, selectedGap, onGapSelect }) => {
  return (
    <div style={{
      display: 'flex',
      gap: '10px',
      padding: '10px',
      background: '#f3f4f6',
      borderRadius: '8px',
      marginBottom: '10px',
    }}>
      <span style={{ fontWeight: 'bold', alignSelf: 'center' }}>Gaps:</span>
      {gaps.length === 0 ? (
        <span style={{ color: '#10b981' }}>✓ No gaps to fill</span>
      ) : (
        gaps.map((gapIndex) => (
          <button
            key={gapIndex}
            onClick={() => onGapSelect(gapIndex)}
            style={{
              padding: '5px 10px',
              background: selectedGap === gapIndex ? '#667eea' : '#fff',
              color: selectedGap === gapIndex ? '#fff' : '#000',
              border: '1px solid #667eea',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px',
            }}
          >
            Gap {gapIndex}
          </button>
        ))
      )}
    </div>
  );
};

export default GapSelector;