/**
 * PipelineEditor — React Flow-based visual pipeline topology editor.
 *
 * M8 enhancements:
 * - CanvasToolbar with undo/redo, add-node, template gallery
 * - Keyboard shortcuts (Ctrl+Z, Ctrl+S, Ctrl+Enter, etc.)
 * - Node execution status animation via stageStatuses prop
 * - ReportNode + StickyNote custom node types
 * - First-visit auto-load of quick_evaluate template
 * - Template gallery card overlay
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  type Connection,
  type Edge,
  type Node,
  type NodeTypes,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { API_PREFIX } from '../../../config/api';
import AgentNode from './AgentNode';
import ReportNode from './ReportNode';
import StickyNote from './StickyNote';
import CanvasToolbar from './CanvasToolbar';
import TemplateGallery, { type TemplateInfo } from './TemplateGallery';
import { useCanvasHistory } from './useCanvasHistory';
import { useKeyboardShortcuts } from './useKeyboardShortcuts';
import {
  ALL_AGENT_IDS,
  AGENT_META,
  INITIAL_POSITIONS,
  type AgentNodeId,
  type AgentNodeData,
  type SavedTemplate,
  type TopologyState,
  type ReportOutput,
} from './types';

/* ──────────────────────── Constants ──────────────────────── */

const STORAGE_KEY = 'vulca-custom-templates';
const VISITED_KEY = 'vulca-has-visited';
const MAX_SAVED = 10;
const VALIDATE_DEBOUNCE = 500;

/** Backend template shape (subset we use) */
interface ApiTemplate {
  name: string;
  display_name: string;
  description: string;
  nodes: string[];
  edges: [string, string][];
  conditional_edges?: { source: string; targets: Record<string, string> }[];
  enable_loop: boolean;
}

/** Execution status for each agent stage */
export interface StageStatus {
  status: 'idle' | 'running' | 'done' | 'error' | 'skipped';
  duration?: number;
}

const nodeTypes: NodeTypes = {
  agent: AgentNode,
  report: ReportNode,
  sticky: StickyNote,
} as unknown as NodeTypes;

/* ──────────────────────── Helpers ──────────────────────── */

function toFlowNodes(agentIds: AgentNodeId[]): Node<AgentNodeData>[] {
  return agentIds.map((id) => ({
    id,
    type: id === 'report' ? 'report' : 'agent',
    position: INITIAL_POSITIONS[id] ?? { x: 0, y: 0 },
    data: {
      agentId: id,
      label: AGENT_META[id].label,
      icon: AGENT_META[id].icon,
      description: AGENT_META[id].description,
      params: {},
    },
  }));
}

function sequentialEdges(nodes: string[]): [string, string][] {
  const pairs: [string, string][] = [];
  for (let i = 0; i < nodes.length - 1; i++) pairs.push([nodes[i], nodes[i + 1]]);
  return pairs;
}

function toFlowEdges(
  edgeList: [string, string][] | undefined,
  conditionalEdges?: ApiTemplate['conditional_edges'],
  nodeList?: string[],
): Edge[] {
  const resolved = edgeList ?? (nodeList ? sequentialEdges(nodeList) : []);
  const edges: Edge[] = resolved.map(([src, tgt]) => ({
    id: `${src}->${tgt}`,
    source: src,
    target: tgt,
    animated: false,
    markerEnd: { type: MarkerType.ArrowClosed, width: 16, height: 16 },
  }));

  if (conditionalEdges) {
    for (const ce of conditionalEdges) {
      for (const [label, tgt] of Object.entries(ce.targets)) {
        const id = `${ce.source}->${tgt}:${label}`;
        if (edges.find((e) => e.id === id)) continue;
        edges.push({
          id,
          source: ce.source,
          target: tgt,
          label,
          type: 'smoothstep',
          animated: true,
          style: { strokeDasharray: '6 3', opacity: 0.7 },
          markerEnd: { type: MarkerType.ArrowClosed, width: 16, height: 16 },
        });
      }
    }
  }
  return edges;
}

function extractTopology(
  nodes: Node<AgentNodeData>[],
  edges: Edge[],
): TopologyState {
  const nodeIds = nodes
    .filter((n) => n.type !== 'sticky')
    .map((n) => n.id as AgentNodeId);
  const edgePairs: [string, string][] = edges.map((e) => [e.source, e.target]);
  const hasLoop = edges.some(
    (e) =>
      (e.source === 'queen' && e.target === 'draft') ||
      (e.source === 'queen' && e.target === 'router'),
  );
  return { nodes: nodeIds, edges: edgePairs, enableLoop: hasLoop };
}

/* ──────────────────────── localStorage ──────────────────── */

function loadSavedTemplates(): SavedTemplate[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as SavedTemplate[]) : [];
  } catch {
    return [];
  }
}

function persistTemplates(list: SavedTemplate[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list.slice(0, MAX_SAVED)));
}

function isFirstVisit(): boolean {
  return !localStorage.getItem(VISITED_KEY);
}

function markVisited() {
  localStorage.setItem(VISITED_KEY, '1');
}

/* ──────────────────────── Component ──────────────────────── */

interface Props {
  onRun: (params: {
    template: string;
    customNodes?: string[];
    customEdges?: [string, string][];
    nodeParams?: Record<string, Record<string, unknown>>;
  }) => void;
  disabled?: boolean;
  onNodeSelect?: (nodeId: AgentNodeId | null) => void;
  nodeParams?: Record<string, Record<string, unknown>>;
  /** Live execution status from SSE events */
  stageStatuses?: Record<string, StageStatus>;
  /** Report output to display in ReportNode */
  reportOutput?: ReportOutput;
}

export default function PipelineEditor({
  onRun,
  disabled,
  onNodeSelect,
  nodeParams,
  stageStatuses,
  reportOutput,
}: Props) {
  /* ── API templates ── */
  const [apiTemplates, setApiTemplates] = useState<ApiTemplate[]>([]);
  const [activeTemplate, setActiveTemplate] = useState('default');
  const [savedTemplates, setSavedTemplates] = useState(loadSavedTemplates);
  const [showGallery, setShowGallery] = useState(false);
  const [showFirstVisitBanner, setShowFirstVisitBanner] = useState(false);

  useEffect(() => {
    fetch(`${API_PREFIX}/prototype/templates`)
      .then((r) => r.json())
      .then((data: ApiTemplate[]) => {
        if (data.length) setApiTemplates(data);
      })
      .catch(() => {});
  }, []);

  /* ── React Flow state ── */
  const [nodes, setNodes, onNodesChange] = useNodesState<Node<AgentNodeData>>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [, setSelectedNodeId] = useState<AgentNodeId | null>(null);

  /* ── Undo / Redo ── */
  const { pushSnapshot, undo, redo, canUndo, canRedo } = useCanvasHistory();

  const applySnapshot = useCallback(
    (fn: () => ReturnType<typeof undo>) => {
      const snap = fn();
      if (snap) {
        setNodes(snap.nodes as Node<AgentNodeData>[]);
        setEdges(snap.edges);
      }
    },
    [setNodes, setEdges],
  );

  const handleUndo = useCallback(() => applySnapshot(undo), [applySnapshot, undo]);
  const handleRedo = useCallback(() => applySnapshot(redo), [applySnapshot, redo]);

  /* ── Validation ── */
  const [validation, setValidation] = useState<{
    valid: boolean;
    errors: string[];
    warnings: string[];
  } | null>(null);
  const validateTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const runValidation = useCallback(
    (n: Node<AgentNodeData>[], e: Edge[]) => {
      clearTimeout(validateTimer.current);
      validateTimer.current = setTimeout(() => {
        const topo = extractTopology(n, e);
        if (topo.nodes.length === 0 || topo.edges.length === 0) {
          setValidation({
            valid: false,
            errors: ['Topology needs at least 1 node and 1 edge'],
            warnings: [],
          });
          return;
        }
        fetch(`${API_PREFIX}/prototype/topologies/validate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ nodes: topo.nodes, edges: topo.edges }),
        })
          .then((r) => r.json())
          .then((data: { valid: boolean; errors: string[]; warnings: string[] }) =>
            setValidation(data),
          )
          .catch(() =>
            setValidation({ valid: true, errors: [], warnings: ['Validation API unavailable'] }),
          );
      }, VALIDATE_DEBOUNCE);
    },
    [],
  );

  /* ── Load template into canvas ── */
  const loadTemplate = useCallback(
    (name: string) => {
      // Push snapshot before loading
      if (nodes.length > 0) pushSnapshot(nodes, edges);

      setActiveTemplate(name);
      setSelectedNodeId(null);
      onNodeSelect?.(null);
      setShowGallery(false);

      const saved = savedTemplates.find((s) => s.id === name);
      if (saved) {
        const flowNodes = toFlowNodes(saved.topology.nodes);
        const flowEdges = toFlowEdges(saved.topology.edges);
        setNodes(flowNodes);
        setEdges(flowEdges);
        runValidation(flowNodes, flowEdges);
        return;
      }

      const tmpl = apiTemplates.find((t) => t.name === name);
      if (tmpl) {
        const agentIds = tmpl.nodes.filter((n): n is AgentNodeId =>
          ALL_AGENT_IDS.includes(n as AgentNodeId),
        );
        const flowNodes = toFlowNodes(agentIds);
        const flowEdges = toFlowEdges(tmpl.edges, tmpl.conditional_edges, tmpl.nodes);
        setNodes(flowNodes);
        setEdges(flowEdges);
        runValidation(flowNodes, flowEdges);
        return;
      }

      // Fallback
      const defaultIds: AgentNodeId[] = [
        'scout', 'router', 'draft', 'critic', 'queen', 'archivist',
      ];
      const defaultEdges: [string, string][] = [
        ['scout', 'router'],
        ['router', 'draft'],
        ['draft', 'critic'],
        ['critic', 'queen'],
        ['queen', 'archivist'],
      ];
      const fn = toFlowNodes(defaultIds);
      const fe = toFlowEdges(defaultEdges);
      setNodes(fn);
      setEdges(fe);
      runValidation(fn, fe);
    },
    [apiTemplates, savedTemplates, setNodes, setEdges, runValidation, onNodeSelect, nodes, edges, pushSnapshot],
  );

  // Phase 1: load default immediately so canvas is never empty
  const didInit = useRef(false);
  useEffect(() => {
    if (!didInit.current) {
      loadTemplate('default');
      didInit.current = true;
    }
  }, [loadTemplate]);

  // Phase 2: when API templates arrive, apply first-visit logic
  const didApplyFirstVisit = useRef(false);
  useEffect(() => {
    if (apiTemplates.length > 0 && !didApplyFirstVisit.current) {
      didApplyFirstVisit.current = true;
      if (isFirstVisit()) {
        loadTemplate('quick_evaluate');
        setShowFirstVisitBanner(true);
        markVisited();
        setTimeout(() => setShowFirstVisitBanner(false), 6000);
      }
    }
  }, [apiTemplates, loadTemplate]);

  /* ── Edge connection ── */
  const onConnect = useCallback(
    (conn: Connection) => {
      pushSnapshot(nodes, edges);
      setEdges((eds) => {
        const next = addEdge(
          { ...conn, markerEnd: { type: MarkerType.ArrowClosed, width: 16, height: 16 } },
          eds,
        );
        runValidation(nodes, next);
        return next;
      });
    },
    [setEdges, nodes, edges, runValidation, pushSnapshot],
  );

  const handleEdgesChange: typeof onEdgesChange = useCallback(
    (changes) => {
      onEdgesChange(changes);
      setTimeout(() => {
        setEdges((cur) => {
          runValidation(nodes, cur);
          return cur;
        });
      }, 0);
    },
    [onEdgesChange, nodes, runValidation, setEdges],
  );

  /* ── Node selection ── */
  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      if (node.type === 'sticky') return;
      const id = node.id as AgentNodeId;
      setSelectedNodeId(id);
      onNodeSelect?.(id);
    },
    [onNodeSelect],
  );

  const onPaneClick = useCallback(() => {
    setSelectedNodeId(null);
    onNodeSelect?.(null);
  }, [onNodeSelect]);

  /* ── Save / Delete custom template ── */
  const handleSave = useCallback(() => {
    const name = prompt('Template name:');
    if (!name?.trim()) return;
    const topo = extractTopology(nodes, edges);
    const entry: SavedTemplate = {
      id: `custom-${Date.now()}`,
      name: name.trim(),
      createdAt: Date.now(),
      topology: topo,
      nodeParams: nodeParams ?? {},
    };
    const next = [entry, ...savedTemplates].slice(0, MAX_SAVED);
    setSavedTemplates(next);
    persistTemplates(next);
    setActiveTemplate(entry.id);
  }, [nodes, edges, nodeParams, savedTemplates]);

  const handleDeleteSaved = useCallback(
    (id: string) => {
      const next = savedTemplates.filter((s) => s.id !== id);
      setSavedTemplates(next);
      persistTemplates(next);
      if (activeTemplate === id) loadTemplate('default');
    },
    [savedTemplates, activeTemplate, loadTemplate],
  );

  /* ── Add node / sticky note ── */
  const handleAddNode = useCallback(
    (nodeId: AgentNodeId) => {
      pushSnapshot(nodes, edges);
      const maxX = nodes.reduce((mx, n) => Math.max(mx, n.position.x), 0);
      const newNode: Node<AgentNodeData> = {
        id: `${nodeId}-${Date.now()}`,
        type: nodeId === 'report' ? 'report' : 'agent',
        position: { x: maxX + 200, y: 80 },
        data: {
          agentId: nodeId,
          label: AGENT_META[nodeId].label,
          icon: AGENT_META[nodeId].icon,
          description: AGENT_META[nodeId].description,
          params: {},
        },
      };
      setNodes((prev) => [...prev, newNode]);
    },
    [nodes, edges, setNodes, pushSnapshot],
  );

  const handleAddStickyNote = useCallback(() => {
    pushSnapshot(nodes, edges);
    const maxX = nodes.reduce((mx, n) => Math.max(mx, n.position.x), 0);
    const newNote: Node = {
      id: `sticky-${Date.now()}`,
      type: 'sticky',
      position: { x: maxX + 200, y: -100 },
      data: { text: '', color: 'yellow' },
    };
    setNodes((prev) => [...prev, newNote as Node<AgentNodeData>]);
  }, [nodes, edges, setNodes, pushSnapshot]);

  /* ── Run ── */
  const handleRun = useCallback(() => {
    const topo = extractTopology(nodes, edges);
    const isApiTemplate = apiTemplates.some((t) => t.name === activeTemplate);
    onRun({
      template: isApiTemplate ? activeTemplate : 'default',
      customNodes: isApiTemplate ? undefined : topo.nodes,
      customEdges: isApiTemplate ? undefined : topo.edges,
      nodeParams,
    });
  }, [nodes, edges, activeTemplate, apiTemplates, nodeParams, onRun]);

  /* ── Select all / deselect ── */
  const selectAll = useCallback(() => {
    setNodes((nds) => nds.map((n) => ({ ...n, selected: true })));
  }, [setNodes]);

  const deselectAll = useCallback(() => {
    setNodes((nds) => nds.map((n) => ({ ...n, selected: false })));
    setSelectedNodeId(null);
    onNodeSelect?.(null);
  }, [setNodes, onNodeSelect]);

  /* ── Keyboard shortcuts ── */
  useKeyboardShortcuts({
    onUndo: handleUndo,
    onRedo: handleRedo,
    onSave: handleSave,
    onRun: handleRun,
    onSelectAll: selectAll,
    onDeselectAll: deselectAll,
    disabled,
  });

  /* ── Propagate stage statuses to node data ── */
  useEffect(() => {
    if (!stageStatuses) return;
    setNodes((nds) =>
      nds.map((n) => {
        if (n.type === 'sticky') return n;
        const st = stageStatuses[n.id];
        if (!st) return n;
        return {
          ...n,
          data: {
            ...n.data,
            status: st.status,
            duration: st.duration,
          },
        };
      }),
    );
  }, [stageStatuses, setNodes]);

  /* ── Propagate report output to report nodes ── */
  useEffect(() => {
    if (!reportOutput) return;
    setNodes((nds) =>
      nds.map((n) => {
        if (n.type !== 'report') return n;
        return { ...n, data: { ...n.data, reportOutput } };
      }),
    );
  }, [reportOutput, setNodes]);

  /* ── Template gallery info ── */
  const galleryTemplates: TemplateInfo[] = useMemo(() => {
    const api: TemplateInfo[] = apiTemplates.map((t) => ({
      id: t.name,
      name: t.display_name,
      description: t.description,
      nodeCount: t.nodes.length,
      nodes: t.nodes,
    }));
    const custom: TemplateInfo[] = savedTemplates.map((s) => ({
      id: s.id,
      name: s.name,
      description: `Custom template (${s.topology.nodes.length} nodes)`,
      nodeCount: s.topology.nodes.length,
      nodes: s.topology.nodes,
      isSaved: true,
    }));
    if (!api.length) {
      api.push({
        id: 'default',
        name: 'Standard Pipeline',
        description: 'Full Scout-Draft-Critic-Queen cycle',
        nodeCount: 6,
        nodes: ['scout', 'router', 'draft', 'critic', 'queen', 'archivist'],
      });
    }
    return [...api, ...custom];
  }, [apiTemplates, savedTemplates]);

  /* ──────────────────────── Render ──────────────────────── */
  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <CanvasToolbar
        onToggleGallery={() => setShowGallery((v) => !v)}
        onUndo={handleUndo}
        onRedo={handleRedo}
        canUndo={canUndo}
        canRedo={canRedo}
        onAddNode={handleAddNode}
        onAddStickyNote={handleAddStickyNote}
        onSave={handleSave}
        onRun={handleRun}
        disabled={!!disabled}
        validation={validation}
        activeTemplate={activeTemplate}
      />

      {/* First-visit banner */}
      {showFirstVisitBanner && (
        <div className="px-3 py-2 bg-blue-50 dark:bg-blue-900/20 text-xs text-blue-700 dark:text-blue-300 border-b border-blue-200 dark:border-blue-800 flex items-center justify-between">
          <span>
            This is the <strong>Quick Evaluate</strong> template. Drop in an image and click Run!
          </span>
          <button
            onClick={() => setShowFirstVisitBanner(false)}
            className="text-blue-500 hover:text-blue-700 ml-2"
          >
            &times;
          </button>
        </div>
      )}

      {/* Canvas */}
      <div className="flex-1 min-h-0 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={handleEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.3 }}
          deleteKeyCode="Backspace"
          className="bg-gray-50 dark:bg-gray-900"
        >
          <Background gap={20} size={1} />
          <Controls className="!bg-white dark:!bg-gray-800 !border-gray-200 dark:!border-gray-700 !shadow-sm" />
          <MiniMap
            nodeStrokeWidth={3}
            className="!bg-white dark:!bg-gray-800 !border-gray-200 dark:!border-gray-700"
          />
        </ReactFlow>

        {/* Template Gallery overlay */}
        {showGallery && (
          <TemplateGallery
            templates={galleryTemplates}
            activeTemplate={activeTemplate}
            onSelect={(id) => {
              loadTemplate(id);
              setShowGallery(false);
            }}
            onDelete={handleDeleteSaved}
            onClose={() => setShowGallery(false)}
          />
        )}
      </div>

      {/* Validation messages */}
      {validation && (validation.errors.length > 0 || validation.warnings.length > 0) && (
        <div className="px-3 py-2 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 text-xs space-y-0.5 flex-shrink-0 max-h-20 overflow-y-auto">
          {validation.errors.map((e, i) => (
            <div key={`e-${i}`} className="text-red-600 dark:text-red-400">
              {e}
            </div>
          ))}
          {validation.warnings.map((w, i) => (
            <div key={`w-${i}`} className="text-amber-600 dark:text-amber-400">
              {w}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
