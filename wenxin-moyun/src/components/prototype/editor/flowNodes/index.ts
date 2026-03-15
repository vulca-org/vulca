export { default as FlowNodeBase } from './FlowNodeBase';
export { default as IfElseNode } from './IfElseNode';
export { default as LoopNode } from './LoopNode';
export { default as MergeNode } from './MergeNode';
export { default as SplitNode } from './SplitNode';
export { default as GateNode } from './GateNode';

export const FLOW_NODE_META = {
  ifElse: { label: 'If / Else', icon: '🔀', description: 'Conditional routing' },
  loop: { label: 'Loop', icon: '🔄', description: 'Iteration controller' },
  merge: { label: 'Merge', icon: '🔗', description: 'Combine branches' },
  split: { label: 'Split', icon: '🔱', description: 'Split to branches' },
  gate: { label: 'Quality Gate', icon: '🚦', description: 'Score threshold gate' },
};
