/**
 * TopologyViewer — visual representation of the pipeline graph topology.
 *
 * Renders nodes as rounded rectangles in a horizontal flexbox row with
 * SVG arrow connectors. Supports both static template names and dynamic
 * node lists from the API.
 *
 * Enhancements:
 * - HITL 'waiting' state with amber pulsing indicator
 * - Optional per-stage duration display on completed nodes
 */

import { useMemo } from 'react';

const ALL_NODES = ['scout', 'router', 'draft', 'critic', 'queen', 'archivist'] as const;

const NODE_LABELS: Record<string, string> = {
  scout: 'Scout',
  router: 'Router',
  draft: 'Draft',
  critic: 'Critic',
  queen: 'Queen',
  archivist: 'Archivist',
};

const NODE_ICONS: Record<string, string> = {
  scout: '\u{1F50D}',    // 🔍
  router: '\u{1F6A6}',   // 🚦
  draft: '\u{1F3A8}',    // 🎨
  critic: '\u{1F4CA}',   // 📊
  queen: '\u{1F451}',    // 👑
  archivist: '\u{1F4BE}', // 💾
};

/** Fallback: templates that support Queen→Draft loop */
const LOOP_TEMPLATES = new Set(['default', 'fast_draft', 'interactive_full']);

/** Fallback: template→node mapping when no API data available */
const TEMPLATE_NODE_MAP: Record<string, string[]> = {
  default: ['scout', 'router', 'draft', 'critic', 'queen', 'archivist'],
  fast_draft: ['draft', 'critic', 'queen', 'archivist'],
  critique_only: ['critic', 'archivist'],
  interactive_full: ['scout', 'router', 'draft', 'critic', 'queen', 'archivist'],
  batch_eval: ['scout', 'router', 'draft', 'critic', 'archivist'],
};

interface Props {
  template: string;
  currentStage: string;
  status: string;
  completedStages: string[];
  /** Dynamic node list from API (overrides template-based lookup) */
  templateNodes?: string[];
  /** Whether this template supports loops (overrides template-based lookup) */
  enableLoop?: boolean;
  /** Per-stage durations in ms, displayed under completed nodes */
  stageDurations?: Record<string, number>;
}

type NodeStatus = 'inactive' | 'pending' | 'active' | 'waiting' | 'completed';

function getNodeStatus(
  node: string,
  templateNodes: Set<string>,
  currentStage: string,
  completedStages: Set<string>,
  pipelineStatus: string,
): NodeStatus {
  if (!templateNodes.has(node)) return 'inactive';
  if (completedStages.has(node)) return 'completed';
  if (node === currentStage && pipelineStatus === 'waiting_human') return 'waiting';
  if (node === currentStage && (pipelineStatus === 'running' || pipelineStatus === 'waiting_human')) return 'active';
  return 'pending';
}

function nodeClasses(status: NodeStatus): string {
  const base = 'flex flex-col items-center justify-center px-3 py-2 rounded-xl border-2 transition-all duration-300 min-w-[72px]';
  switch (status) {
    case 'inactive':
      return `${base} border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/30 opacity-40`;
    case 'pending':
      return `${base} border-[#C9C2B8] dark:border-[#4A433C] bg-white dark:bg-gray-800`;
    case 'active':
      return `${base} border-[#C87F4A] dark:border-[#DDA574] bg-[#f9f9ff] dark:bg-[#C87F4A]/15 ring-2 ring-[#C87F4A]/30 animate-pulse`;
    case 'waiting':
      return `${base} border-amber-400 dark:border-amber-500 bg-amber-50 dark:bg-amber-900/20 ring-2 ring-amber-400/50 animate-pulse`;
    case 'completed':
      return `${base} border-[#5F8A50] dark:border-[#87A878] bg-[#5F8A50]/5 dark:bg-[#5F8A50]/10`;
  }
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

function ArrowSvg({ active }: { active: boolean }) {
  return (
    <svg width="24" height="16" viewBox="0 0 24 16" className="shrink-0 mx-0.5">
      <line
        x1="0" y1="8" x2="18" y2="8"
        stroke={active ? '#C87F4A' : '#d1d5db'}
        strokeWidth="2"
        className="dark:stroke-current"
        style={{ color: active ? '#DDA574' : '#4b5563' }}
      />
      <polygon
        points="16,4 24,8 16,12"
        fill={active ? '#C87F4A' : '#d1d5db'}
        className="dark:fill-current"
        style={{ color: active ? '#DDA574' : '#4b5563' }}
      />
    </svg>
  );
}

function LoopArrow() {
  return (
    <svg width="100%" height="24" viewBox="0 0 400 24" preserveAspectRatio="xMidYMid meet" className="mt-1">
      <path
        d="M 320 4 C 340 4, 340 20, 320 20 L 160 20 C 140 20, 140 4, 160 4"
        fill="none"
        stroke="#b45309"
        strokeWidth="1.5"
        strokeDasharray="4 3"
        opacity="0.5"
      />
      <polygon points="160,1 152,4 160,7" fill="#b45309" opacity="0.5" />
      <text x="240" y="18" textAnchor="middle" fill="#b45309" fontSize="8" opacity="0.6">
        rerun loop
      </text>
    </svg>
  );
}

export default function TopologyViewer({
  template,
  currentStage,
  status,
  completedStages,
  templateNodes,
  enableLoop,
  stageDurations,
}: Props) {
  // Use dynamic templateNodes if provided, otherwise fall back to static map
  const activeNodeList = templateNodes ?? TEMPLATE_NODE_MAP[template] ?? TEMPLATE_NODE_MAP.default;
  const activeNodes = useMemo(() => new Set(activeNodeList), [activeNodeList]);
  const completedSet = useMemo(() => new Set(completedStages), [completedStages]);

  // Use dynamic enableLoop if provided, otherwise fall back to static set
  const showLoop = enableLoop ?? LOOP_TEMPLATES.has(template);

  return (
    <div className="w-full">
      <div className="flex items-center justify-center gap-1 overflow-x-auto py-2">
        {ALL_NODES.map((node, idx) => {
          const nodeStatus = getNodeStatus(node, activeNodes, currentStage, completedSet, status);
          const nextNode = ALL_NODES[idx + 1];
          const showArrow = idx < ALL_NODES.length - 1;
          // Arrow is active if this node is completed and next is in template
          const arrowActive = nodeStatus === 'completed' && !!nextNode && activeNodes.has(nextNode);
          const dur = stageDurations?.[node];

          return (
            <div key={node} className="flex items-center">
              <div className={nodeClasses(nodeStatus)}>
                <span className="text-lg leading-none">{NODE_ICONS[node]}</span>
                <span className="text-[10px] font-medium text-gray-700 dark:text-gray-300 mt-0.5">
                  {NODE_LABELS[node]}
                </span>
                {nodeStatus === 'completed' && (
                  <span className="text-[9px] text-[#5F8A50] dark:text-[#87A878]">done</span>
                )}
                {nodeStatus === 'waiting' && (
                  <span className="text-[9px] text-amber-600 dark:text-amber-400 font-medium">HITL</span>
                )}
                {nodeStatus === 'completed' && dur !== undefined && (
                  <span className="text-[8px] font-mono text-gray-400 mt-0.5">{formatDuration(dur)}</span>
                )}
              </div>
              {showArrow && <ArrowSvg active={arrowActive} />}
            </div>
          );
        })}
      </div>
      {showLoop && (
        <div className="px-8">
          <LoopArrow />
        </div>
      )}
    </div>
  );
}
