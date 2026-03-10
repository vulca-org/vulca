/**
 * Run configuration form for creating new pipeline runs.
 *
 * Features:
 * - Template-driven field visibility (e.g. fast_draft hides max_rounds)
 * - Cultural preset buttons for one-click form fill
 * - TemplateSelector always visible (not gated on Graph Mode)
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { API_PREFIX } from '../../config/api';
import TemplateSelector from './TemplateSelector';
import MediaTypeSelector from './MediaTypeSelector';

// Static fallback traditions (used when API is unavailable)
const STATIC_TRADITIONS = [
  'default', 'chinese_xieyi', 'chinese_gongbi', 'western_academic',
  'islamic_geometric', 'japanese_traditional', 'watercolor',
  'african_traditional', 'south_asian',
];

/** Convert snake_case tradition key to human-readable label */
function traditionLabel(key: string): string {
  return key
    .split('_')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

// --- Template-driven field config ---
interface FieldConfig {
  hideMaxRounds?: boolean;
  hideHitl?: boolean;
  hideSubject?: boolean;
  autoHitl?: boolean;
  subjectMultiline?: boolean;
}

const TEMPLATE_FIELD_CONFIG: Record<string, FieldConfig> = {
  fast_draft: { hideMaxRounds: true, hideHitl: true },
  critique_only: { hideSubject: true },
  interactive_full: { autoHitl: true },
  batch_eval: { subjectMultiline: true },
};

// --- Cultural presets ---
interface Preset {
  label: string;
  subject: string;
  tradition: string;
}

const PRESETS: Preset[] = [
  { label: '水墨山水', subject: 'Misty mountain landscape with pine trees and a winding river', tradition: 'chinese_xieyi' },
  { label: '工笔花鸟', subject: 'Meticulous peony and crane in traditional mineral pigments', tradition: 'chinese_gongbi' },
  { label: 'Ukiyo-e Wave', subject: 'Great wave crashing against rocky shore under moonlight', tradition: 'default' },
  { label: 'Persian Garden', subject: 'Walled paradise garden with flowing water channels and cypress trees', tradition: 'islamic_geometric' },
  { label: 'African Mask', subject: 'Ceremonial mask with bold geometric patterns and spiritual symbols', tradition: 'african_traditional' },
  { label: 'Miniature Court', subject: 'Royal court scene with detailed figures and gold leaf ornaments', tradition: 'south_asian' },
];

// --- Tradition Combobox (Phase 3.1: free-text + suggestions) ---

function TraditionCombobox({
  value,
  onChange,
  traditions,
  emergedConcepts,
  disabled,
}: {
  value: string;
  onChange: (v: string) => void;
  traditions: string[];
  emergedConcepts: Array<{ name: string; description: string }>;
  disabled?: boolean;
}) {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // Build unified suggestion list
  const allItems = [
    ...traditions.map(t => ({ key: t, label: traditionLabel(t), type: 'tradition' as const })),
    ...emergedConcepts.map(c => ({ key: c.name, label: c.name, type: 'emerged' as const, desc: c.description })),
  ];

  const filtered = query
    ? allItems.filter(item =>
        item.label.toLowerCase().includes(query.toLowerCase()) ||
        item.key.toLowerCase().includes(query.toLowerCase())
      )
    : allItems;

  const handleSelect = (key: string) => {
    onChange(key);
    setQuery('');
    setOpen(false);
  };

  return (
    <div ref={ref} className="relative">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        Tradition
      </label>
      <input
        type="text"
        value={open ? query : traditionLabel(value)}
        onChange={e => { setQuery(e.target.value); setOpen(true); }}
        onFocus={() => { setQuery(''); setOpen(true); }}
        placeholder="Type to search or enter custom..."
        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
        disabled={disabled}
      />
      {open && filtered.length > 0 && (
        <ul className="absolute z-50 mt-1 w-full max-h-60 overflow-auto rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 shadow-lg">
          {filtered.map(item => (
            <li
              key={item.key}
              onClick={() => handleSelect(item.key)}
              className={`px-3 py-2 cursor-pointer hover:bg-[#FAF7F2] dark:hover:bg-gray-700 text-sm ${
                item.key === value ? 'bg-[#FAF7F2] dark:bg-gray-700 font-medium' : ''
              }`}
            >
              <span className="text-gray-900 dark:text-gray-100">{item.label}</span>
              {item.type === 'emerged' && (
                <span className="ml-2 text-xs text-[#C87F4A] dark:text-[#DDA574]">emerged</span>
              )}
              {'desc' in item && item.desc && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 truncate">{item.desc}</p>
              )}
            </li>
          ))}
        </ul>
      )}
      {open && query && !filtered.some(f => f.key === query) && (
        <ul className="absolute z-50 mt-1 w-full rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 shadow-lg">
          <li
            onClick={() => handleSelect(query.toLowerCase().replace(/\s+/g, '_'))}
            className="px-3 py-2 cursor-pointer hover:bg-[#FAF7F2] dark:hover:bg-gray-700 text-sm"
          >
            <span className="text-gray-900 dark:text-gray-100">Use &ldquo;{query}&rdquo;</span>
            <span className="ml-2 text-xs text-[#5F8A50]">custom</span>
          </li>
        </ul>
      )}
    </div>
  );
}

export interface RunConfigParams {
  subject: string;
  tradition: string;
  intent: string;
  provider: string;
  n_candidates: number;
  max_rounds: number;
  enable_hitl: boolean;
  enable_agent_critic: boolean;
  enable_parallel_critic: boolean;
  use_graph: boolean;
  template: string;
  media_type: string;
}

interface Props {
  onSubmit: (params: RunConfigParams) => void;
  disabled?: boolean;
  /** Pre-fill form with values from a previous run (for "adjust and rerun"). */
  initialValues?: Partial<RunConfigParams>;
}

export default function RunConfigForm({ onSubmit, disabled, initialValues }: Props) {
  const [subject, setSubject] = useState('');
  const [tradition, setTradition] = useState('chinese_xieyi');
  const [culturalIntent, setCulturalIntent] = useState('');
  const [provider, setProvider] = useState('mock');
  const [nCandidates, setNCandidates] = useState(4);
  const [maxRounds, setMaxRounds] = useState(3);
  const [enableHitl, setEnableHitl] = useState(false);
  const [enableAgentCritic, setEnableAgentCritic] = useState(false);
  const [useGraph, setUseGraph] = useState(false);
  const [enableParallelCritic, setEnableParallelCritic] = useState(true);
  const [template, setTemplate] = useState('default');
  const [mediaType, setMediaType] = useState('image');

  // Dynamic tradition list (falls back to STATIC_TRADITIONS)
  const [traditions, setTraditions] = useState<string[]>(STATIC_TRADITIONS);
  // Emerged cultural concepts from the digestion system
  const [emergedConcepts, setEmergedConcepts] = useState<Array<{ name: string; description: string }>>([]);

  // Load dynamic traditions + emerged concepts on mount
  useEffect(() => {
    // Load traditions from knowledge-base API
    fetch(`${API_PREFIX}/knowledge-base`)
      .then(res => (res.ok ? res.json() : null))
      .then(data => {
        if (data?.traditions) {
          const names = data.traditions.map((t: { tradition: string }) => t.tradition);
          if (names.length > 0) setTraditions(names);
        }
      })
      .catch(() => {}); // Silently fall back to static

    // Load emerged concepts from digestion system
    fetch(`${API_PREFIX}/digestion/status`)
      .then(res => (res.ok ? res.json() : null))
      .then(data => {
        if (data?.cultures) {
          const concepts = (Object.values(data.cultures) as Record<string, unknown>[]).map((c) => ({
            name: (c.name as string) || '',
            description: (c.description as string) || '',
          }));
          setEmergedConcepts(concepts);
        }
      })
      .catch(() => {});
  }, []);

  // Apply initialValues when they change (e.g. after "adjust and rerun")
  useEffect(() => {
    if (!initialValues) return;
    if (initialValues.subject !== undefined) setSubject(initialValues.subject);
    if (initialValues.tradition !== undefined) setTradition(initialValues.tradition);
    if (initialValues.intent !== undefined) setCulturalIntent(initialValues.intent);
    if (initialValues.provider !== undefined) setProvider(initialValues.provider);
    if (initialValues.n_candidates !== undefined) setNCandidates(initialValues.n_candidates);
    if (initialValues.max_rounds !== undefined) setMaxRounds(initialValues.max_rounds);
    if (initialValues.enable_hitl !== undefined) setEnableHitl(initialValues.enable_hitl);
    if (initialValues.enable_agent_critic !== undefined) setEnableAgentCritic(initialValues.enable_agent_critic);
    if (initialValues.enable_parallel_critic !== undefined) setEnableParallelCritic(initialValues.enable_parallel_critic);
    if (initialValues.use_graph !== undefined) setUseGraph(initialValues.use_graph);
    if (initialValues.template !== undefined) setTemplate(initialValues.template);
    if (initialValues.media_type !== undefined) setMediaType(initialValues.media_type);
  }, [initialValues]);

  // Derive field config from current template
  const fieldCfg = TEMPLATE_FIELD_CONFIG[template] || {};

  // Template data callback: auto-apply HITL if template demands it
  const handleTemplateData = useCallback((data: { value: string } | undefined) => {
    if (!data) return;
    const cfg = TEMPLATE_FIELD_CONFIG[data.value];
    if (cfg?.autoHitl) setEnableHitl(true);
  }, []);

  // Preset click handler
  const applyPreset = (p: Preset) => {
    setSubject(p.subject);
    setTradition(p.tradition);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!subject.trim() && !fieldCfg.hideSubject) return;
    onSubmit({
      subject: subject.trim(),
      tradition,
      intent: culturalIntent.trim(),
      provider,
      n_candidates: nCandidates,
      max_rounds: maxRounds,
      enable_hitl: enableHitl,
      enable_agent_critic: enableAgentCritic,
      enable_parallel_critic: enableParallelCritic,
      use_graph: useGraph,
      template,
      media_type: mediaType,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Preset buttons */}
      <div className="flex flex-wrap gap-2">
        {PRESETS.map(p => (
          <button
            key={p.label}
            type="button"
            onClick={() => applyPreset(p)}
            disabled={disabled}
            className="px-3 py-1.5 text-xs font-medium rounded-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 transition-colors"
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Media Type */}
      <MediaTypeSelector
        value={mediaType}
        onChange={setMediaType}
        disabled={disabled}
      />

      {/* Subject */}
      {!fieldCfg.hideSubject && (
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Subject
          </label>
          <textarea
            value={subject}
            onChange={e => setSubject(e.target.value)}
            placeholder="e.g., Dong Yuan landscape with hemp-fiber texture strokes"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#C87F4A] focus:border-transparent resize-none"
            rows={fieldCfg.subjectMultiline ? 4 : 2}
            disabled={disabled}
          />
        </div>
      )}

      {/* Cultural Intent (free text) */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Cultural Intent <span className="text-xs text-gray-400 font-normal">(optional)</span>
        </label>
        <input
          type="text"
          value={culturalIntent}
          onChange={e => setCulturalIntent(e.target.value)}
          placeholder="Describe your cultural vision freely, e.g. 'wabi-sabi minimalism meets Bauhaus'"
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#C87F4A] focus:border-transparent"
          disabled={disabled}
        />
      </div>

      {/* Emerged cultural concepts (clickable tags) */}
      {emergedConcepts.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Emerged Concepts
          </label>
          <div className="flex flex-wrap gap-2">
            {emergedConcepts.map(c => (
              <button
                key={c.name}
                type="button"
                onClick={() => setCulturalIntent(c.name)}
                title={c.description}
                disabled={disabled}
                className="px-3 py-1 text-xs font-medium rounded-full border border-[#C87F4A]/30 dark:border-[#DDA574]/30 bg-[#C87F4A]/10 dark:bg-[#C87F4A]/15 text-[#C87F4A] dark:text-[#DDA574] hover:bg-[#C87F4A]/15 dark:hover:bg-[#C87F4A]/25 disabled:opacity-50 transition-colors"
              >
                {c.name}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <TemplateSelector
          value={template}
          onChange={setTemplate}
          onTemplateData={handleTemplateData}
          disabled={disabled}
        />
        <TraditionCombobox
          value={tradition}
          onChange={setTradition}
          traditions={traditions}
          emergedConcepts={emergedConcepts}
          disabled={disabled}
        />

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Provider
          </label>
          <select
            value={provider}
            onChange={e => setProvider(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            disabled={disabled}
          >
            <option value="mock">Mock (instant, free)</option>
            <option value="nb2">NB2 / Gemini Image ($0.067/img)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Candidates
          </label>
          <input
            type="number"
            value={nCandidates}
            onChange={e => setNCandidates(Number(e.target.value))}
            min={1} max={8}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            disabled={disabled}
          />
        </div>

        {!fieldCfg.hideMaxRounds && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Max Rounds
            </label>
            <input
              type="number"
              value={maxRounds}
              onChange={e => setMaxRounds(Number(e.target.value))}
              min={1} max={5}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              disabled={disabled}
            />
          </div>
        )}
      </div>

      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-6">
          <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
            <input
              type="checkbox"
              checked={enableAgentCritic}
              onChange={e => setEnableAgentCritic(e.target.checked)}
              className="rounded border-gray-300 dark:border-gray-600"
              disabled={disabled}
            />
            <span>
              Agent Critic (LLM)
              <span className="ml-1 text-xs text-gray-400">uses Gemini for scoring + FixItPlan</span>
            </span>
          </label>
          {!fieldCfg.hideHitl && (
            <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
              <input
                type="checkbox"
                checked={enableHitl}
                onChange={e => setEnableHitl(e.target.checked)}
                className="rounded border-gray-300 dark:border-gray-600"
                disabled={disabled}
              />
              Human-in-the-Loop
            </label>
          )}
          <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
            <input
              type="checkbox"
              checked={enableParallelCritic}
              onChange={e => setEnableParallelCritic(e.target.checked)}
              className="rounded border-gray-300 dark:border-gray-600"
              disabled={disabled || useGraph}
            />
            <span>
              Parallel Critic
              <span className="ml-1 text-xs text-gray-400">5x faster L1-L5</span>
            </span>
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
            <input
              type="checkbox"
              checked={useGraph}
              onChange={e => setUseGraph(e.target.checked)}
              className="rounded border-gray-300 dark:border-gray-600"
              disabled={disabled}
            />
            <span>
              Graph Mode
              <span className="ml-1 text-xs text-gray-400">LangGraph pipeline</span>
            </span>
          </label>
        </div>

        <button
          type="submit"
          disabled={disabled || (!subject.trim() && !fieldCfg.hideSubject)}
          className="px-6 py-2.5 bg-[#C87F4A] text-white rounded-lg font-medium hover:bg-[#A85D3B] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {disabled ? 'Running...' : 'Run Pipeline'}
        </button>
      </div>
    </form>
  );
}
