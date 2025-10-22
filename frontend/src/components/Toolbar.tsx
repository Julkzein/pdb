// frontend/src/components/Toolbar.tsx
import React from 'react';

interface ToolbarProps {
  onSave: () => void;
  onLoad: () => void;
  onPrint: () => void;
  onRecommend: () => void;
  onReset: () => void;
  onValidate: () => void;
  totalTime: number;
  budgetTime: number;
}

const Toolbar: React.FC<ToolbarProps> = ({
  onSave,
  onLoad,
  onPrint,
  onRecommend,
  onReset,
  onValidate,
  totalTime,
  budgetTime,
}) => {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '10px 20px',
      backgroundColor: '#f3f4f6',
      borderBottom: '1px solid #e5e7eb',
    }}>
      <div style={{ display: 'flex', gap: '10px' }}>
        <button onClick={onRecommend} style={buttonStyle('#10b981')}>
          Recommend
        </button>
        <button onClick={onValidate} style={buttonStyle('#3b82f6')}>
          Validate
        </button>
        <button onClick={onReset} style={buttonStyle('#ef4444')}>
          Reset
        </button>
      </div>
      
      <div style={{ 
        display: 'flex', 
        alignItems: 'center',
        gap: '20px',
        fontSize: '14px',
        fontWeight: 'bold',
      }}>
        <span style={{ color: totalTime > budgetTime ? '#ef4444' : '#10b981' }}>
          Time: {totalTime}/{budgetTime} min
        </span>
      </div>
      
      <div style={{ display: 'flex', gap: '10px' }}>
        <button onClick={onSave} style={buttonStyle('#6366f1')}>
          Save
        </button>
        <button onClick={onLoad} style={buttonStyle('#6366f1')}>
          Load
        </button>
        <button onClick={onPrint} style={buttonStyle('#6366f1')}>
          Print
        </button>
      </div>
    </div>
  );
};

const buttonStyle = (color: string): React.CSSProperties => ({
  padding: '8px 16px',
  backgroundColor: color,
  color: 'white',
  border: 'none',
  borderRadius: '6px',
  cursor: 'pointer',
  fontSize: '14px',
  fontWeight: 'bold',
  transition: 'opacity 0.2s',
});

export default Toolbar;