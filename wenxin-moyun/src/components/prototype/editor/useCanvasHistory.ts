/**
 * useCanvasHistory — undo/redo stack for React Flow canvas state.
 * Maintains snapshots of { nodes, edges } with configurable max depth.
 */

import { useCallback, useRef, useState } from 'react';
import type { Node, Edge } from '@xyflow/react';

export interface HistorySnapshot {
  nodes: Node[];
  edges: Edge[];
}

export function useCanvasHistory(maxEntries = 50) {
  const stackRef = useRef<HistorySnapshot[]>([]);
  const indexRef = useRef(-1);
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);

  const sync = useCallback(() => {
    setCanUndo(indexRef.current > 0);
    setCanRedo(indexRef.current < stackRef.current.length - 1);
  }, []);

  const pushSnapshot = useCallback(
    (nodes: Node[], edges: Edge[]) => {
      const snapshot: HistorySnapshot = {
        nodes: JSON.parse(JSON.stringify(nodes)),
        edges: JSON.parse(JSON.stringify(edges)),
      };
      stackRef.current = stackRef.current.slice(0, indexRef.current + 1);
      stackRef.current.push(snapshot);
      if (stackRef.current.length > maxEntries) {
        stackRef.current = stackRef.current.slice(-maxEntries);
      }
      indexRef.current = stackRef.current.length - 1;
      sync();
    },
    [maxEntries, sync],
  );

  const undo = useCallback((): HistorySnapshot | null => {
    if (indexRef.current <= 0) return null;
    indexRef.current--;
    sync();
    return stackRef.current[indexRef.current];
  }, [sync]);

  const redo = useCallback((): HistorySnapshot | null => {
    if (indexRef.current >= stackRef.current.length - 1) return null;
    indexRef.current++;
    sync();
    return stackRef.current[indexRef.current];
  }, [sync]);

  return { pushSnapshot, undo, redo, canUndo, canRedo };
}
