/**
 * Template selector for choosing pipeline graph topology.
 *
 * Fetches templates from the backend API with hardcoded fallback.
 */

import { useEffect, useRef, useState } from 'react';
import { API_PREFIX } from '../../config/api';

interface TemplateOption {
  value: string;
  label: string;
  desc: string;
  nodes?: string[];
  enableLoop?: boolean;
  parallelCritic?: boolean;
}

const FALLBACK_TEMPLATES: TemplateOption[] = [
  { value: 'default', label: 'Standard Pipeline', desc: 'Scout → Draft → Critic → Queen with loop' },
  { value: 'fast_draft', label: 'Fast Draft', desc: 'Skip Scout, jump to generation' },
  { value: 'critique_only', label: 'Critique Only', desc: 'Evaluate existing image only' },
  { value: 'interactive_full', label: 'Interactive (HITL)', desc: 'All stages with human review + parallel scoring' },
  { value: 'batch_eval', label: 'Batch Evaluation', desc: 'Single-pass, no loop' },
];

interface Props {
  value: string;
  onChange: (template: string) => void;
  onTemplateData?: (data: TemplateOption | undefined) => void;
  disabled?: boolean;
}

export default function TemplateSelector({ value, onChange, onTemplateData, disabled }: Props) {
  const [templates, setTemplates] = useState<TemplateOption[]>(FALLBACK_TEMPLATES);

  useEffect(() => {
    fetch(`${API_PREFIX}/prototype/templates`)
      .then(res => res.json())
      .then((data: Array<{ name: string; display_name: string; description: string; nodes: string[]; enable_loop: boolean; parallel_critic: boolean }>) => {
        const mapped = data.map(t => ({
          value: t.name,
          label: t.display_name,
          desc: t.description,
          nodes: t.nodes,
          enableLoop: t.enable_loop,
          parallelCritic: t.parallel_critic,
        }));
        if (mapped.length > 0) setTemplates(mapped);
      })
      .catch(() => {}); // fallback to hardcoded
  }, []);

  const selected = templates.find(t => t.value === value);

  // Use ref to avoid infinite loops when onTemplateData is an unstable reference
  const onTemplateDataRef = useRef(onTemplateData);
  onTemplateDataRef.current = onTemplateData;

  useEffect(() => {
    onTemplateDataRef.current?.(selected);
  }, [selected]);

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        Template
      </label>
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
        disabled={disabled}
      >
        {templates.map(t => (
          <option key={t.value} value={t.value}>{t.label}</option>
        ))}
      </select>
      {selected && (
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          {selected.desc}
        </p>
      )}
    </div>
  );
}
