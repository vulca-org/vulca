/**
 * PipelineEditor — React Flow-based visual pipeline topology editor.
 *
 * Phase 5 enhancements:
 * - All new node types: frame, reroute, substage, skill, processing, flow, output, inputs
 * - TypedEdge with DataType-colored strokes
 * - Mute/bypass/collapse node states
 * - Sub-stage expansion (double-click Draft/Critic)
 * - Skill browser drawer (drag & drop)
 * - Auto-arrange via dagre
 * - Inline preview data propagation
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
  type EdgeTypes,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { API_PREFIX } from '@/config/api';
import AgentNode from './AgentNode';
import ReportNode from './ReportNode';
import StickyNote from './StickyNote';
import FrameNode from './FrameNode';
import RerouteNode from './RerouteNode';
import SubStageNode from './SubStageNode';
import SkillNode from './SkillNode';
import SkillBrowser from './SkillBrowser';
import TypedEdge from './TypedEdge';
import CanvasToolbar from './CanvasToolbar';
import TemplateGallery, { type TemplateInfo } from './TemplateGallery';
import NodeSearchPopup from './NodeSearchPopup';
import { useCanvasHistory } from './useCanvasHistory';
import { useKeyboardShortcuts } from './useKeyboardShortcuts';
import { useNodeStates } from './useNodeStates';
import { useSubStageExpansion } from './useSubStageExpansion';
import { useAutoArrange } from './useAutoArrange';
import {
  SketchUploadNode,
  ReferenceImageNode,
  MaskRegionNode,
  TextPromptNode,
  ScriptNode,
  ModelImportNode,
  AudioImportNode,
} from './inputNodes';
import {
  StyleTransferNode,
  ColorHarmonyNode,
  CompositionBalanceNode,
  UpscaleNode,
  DepthMapNode,
  EdgeDetectionNode,
  ElementExtractNode,
} from './processingNodes';
import {
  IfElseNode,
  LoopNode as FlowLoopNode,
  MergeNode,
  SplitNode,
  GateNode as FlowGateNode,
} from './flowNodes';
import {
  SaveNode,
  GalleryPublishNode,
  ExportNode,
  CompareNode,
} from './outputNodes';
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

/* ──────────────────────── Node & Edge Types ──────────────── */

const nodeTypes: NodeTypes = {
  agent: AgentNode,
  report: ReportNode,
  sticky: StickyNote,
  // Phase 5A
  frame: FrameNode,
  reroute: RerouteNode,
  // Phase 5B
  substage: SubStageNode,
  // Phase 5C
  skill: SkillNode,
  // Input nodes
  sketch: SketchUploadNode,
  reference: ReferenceImageNode,
  mask: MaskRegionNode,
  textPrompt: TextPromptNode,
  script: ScriptNode,
  modelImport: ModelImportNode,
  audioImport: AudioImportNode,
  // Processing nodes
  styleTransfer: StyleTransferNode,
  colorHarmony: ColorHarmonyNode,
  compositionBalance: CompositionBalanceNode,
  upscale: UpscaleNode,
  depthMap: DepthMapNode,
  edgeDetection: EdgeDetectionNode,
  elementExtract: ElementExtractNode,
  // Flow control nodes
  ifElse: IfElseNode,
  loop: FlowLoopNode,
  merge: MergeNode,
  split: SplitNode,
  gate: FlowGateNode,
  // Output nodes
  save: SaveNode,
  galleryPublish: GalleryPublishNode,
  export: ExportNode,
  compare: CompareNode,
} as unknown as NodeTypes;

const edgeTypes: EdgeTypes = {
  typed: TypedEdge,
} as unknown as EdgeTypes;

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
    .filter((n) => n.type !== 'sticky' && n.type !== 'frame' && n.type !== 'reroute')
    .map((n) => n.id as AgentNodeId);
  const edgePairs: [string, string][] = edges.map((e) => [e.source, e.target]);
  const hasLoop = edges.some(
    (e) =>
      (e.source === 'queen' && e.target === 'draft') ||
      (e.source === 'queen' && e.target === 'scout'),
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
  /** Phase 5: Pipeline candidate/score/decision data */
  candidates?: { image_url?: string; candidate_id?: string }[];
  scoredCandidates?: { dimension: string; score: number }[];
  queenDecision?: { action: string; reason?: string; round?: number };
}

export default function PipelineEditor({
  onRun,
  disabled,
  onNodeSelect,
  nodeParams,
  stageStatuses,
  reportOutput,
  candidates,
  scoredCandidates,
  queenDecision,
}: Props) {
  /* ── API templates ── */
  const [apiTemplates, setApiTemplates] = useState<ApiTemplate[]>([]);
  const [activeTemplate, setActiveTemplate] = useState('default');
  const [savedTemplates, setSavedTemplates] = useState(loadSavedTemplates);
  const [showGallery, setShowGallery] = useState(false);
  const [showFirstVisitBanner, setShowFirstVisitBanner] = useState(false);
  const [showSkillBrowser, setShowSkillBrowser] = useState(false);

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

  /* ── Phase 5 hooks ── */
  const { states: _nodeVisualStates, toggleMute, toggleBypass, toggleCollapse } = useNodeStates();
  const { isExpanded, expandNode, collapseNode, hasExpandedDraft } = useSubStageExpansion();
  const { arrange } = useAutoArrange();

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
        const errors: string[] = [];
        const warnings: string[] = [];

        if (topo.nodes.length === 0 || topo.edges.length === 0) {
          errors.push('Topology needs at least 1 node and 1 edge');
        } else {
          // Check all edge endpoints reference existing nodes
          const nodeSet = new Set(topo.nodes as string[]);
          for (const [src, tgt] of topo.edges) {
            if (!nodeSet.has(src)) errors.push(`Edge source "${src}" not found in nodes`);
            if (!nodeSet.has(tgt)) errors.push(`Edge target "${tgt}" not found in nodes`);
          }
          // Check for disconnected nodes
          const connected = new Set<string>();
          for (const [src, tgt] of topo.edges) {
            connected.add(src);
            connected.add(tgt);
          }
          const disconnected = topo.nodes.filter((id) => !connected.has(id));
          if (disconnected.length > 0) {
            warnings.push(`Disconnected nodes: ${disconnected.join(', ')}`);
          }
        }

        setValidation({ valid: errors.length === 0, errors, warnings });
      }, VALIDATE_DEBOUNCE);
    },
    [],
  );

  /* ── Load template into canvas ── */
  const loadTemplate = useCallback(
    (name: string) => {
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
      const defaultIds: AgentNodeId[] = ['scout', 'draft', 'critic', 'queen'];
      const defaultEdges: [string, string][] = [
        ['scout', 'draft'], ['draft', 'critic'],
        ['critic', 'queen'],
      ];
      const fn = toFlowNodes(defaultIds);
      const fe = toFlowEdges(defaultEdges);
      setNodes(fn);
      setEdges(fe);
      runValidation(fn, fe);
    },
    [apiTemplates, savedTemplates, setNodes, setEdges, runValidation, onNodeSelect, nodes, edges, pushSnapshot],
  );

  // Phase 1: load default immediately
  const didInit = useRef(false);
  useEffect(() => {
    if (!didInit.current) {
      loadTemplate('default');
      didInit.current = true;
    }
  }, [loadTemplate]);

  // Phase 2: first-visit logic
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
      if (node.type === 'sticky' || node.type === 'frame' || node.type === 'reroute') return;
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

  /* ── Double-click for sub-stage expansion ── */
  const handleNodeDoubleClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const agentId = (node.data as AgentNodeData)?.agentId;
      if (agentId !== 'draft' && agentId !== 'critic') return;

      if (isExpanded(node.id)) {
        const originalNode = {
          ...node,
          data: { ...(node.data as AgentNodeData) },
        };
        const result = collapseNode(node.id, agentId, originalNode, nodes, edges);
        setNodes(result.nodes as Node<AgentNodeData>[]);
        setEdges(result.edges);
      } else {
        const result = expandNode(node.id, agentId, nodes, edges);
        setNodes(result.nodes as Node<AgentNodeData>[]);
        setEdges(result.edges);
      }
    },
    [nodes, edges, setNodes, setEdges, isExpanded, expandNode, collapseNode],
  );

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

  /* ── Add node ── */
  const handleAddNode = useCallback(
    (nodeId: AgentNodeId | string) => {
      pushSnapshot(nodes, edges);
      const maxX = nodes.reduce((mx, n) => Math.max(mx, n.position.x), 0);

      // Determine node type
      let type: string;
      let data: Record<string, unknown>;

      if (ALL_AGENT_IDS.includes(nodeId as AgentNodeId)) {
        const id = nodeId as AgentNodeId;
        type = id === 'report' ? 'report' : 'agent';
        data = {
          agentId: id,
          label: AGENT_META[id].label,
          icon: AGENT_META[id].icon,
          description: AGENT_META[id].description,
          params: {},
        };
      } else if (nodeId === 'frame') {
        type = 'frame';
        data = { label: 'Frame', color: '#334155' };
      } else if (nodeId === 'reroute') {
        type = 'reroute';
        data = {};
      } else {
        // All other node types use their nodeId as type
        type = nodeId;
        data = {};
      }

      const newNode: Node = {
        id: `${nodeId}-${Date.now()}`,
        type,
        position: { x: maxX + 200, y: 80 },
        data,
      };
      setNodes((prev) => [...prev, newNode as Node<AgentNodeData>]);
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

  /* ── Frame + Reroute ── */
  const handleAddFrame = useCallback(() => {
    handleAddNode('frame');
  }, [handleAddNode]);

  const handleAddReroute = useCallback(() => {
    handleAddNode('reroute');
  }, [handleAddNode]);

  /* ── Auto-arrange ── */
  const handleAutoArrange = useCallback(() => {
    pushSnapshot(nodes, edges);
    const arranged = arrange(nodes, edges);
    setNodes(arranged as Node<AgentNodeData>[]);
  }, [nodes, edges, setNodes, pushSnapshot, arrange]);

  /* ── Node search popup ── */
  const [showNodeSearch, setShowNodeSearch] = useState(false);

  const handleDeleteSelected = useCallback(() => {
    const selectedIds = nodes.filter((n) => n.selected).map((n) => n.id);
    if (selectedIds.length === 0) return;
    pushSnapshot(nodes, edges);
    setNodes((nds) => nds.filter((n) => !n.selected));
    setEdges((eds) =>
      eds.filter((e) => !selectedIds.includes(e.source) && !selectedIds.includes(e.target)),
    );
  }, [nodes, edges, setNodes, setEdges, pushSnapshot]);

  const handleDuplicateSelected = useCallback(() => {
    const selected = nodes.filter((n) => n.selected);
    if (selected.length === 0) return;
    pushSnapshot(nodes, edges);
    const newNodes = selected.map((n) => ({
      ...n,
      id: `${n.id}-copy-${Date.now()}`,
      position: { x: n.position.x + 40, y: n.position.y + 40 },
      selected: false,
    }));
    setNodes((prev) => [...prev, ...newNodes]);
  }, [nodes, edges, setNodes, pushSnapshot]);

  const rfInstance = useRef<{ fitView: () => void } | null>(null);
  const handleFitView = useCallback(() => {
    rfInstance.current?.fitView();
  }, []);

  /* ── Mute/Bypass/Collapse selected ── */
  const handleMuteSelected = useCallback(() => {
    setNodes((nds) =>
      nds.map((n) => {
        if (!n.selected) return n;
        const newVal = !n.data.muted;
        toggleMute(n.id);
        return { ...n, data: { ...n.data, muted: newVal } };
      }),
    );
  }, [setNodes, toggleMute]);

  const handleBypassSelected = useCallback(() => {
    setNodes((nds) =>
      nds.map((n) => {
        if (!n.selected) return n;
        const newVal = !n.data.bypassed;
        toggleBypass(n.id);
        return { ...n, data: { ...n.data, bypassed: newVal } };
      }),
    );
  }, [setNodes, toggleBypass]);

  const handleCollapseSelected = useCallback(() => {
    setNodes((nds) =>
      nds.map((n) => {
        if (!n.selected) return n;
        const newVal = !n.data.collapsed;
        toggleCollapse(n.id);
        return { ...n, data: { ...n.data, collapsed: newVal } };
      }),
    );
  }, [setNodes, toggleCollapse]);

  /* ── Drag & drop from skill browser ── */
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const skillData = e.dataTransfer.getData('application/vulca-skill');
      if (!skillData) return;

      try {
        const skill = JSON.parse(skillData);
        const position = rfInstance.current
          ? { x: e.clientX - 200, y: e.clientY - 100 }
          : { x: e.clientX, y: e.clientY };

        const newNodeId = `skill-${Date.now()}`;
        const newNode: Node = {
          id: newNodeId,
          type: 'skill',
          position,
          data: {
            skillName: skill.display_name || skill.name,
            skillId: skill.name,
            tags: skill.tags || [],
          },
        };
        setNodes((prev) => [...prev, newNode as Node<AgentNodeData>]);

        // Auto-connect: prefer selected node, else nearest node within 200px
        const selectedNodes = nodes.filter((n) => n.selected);
        let sourceNode: Node | null = selectedNodes[0] ?? null;
        if (!sourceNode && nodes.length > 0) {
          let minDist = Infinity;
          for (const n of nodes) {
            const dist = Math.hypot(n.position.x - position.x, n.position.y - position.y);
            if (dist < minDist) {
              minDist = dist;
              sourceNode = n;
            }
          }
          if (minDist > 200) sourceNode = null;
        }
        if (sourceNode) {
          setEdges((prev) => [
            ...prev,
            {
              id: `${sourceNode!.id}->${newNodeId}`,
              source: sourceNode!.id,
              target: newNodeId,
              type: 'typed',
              markerEnd: { type: MarkerType.ArrowClosed, width: 16, height: 16 },
            },
          ]);
        }
      } catch {
        // Invalid drag data
      }
    },
    [setNodes, setEdges, nodes],
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  }, []);

  /* ── Run ── */
  const handleRun = useCallback(() => {
    const topo = extractTopology(nodes, edges);
    const isApiTemplate = apiTemplates.some((t) => t.name === activeTemplate);

    // Inject sub-stage expansion state into node_params
    const mergedParams = { ...nodeParams };
    if (hasExpandedDraft) {
      mergedParams.draft = {
        ...(mergedParams.draft || {}),
        enable_sub_stages: true,
        recipe_name: 'image_standard',
      };
    }

    onRun({
      template: isApiTemplate ? activeTemplate : 'default',
      customNodes: isApiTemplate ? undefined : topo.nodes,
      customEdges: isApiTemplate ? undefined : topo.edges,
      nodeParams: mergedParams,
    });
  }, [nodes, edges, activeTemplate, apiTemplates, nodeParams, hasExpandedDraft, onRun]);

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
    onOpenNodeSearch: () => setShowNodeSearch(true),
    onDeleteSelected: handleDeleteSelected,
    onDuplicateSelected: handleDuplicateSelected,
    onFitView: handleFitView,
    onMuteSelected: handleMuteSelected,
    onBypassSelected: handleBypassSelected,
    onCollapseSelected: handleCollapseSelected,
    onAddFrame: handleAddFrame,
    onAutoArrange: handleAutoArrange,
    disabled,
  });

  /* ── Propagate stage statuses + inline preview data to node data ── */
  useEffect(() => {
    if (!stageStatuses && !candidates && !scoredCandidates && !queenDecision) return;
    setNodes((nds) =>
      nds.map((n) => {
        if (n.type === 'sticky' || n.type === 'frame' || n.type === 'reroute') return n;
        const st = stageStatuses?.[n.id];
        const agentId = (n.data as AgentNodeData)?.agentId;
        const updates: Partial<AgentNodeData> = {};

        if (st) {
          updates.status = st.status;
          updates.duration = st.duration;
        }

        // Propagate inline preview data
        if (agentId === 'draft' && candidates) {
          updates.candidates = candidates;
        }
        if (agentId === 'critic' && scoredCandidates) {
          updates.scores = scoredCandidates;
        }
        if (agentId === 'queen' && queenDecision) {
          updates.decision = queenDecision;
        }

        if (Object.keys(updates).length === 0) return n;
        return { ...n, data: { ...n.data, ...updates } };
      }),
    );
  }, [stageStatuses, candidates, scoredCandidates, queenDecision, setNodes]);

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
        nodeCount: 4,
        nodes: ['scout', 'draft', 'critic', 'queen'],
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
        onAddFrame={handleAddFrame}
        onAddReroute={handleAddReroute}
        onAutoArrange={handleAutoArrange}
        onToggleSkills={() => setShowSkillBrowser((v) => !v)}
      />

      {/* First-visit banner */}
      {showFirstVisitBanner && (
        <div className="px-3 py-2 bg-[#f9f9ff] dark:bg-[#C87F4A]/10 text-xs text-[#C87F4A] dark:text-[#DDA574] border-b border-[#C9C2B8] dark:border-[#4A433C] flex items-center justify-between">
          <span>
            This is the <strong>Quick Evaluate</strong> template. Drop in an image and click Run!
          </span>
          <button
            onClick={() => setShowFirstVisitBanner(false)}
            className="text-[#C87F4A] hover:text-[#A85D3B] ml-2"
          >
            &times;
          </button>
        </div>
      )}

      {/* Canvas */}
      <div className="flex-1 min-h-0 relative">
        {/* Skill browser drawer */}
        <SkillBrowser
          visible={showSkillBrowser}
          onClose={() => setShowSkillBrowser(false)}
        />

        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={handleEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          onNodeDoubleClick={handleNodeDoubleClick}
          onPaneClick={onPaneClick}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          onInit={(instance) => { rfInstance.current = instance; }}
          fitView
          fitViewOptions={{ padding: 0.3 }}
          deleteKeyCode="Backspace"
          proOptions={{ hideAttribution: true }}
          className="bg-gray-50 dark:bg-gray-900"
        >
          <Background gap={20} size={1} />
          <Controls className="!bg-white dark:!bg-gray-800 !border-gray-200 dark:!border-gray-700 !shadow-sm" />
          <MiniMap
            nodeStrokeWidth={3}
            className="!bg-white dark:!bg-gray-800 !border-gray-200 dark:!border-gray-700"
          />
        </ReactFlow>

        {/* Node search popup */}
        <NodeSearchPopup
          visible={showNodeSearch}
          onClose={() => setShowNodeSearch(false)}
          onAddNode={handleAddNode}
        />

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
