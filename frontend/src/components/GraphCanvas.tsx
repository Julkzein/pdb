// frontend/src/components/GraphCanvas.tsx
import React, { useCallback, useState, useRef, useEffect } from 'react';
import ReactFlow, {
  ReactFlowProvider,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap,
  Node,
  Edge,
  Connection,
  ReactFlowInstance,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useDrop } from 'react-dnd';
import { Activity } from '../types';

interface GraphCanvasProps {
  onTimeUpdate?: (time: number) => void;
  onGraphUpdate?: (nodes: Node[]) => void;
  recommendedActivity?: Activity | null;
}

interface NodeData {
  label: React.ReactNode;
  duration?: number;
  activityId?: string;
  isRecommended?: boolean;
}

const GraphCanvasInner: React.FC<GraphCanvasProps> = ({ 
  onTimeUpdate, 
  onGraphUpdate,
  recommendedActivity 
}) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
  const [nextNodeId, setNextNodeId] = useState(1);
  const [gaps, setGaps] = useState<any[]>([]);

  // Calculate total time and notify parent when nodes change
  useEffect(() => {
    if (onTimeUpdate) {
      const totalTime = nodes.reduce((sum, node) => {
        const nodeData = node.data as NodeData;
        const duration = nodeData?.duration || 0;
        return sum + duration;
      }, 0);
      onTimeUpdate(totalTime);
    }
    
    if (onGraphUpdate) {
      onGraphUpdate(nodes);
    }
  }, [nodes, onTimeUpdate, onGraphUpdate]);

  // Auto-add recommended activity if provided
  useEffect(() => {
    if (recommendedActivity && reactFlowInstance) {
      // Find the best position (after the last node or at a gap)
      const lastNode = nodes[nodes.length - 1];
      const position = lastNode 
        ? { x: lastNode.position.x + 250, y: lastNode.position.y }
        : { x: 100, y: 100 };
      
      addNode(recommendedActivity, position, true);
    }
  }, [recommendedActivity]);

  const onConnect = useCallback(
    (params: Connection) => {
      const newEdge = {
        ...params,
        type: 'smoothstep',
        markerEnd: {
          type: MarkerType.ArrowClosed,
        },
        style: { stroke: '#667eea', strokeWidth: 2 },
      };
      setEdges((eds) => addEdge(newEdge, eds));
    },
    [setEdges]
  );

  const onInit = useCallback((instance: ReactFlowInstance) => {
    console.log('ReactFlow initialized');
    setReactFlowInstance(instance);
  }, []);

  const addNode = useCallback((
    activity: Activity, 
    position: { x: number; y: number },
    isRecommended: boolean = false
  ) => {
    const newNode: Node = {
      id: `node-${nextNodeId}`,
      type: 'default',
      position: position,
      data: { 
        label: (
          <div>
            <strong>{activity.name}</strong>
            <div style={{ fontSize: '10px', marginTop: '4px' }}>
              {activity.duration} min
            </div>
            {isRecommended && (
              <div style={{ fontSize: '9px', marginTop: '2px', fontStyle: 'italic' }}>
                (Recommended)
              </div>
            )}
          </div>
        ),
        duration: activity.duration,
        activityId: activity.id,
        isRecommended: isRecommended,
      } as NodeData,
      style: {
        background: isRecommended ? '#10b981' : (activity.color || '#4CAF50'),
        color: 'white',
        border: isRecommended ? '2px solid #059669' : '1px solid #222',
        width: 180,
        borderRadius: '5px',
        boxShadow: isRecommended ? '0 4px 6px rgba(0, 0, 0, 0.1)' : 'none',
      },
    };

    console.log('Adding node:', newNode);
    setNodes((nds) => {
      // If adding recommended, try to maintain logical flow
      if (isRecommended && nds.length > 0) {
        // Auto-connect to previous node
        const lastNode = nds[nds.length - 1];
        const autoEdge: Edge = {
          id: `e${lastNode.id}-${newNode.id}`,
          source: lastNode.id,
          target: newNode.id,
          type: 'smoothstep',
          markerEnd: {
            type: MarkerType.ArrowClosed,
          },
          style: { stroke: '#10b981', strokeWidth: 2 },
        };
        setEdges((eds) => [...eds, autoEdge]);
      }
      return [...nds, newNode];
    });
    setNextNodeId(nextNodeId + 1);
  }, [nextNodeId, setNodes, setEdges]);

  const [{ isOver, canDrop }, drop] = useDrop(() => ({
    accept: 'activity',
    drop: (item: Activity, monitor) => {
      console.log('Item dropped:', item);
      const offset = monitor.getClientOffset();
      
      if (offset && reactFlowWrapper.current) {
        const bounds = reactFlowWrapper.current.getBoundingClientRect();
        let position = {
          x: offset.x - bounds.left,
          y: offset.y - bounds.top,
        };
        
        if (reactFlowInstance) {
          position = reactFlowInstance.project(position);
        }
        
        addNode(item, position);
      }
      
      return { dropped: true };
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
      canDrop: monitor.canDrop(),
    }),
  }), [reactFlowInstance, addNode]);

  const setRefs = useCallback(
    (node: HTMLDivElement | null) => {
      reactFlowWrapper.current = node;
      drop(node);
    },
    [drop]
  );

  return (
    <div className="graph-canvas" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Orchestration Graph</h2>
        {gaps.length > 0 && (
          <div style={{ fontSize: '14px', color: '#ef4444' }}>
            {gaps.length} gap{gaps.length > 1 ? 's' : ''} to fill
          </div>
        )}
      </div>
      <div 
        ref={setRefs}
        style={{ 
          flex: 1,
          border: `2px ${isOver ? 'dashed' : 'solid'} ${canDrop ? '#4CAF50' : '#ccc'}`,
          backgroundColor: isOver ? '#f0fff4' : '#fff',
          transition: 'all 0.2s',
          borderRadius: '8px',
          position: 'relative',
        }}
      >
        {nodes.length === 0 && (
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            color: '#9ca3af',
            fontSize: '14px',
            pointerEvents: 'none',
            zIndex: 1,
            textAlign: 'center',
          }}>
            <div>Drag activities here to build your orchestration graph</div>
            <div style={{ marginTop: '10px' }}>or use "Recommend" to auto-build</div>
          </div>
        )}
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={onInit}
          fitView
          attributionPosition="bottom-left"
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    </div>
  );
};

const GraphCanvas: React.FC<GraphCanvasProps> = (props) => {
  return (
    <ReactFlowProvider>
      <GraphCanvasInner {...props} />
    </ReactFlowProvider>
  );
};

export default GraphCanvas;