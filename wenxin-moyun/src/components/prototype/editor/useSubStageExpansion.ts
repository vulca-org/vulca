/**
 * useSubStageExpansion — Expand/collapse hook for Draft/Critic nodes.
 *
 * Replaces a parent Draft/Critic node with multiple sub-stage nodes,
 * or collapses them back into the parent.
 */

import { useCallback, useState } from 'react';
import type { Node, Edge } from '@xyflow/react';
import { DRAFT_SUB_STAGES, CRITIC_SUB_STAGES, type SubStageDef } from './subStageDefinitions';

interface ExpansionState {
  expandedNodes: Set<string>;
}

export function useSubStageExpansion() {
  const [expansionState, setExpansionState] = useState<ExpansionState>({
    expandedNodes: new Set(),
  });

  const isExpanded = useCallback(
    (nodeId: string) => expansionState.expandedNodes.has(nodeId),
    [expansionState],
  );

  const expandNode = useCallback(
    (
      nodeId: string,
      agentId: string,
      nodes: Node[],
      edges: Edge[],
    ): { nodes: Node[]; edges: Edge[] } => {
      const subStages = agentId === 'draft' ? DRAFT_SUB_STAGES : agentId === 'critic' ? CRITIC_SUB_STAGES : [];
      if (subStages.length === 0) return { nodes, edges };

      const parentNode = nodes.find((n) => n.id === nodeId);
      if (!parentNode) return { nodes, edges };

      const baseX = parentNode.position.x;
      const baseY = parentNode.position.y;

      // Create sub-stage nodes
      const subNodes: Node[] = subStages.map((sub: SubStageDef, idx: number) => ({
        id: `${nodeId}__${sub.id}`,
        type: 'substage',
        position: { x: baseX, y: baseY + idx * 45 },
        data: {
          label: sub.label,
          icon: sub.icon,
          parentAgent: agentId,
          subStageId: sub.id,
          status: 'pending',
        },
      }));

      // Create sequential edges between sub-stages
      const subEdges: Edge[] = [];
      for (let i = 0; i < subNodes.length - 1; i++) {
        subEdges.push({
          id: `${subNodes[i].id}->${subNodes[i + 1].id}`,
          source: subNodes[i].id,
          target: subNodes[i + 1].id,
          animated: false,
        });
      }

      // Redirect incoming edges to first sub-stage
      const firstSubId = subNodes[0].id;
      const lastSubId = subNodes[subNodes.length - 1].id;
      const updatedEdges = edges.map((e) => {
        if (e.target === nodeId) return { ...e, target: firstSubId };
        if (e.source === nodeId) return { ...e, source: lastSubId };
        return e;
      });

      // Remove parent node, add sub-nodes
      const updatedNodes = nodes.filter((n) => n.id !== nodeId);

      setExpansionState((prev) => ({
        expandedNodes: new Set([...prev.expandedNodes, nodeId]),
      }));

      return {
        nodes: [...updatedNodes, ...subNodes],
        edges: [...updatedEdges, ...subEdges],
      };
    },
    [],
  );

  const collapseNode = useCallback(
    (
      nodeId: string,
      agentId: string,
      originalNode: Node,
      nodes: Node[],
      edges: Edge[],
    ): { nodes: Node[]; edges: Edge[] } => {
      const prefix = `${nodeId}__`;

      // Find edges that connect to/from sub-nodes
      const subNodeIds = nodes.filter((n) => n.id.startsWith(prefix)).map((n) => n.id);
      const firstSubId = subNodeIds[0];
      const lastSubId = subNodeIds[subNodeIds.length - 1];

      // Redirect edges back to parent
      const updatedEdges = edges
        .filter((e) => !(e.source.startsWith(prefix) && e.target.startsWith(prefix)))
        .map((e) => {
          if (e.target === firstSubId) return { ...e, target: nodeId };
          if (e.source === lastSubId) return { ...e, source: nodeId };
          return e;
        });

      // Remove sub-nodes, add parent back
      const updatedNodes = nodes.filter((n) => !n.id.startsWith(prefix));

      setExpansionState((prev) => {
        const next = new Set(prev.expandedNodes);
        next.delete(nodeId);
        return { expandedNodes: next };
      });

      return {
        nodes: [...updatedNodes, originalNode],
        edges: updatedEdges,
      };
    },
    [],
  );

  /** True if any Draft node is currently expanded into sub-stages. */
  const hasExpandedDraft = [...expansionState.expandedNodes].some((id) => id === 'draft');

  return { isExpanded, expandNode, collapseNode, hasExpandedDraft };
}
