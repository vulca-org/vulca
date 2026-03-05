/**
 * NodeParamPanel — slide-out drawer for editing per-node parameters.
 * Renders controls dynamically from AGENT_PARAM_SCHEMA.
 */

import { useMemo } from 'react';
import { IOSToggle, IOSSlider } from '../../ios';
import { AGENT_META, type AgentNodeId } from './types';
import { AGENT_PARAM_SCHEMA, type ParamDef } from './agentParamSchema';
import TraditionWeightGrid from './TraditionWeightGrid';

interface Props {
  nodeId: AgentNodeId | null;
  params: Record<string, Record<string, unknown>>;
  onChange: (nodeId: AgentNodeId, paramId: string, value: unknown) => void;
  onClose: () => void;
}

function getVal<T>(params: Record<string, Record<string, unknown>>, nodeId: string, paramId: string, fallback: T): T {
  return (params[nodeId]?.[paramId] as T) ?? fallback;
}

export default function NodeParamPanel({ nodeId, params, onChange, onClose }: Props) {
  if (!nodeId) return null;

  const schema = AGENT_PARAM_SCHEMA[nodeId];
  const meta = AGENT_META[nodeId];

  // Critic L1-L5 weight sum warning
  const weightSum = useMemo(() => {
    if (nodeId !== 'critic') return null;
    const weights = ['w_l1', 'w_l2', 'w_l3', 'w_l4', 'w_l5'];
    const sum = weights.reduce(
      (acc, wId) => acc + (getVal<number>(params, nodeId, wId, schema.find(p => p.id === wId)?.default as number ?? 0.2)),
      0,
    );
    return sum;
  }, [nodeId, params, schema]);

  if (schema.length === 0) {
    return (
      <div className="absolute right-0 top-0 bottom-0 w-72 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 shadow-lg z-20 overflow-y-auto">
        <Header meta={meta} onClose={onClose} />
        <div className="p-4 text-sm text-gray-500 dark:text-gray-400 text-center">
          No configurable parameters for {meta.label}.
        </div>
      </div>
    );
  }

  return (
    <div className="absolute right-0 top-0 bottom-0 w-72 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 shadow-lg z-20 overflow-y-auto">
      <Header meta={meta} onClose={onClose} />

      <div className="p-3 space-y-4">
        {schema.map((def) => (
          <ParamControl
            key={def.id}
            def={def}
            value={getVal(params, nodeId, def.id, def.default)}
            onChange={(val) => onChange(nodeId, def.id, val)}
          />
        ))}

        {/* Weight sum warning for Critic */}
        {weightSum !== null && Math.abs(weightSum - 1.0) > 0.01 && (
          <div className="rounded-lg border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/10 p-2 text-[11px] text-amber-700 dark:text-amber-300">
            L1-L5 weights sum to {weightSum.toFixed(2)} (expected 1.00)
          </div>
        )}

        {/* Tradition weight reference heatmap for Critic */}
        {nodeId === 'critic' && <TraditionWeightGrid />}
      </div>
    </div>
  );
}

function Header({ meta, onClose }: { meta: { label: string; icon: string; description: string }; onClose: () => void }) {
  return (
    <div className="flex items-center justify-between px-3 py-2 border-b border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-2">
        <span className="text-lg">{meta.icon}</span>
        <div>
          <div className="text-sm font-semibold text-gray-900 dark:text-white">{meta.label}</div>
          <div className="text-[10px] text-gray-500 dark:text-gray-400">{meta.description}</div>
        </div>
      </div>
      <button
        onClick={onClose}
        className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 text-lg leading-none"
      >
        &times;
      </button>
    </div>
  );
}

function ParamControl({
  def,
  value,
  onChange,
}: {
  def: ParamDef;
  value: unknown;
  onChange: (val: unknown) => void;
}) {
  switch (def.type) {
    case 'toggle':
      return (
        <IOSToggle
          checked={value as boolean}
          onChange={(v: boolean) => onChange(v)}
          label={def.label}
          description={def.description}
          size="sm"
        />
      );

    case 'slider':
      return (
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs font-medium text-gray-700 dark:text-gray-300">{def.label}</label>
            <span className="text-xs font-mono text-gray-500">{String(value)}</span>
          </div>
          {def.description && (
            <p className="text-[10px] text-gray-400 mb-1">{def.description}</p>
          )}
          <IOSSlider
            value={value as number}
            onChange={(v: number) => onChange(v)}
            min={def.min ?? 0}
            max={def.max ?? 1}
            step={def.step ?? 0.01}
            showValue={false}
            size="sm"
          />
        </div>
      );

    case 'number':
      return (
        <div>
          <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
            {def.label}
          </label>
          {def.description && (
            <p className="text-[10px] text-gray-400 mb-1">{def.description}</p>
          )}
          <input
            type="number"
            value={value as number}
            onChange={(e) => onChange(Number(e.target.value))}
            min={def.min}
            max={def.max}
            step={def.step ?? 1}
            className="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
          />
        </div>
      );

    case 'select':
      return (
        <div>
          <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
            {def.label}
          </label>
          {def.description && (
            <p className="text-[10px] text-gray-400 mb-1">{def.description}</p>
          )}
          <select
            value={value as string}
            onChange={(e) => onChange(e.target.value)}
            className="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
          >
            {def.options?.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      );

    default:
      return null;
  }
}
