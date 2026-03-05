/**
 * PipelineEditor — React Flow-based visual pipeline topology editor.
 *
 * Loads templates from the backend, converts them to React Flow nodes/edges,
 * and lets users drag nodes, add/remove edges, and validate topology in real-time.
 *
 * Custom topologies are serialized as custom_nodes + custom_edges for the run API.
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
import {
  ALL_AGENT_IDS,
  AGENT_META,
  INITIAL_POSITIONS,
  type AgentNodeId,
  type AgentNodeData,
  type SavedTemplate,
  type TopologyState,
} from './types';

/* ──────────────────────── Constants ──────────────────────── */

const STORAGE_KEY = 'vulca-custom-templates';
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

const nodeTypes: NodeTypes = { agent: AgentNode } as unknown as NodeTypes;

/* ──────────────────────── Helpers ──────────────────────── */

function toFlowNodes(agentIds: AgentNodeId[]): Node<AgentNodeData>[] {
  return agentIds.map((id) => ({
    id,
    type: 'agent',
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

/** Generate sequential edges from a node list (fallback when API omits edges) */
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
  const nodeIds = nodes.map((n) => n.id as AgentNodeId);
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

/* ──────────────────────── Component ──────────────────────── */

interface Props {
  onRun: (params: {
    template: string;
    customNodes?: string[];
    customEdges?: [string, string][];
    nodeParams?: Record<string, Record<string, unknown>>;
  }) => void;
  disabled?: boolean;
  /** Notify parent of selected node for NodeParamPanel */
  onNodeSelect?: (nodeId: AgentNodeId | null) => void;
  /** External node params (managed by parent via NodeParamPanel) */
  nodeParams?: Record<string, Record<string, unknown>>;
}

export default function PipelineEditor({
  onRun,
  disabled,
  onNodeSelect,
  nodeParams,
}: Props) {
  /* ── API templates ── */
  const [apiTemplates, setApiTemplates] = useState<ApiTemplate[]>([]);
  const [activeTemplate, setActiveTemplate] = useState('default');
  const [savedTemplates, setSavedTemplates] = useState(loadSavedTemplates);

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
  const [selectedNodeId, setSelectedNodeId] = useState<AgentNodeId | null>(null);

  /* ── Validation ── */
  const [validation, setValidation] = useState<{
    valid: boolean;
    errors: string[];
    warnings: string[];
  } | null>(null);
  const validateTimer = useRef<ReturnType<typeof setTimeout>>();

  const runValidation = useCallback(
    (n: Node<AgentNodeData>[], e: Edge[]) => {
      clearTimeout(validateTimer.current);
      validateTimer.current = setTimeout(() => {
        const topo = extractTopology(n, e);
        if (topo.nodes.length === 0 || topo.edges.length === 0) {
          setValidation({ valid: false, errors: ['Topology needs at least 1 node and 1 edge'], warnings: [] });
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
      setActiveTemplate(name);
      setSelectedNodeId(null);
      onNodeSelect?.(null);

      // Check saved templates first
      const saved = savedTemplates.find((s) => s.id === name);
      if (saved) {
        const flowNodes = toFlowNodes(saved.topology.nodes);
        const flowEdges = toFlowEdges(saved.topology.edges);
        setNodes(flowNodes);
        setEdges(flowEdges);
        runValidation(flowNodes, flowEdges);
        return;
      }

      // API template
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

      // Fallback: default pipeline
      const defaultIds: AgentNodeId[] = ['scout', 'router', 'draft', 'critic', 'queen', 'archivist'];
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
    [apiTemplates, savedTemplates, setNodes, setEdges, runValidation, onNodeSelect],
  );

  // Load default on mount / when API templates arrive
  const didInit = useRef(false);
  useEffect(() => {
    if (!didInit.current) {
      loadTemplate('default');
      didInit.current = true;
    }
  }, [loadTemplate]);

  /* ── Edge connection ── */
  const onConnect = useCallback(
    (conn: Connection) => {
      setEdges((eds) => {
        const next = addEdge(
          {
            ...conn,
            markerEnd: { type: MarkerType.ArrowClosed, width: 16, height: 16 },
          },
          eds,
        );
        runValidation(nodes, next);
        return next;
      });
    },
    [setEdges, nodes, runValidation],
  );

  // Re-validate on edge delete
  const handleEdgesChange: typeof onEdgesChange = useCallback(
    (changes) => {
      onEdgesChange(changes);
      // Defer to next tick so state is updated
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

  /* ── Save custom template ── */
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

  /* ── Delete saved template ── */
  const handleDeleteSaved = useCallback(
    (id: string) => {
      const next = savedTemplates.filter((s) => s.id !== id);
      setSavedTemplates(next);
      persistTemplates(next);
      if (activeTemplate === id) loadTemplate('default');
    },
    [savedTemplates, activeTemplate, loadTemplate],
  );

  /* ── Run ── */
  const handleRun = useCallback(() => {
    const topo = extractTopology(nodes, edges);
    // If it's a known API template name AND unmodified, just pass template name
    const isApiTemplate = apiTemplates.some((t) => t.name === activeTemplate);
    onRun({
      template: isApiTemplate ? activeTemplate : 'default',
      customNodes: isApiTemplate ? undefined : topo.nodes,
      customEdges: isApiTemplate ? undefined : topo.edges,
      nodeParams,
    });
  }, [nodes, edges, activeTemplate, apiTemplates, nodeParams, onRun]);

  /* ── Template options ── */
  const templateOptions = useMemo(() => {
    const api = apiTemplates.map((t) => ({ id: t.name, label: t.display_name }));
    const custom = savedTemplates.map((s) => ({ id: s.id, label: `Custom: ${s.name}` }));
    return [...(api.length ? api : [{ id: 'default', label: 'Standard Pipeline' }]), ...custom];
  }, [apiTemplates, savedTemplates]);

  /* ──────────────────────── Render ──────────────────────── */
  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center gap-2 px-3 py-2 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 flex-shrink-0 flex-wrap">
        {/* Template selector */}
        <select
          value={activeTemplate}
          onChange={(e) => loadTemplate(e.target.value)}
          className="px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          disabled={disabled}
        >
          {templateOptions.map((t) => (
            <option key={t.id} value={t.id}>
              {t.label}
            </option>
          ))}
        </select>

        {/* Save / Delete */}
        <button
          onClick={handleSave}
          className="px-2 py-1 text-xs font-medium text-blue-600 dark:text-blue-400 border border-blue-300 dark:border-blue-600 rounded-md hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors"
          disabled={disabled}
        >
          Save
        </button>
        {activeTemplate.startsWith('custom-') && (
          <button
            onClick={() => handleDeleteSaved(activeTemplate)}
            className="px-2 py-1 text-xs font-medium text-red-600 dark:text-red-400 border border-red-300 dark:border-red-600 rounded-md hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors"
          >
            Delete
          </button>
        )}

        <div className="flex-1" />

        {/* Validation badge */}
        {validation && (
          <span
            className={[
              'text-xs px-2 py-0.5 rounded-full font-medium',
              validation.valid
                ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
            ].join(' ')}
            title={[...validation.errors, ...validation.warnings].join('\n')}
          >
            {validation.valid ? 'Valid' : `${validation.errors.length} error(s)`}
          </span>
        )}

        {/* Run button */}
        <button
          onClick={handleRun}
          disabled={disabled || !validation?.valid}
          className="px-4 py-1.5 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 dark:disabled:bg-gray-600 rounded-lg transition-colors"
        >
          Run Pipeline
        </button>
      </div>

      {/* Canvas */}
      <div className="flex-1 min-h-0">
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
