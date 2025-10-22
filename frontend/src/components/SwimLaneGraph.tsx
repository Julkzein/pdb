// frontend/src/components/SwimLaneGraph.tsx
import React, { useCallback, useState, useRef } from 'react';
import ReactFlow, {
  ReactFlowProvider,
  Node,
  Edge,
  Connection,
  ReactFlowInstance,
  Background,
  Controls,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useDrop } from 'react-dnd';
import { Activity } from '../types';

interface SwimLaneGraphProps {
  onNodesChange?: (nodes: any[]) => void;
  gaps?: number[];
}

const SwimLaneGraphInner: React.FC<SwimLaneGraphProps> = ({ onNodesChange, gaps = [] }) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
  
  // Define swim lanes
  const lanes = {
    individual: { y: 100, label: 'Indiv.' },
    team: { y: 200, label: 'Team' },
    class: { y: 300, label: 'Class' },
  };

  const addActivity = useCallback((activity: Activity, laneType: 'individual' | 'team' | 'class', xPosition: number) => {
    const newNode: Node = {
      id: `node-${nodes.length}`,
      position: { x: xPosition, y: lanes[laneType].y },
      data: { 
        label: activity.name,
        duration: activity.duration,
        laneType 
      },
      style: {
        background: '#40E0D0',
        width: 180,
        height: 40,
        fontSize: '12px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      },
    };
    
    setNodes(prev => [...prev, newNode]);
    if (onNodesChange) onNodesChange([...nodes, newNode]);
  }, [nodes, onNodesChange]);

  const [{ isOver }, drop] = useDrop(() => ({
    accept: 'activity',
    drop: (item: Activity, monitor) => {
      const offset = monitor.getClientOffset();
      if (offset && reactFlowWrapper.current) {
        const bounds = reactFlowWrapper.current.getBoundingClientRect();
        const y = offset.y - bounds.top;
        
        // Determine which lane based on Y position
        let laneType: 'individual' | 'team' | 'class' = 'individual';
        if (y > 250) laneType = 'class';
        else if (y > 150) laneType = 'team';
        
        const xPosition = 100 + nodes.length * 200;
        addActivity(item, laneType, xPosition);
      }
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  }), [nodes, addActivity]);

  return (
    <div
  ref={(node) => {
    drop(node);
    reactFlowWrapper.current = node;
  }}
  style={{ width: '100%', height: '500px', position: 'relative' }}
>
      {/* Lane labels */}
      <div style={{ position: 'absolute', left: '10px', top: '90px', fontSize: '12px' }}>Indiv.</div>
      <div style={{ position: 'absolute', left: '10px', top: '190px', fontSize: '12px' }}>Team</div>
      <div style={{ position: 'absolute', left: '10px', top: '290px', fontSize: '12px' }}>Class</div>
      
      {/* Gap indicators */}
      {gaps.map((gapPosition, index) => (
        <div
          key={index}
          style={{
            position: 'absolute',
            left: `${100 + gapPosition * 200}px`,
            top: '50%',
            transform: 'translateY(-50%)',
            color: 'red',
            fontSize: '24px',
            fontWeight: 'bold',
            zIndex: 10,
          }}
        >
          !
        </div>
      ))}
      
      {/* Lane backgrounds */}
      <div style={{
        position: 'absolute',
        top: '80px',
        left: '50px',
        right: '0',
        height: '60px',
        borderTop: '1px solid #ccc',
        borderBottom: '1px solid #ccc',
      }} />
      <div style={{
        position: 'absolute',
        top: '180px',
        left: '50px',
        right: '0',
        height: '60px',
        borderTop: '1px solid #ccc',
        borderBottom: '1px solid #ccc',
      }} />
      <div style={{
        position: 'absolute',
        top: '280px',
        left: '50px',
        right: '0',
        height: '60px',
        borderTop: '1px solid #ccc',
        borderBottom: '1px solid #ccc',
      }} />
      
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onInit={setReactFlowInstance}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
};

export const SwimLaneGraph: React.FC<SwimLaneGraphProps> = (props) => (
  <ReactFlowProvider>
    <SwimLaneGraphInner {...props} />
  </ReactFlowProvider>
);