// frontend/src/types/index.ts
export interface Activity {
  id: string;
  name: string;
  type: 'general' | 'specific';
  duration: number;
  color: string;
  description?: string;
  constraints?: ActivityConstraint[];
}

export interface ActivityConstraint {
  type: string;
  value: any;
}

export interface GraphNode {
  id: string;
  activityId: string;
  position: { x: number; y: number };
  data: Activity;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
}

export interface OrchestrationGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata?: {
    created: Date;
    modified: Date;
    name: string;
  };
}