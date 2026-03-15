/**
 * Hook managing per-node muted/bypassed/collapsed state.
 */

import { useState, useCallback } from 'react';
import { type NodeVisualState, DEFAULT_NODE_STATE } from './nodeStates';

export function useNodeStates() {
  const [states, setStates] = useState<Record<string, NodeVisualState>>({});

  const getState = useCallback(
    (nodeId: string): NodeVisualState => states[nodeId] ?? DEFAULT_NODE_STATE,
    [states],
  );

  const toggleMute = useCallback((nodeId: string) => {
    setStates((prev) => {
      const current = prev[nodeId] ?? { ...DEFAULT_NODE_STATE };
      return { ...prev, [nodeId]: { ...current, muted: !current.muted } };
    });
  }, []);

  const toggleBypass = useCallback((nodeId: string) => {
    setStates((prev) => {
      const current = prev[nodeId] ?? { ...DEFAULT_NODE_STATE };
      return { ...prev, [nodeId]: { ...current, bypassed: !current.bypassed } };
    });
  }, []);

  const toggleCollapse = useCallback((nodeId: string) => {
    setStates((prev) => {
      const current = prev[nodeId] ?? { ...DEFAULT_NODE_STATE };
      return { ...prev, [nodeId]: { ...current, collapsed: !current.collapsed } };
    });
  }, []);

  return { states, getState, toggleMute, toggleBypass, toggleCollapse };
}
