/**
 * useAutoArrange — Dagre-based automatic node layout.
 * LR direction, 60px node sep, 120px rank sep.
 */

import { useCallback } from 'react';
import type { Node, Edge } from '@xyflow/react';
import dagre from '@dagrejs/dagre';

export function useAutoArrange() {
  const arrange = useCallback(
    (nodes: Node[], edges: Edge[]): Node[] => {
      const g = new dagre.graphlib.Graph();
      g.setDefaultEdgeLabel(() => ({}));
      g.setGraph({
        rankdir: 'LR',
        nodesep: 60,
        ranksep: 120,
        marginx: 20,
        marginy: 20,
      });

      // Add nodes with estimated dimensions
      for (const node of nodes) {
        const width = node.type === 'frame' ? 300 : node.type === 'reroute' ? 12 : 140;
        const height = node.type === 'frame' ? 200 : node.type === 'reroute' ? 12 : 80;
        g.setNode(node.id, { width, height });
      }

      // Add edges
      for (const edge of edges) {
        g.setEdge(edge.source, edge.target);
      }

      dagre.layout(g);

      return nodes.map((node) => {
        const pos = g.node(node.id);
        if (!pos) return node;
        return {
          ...node,
          position: { x: pos.x - (pos.width || 140) / 2, y: pos.y - (pos.height || 80) / 2 },
        };
      });
    },
    [],
  );

  return { arrange };
}
