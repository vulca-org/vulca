/**
 * Run configuration form for creating new pipeline runs.
 */

import { useState } from 'react';

const TRADITIONS = [
  { value: 'chinese_xieyi', label: 'Chinese Xieyi' },
  { value: 'chinese_gongbi', label: 'Chinese Gongbi' },
  { value: 'chinese_guohua', label: 'Chinese Guohua' },
  { value: 'western_academic', label: 'Western Academic' },
  { value: 'islamic_geometric', label: 'Islamic Geometric' },
  { value: 'watercolor', label: 'Watercolor' },
  { value: 'african_traditional', label: 'African Traditional' },
  { value: 'south_asian', label: 'South Asian' },
  { value: 'default', label: 'Default' },
];

interface Props {
  onSubmit: (params: {
    subject: string;
    tradition: string;
    provider: string;
    n_candidates: number;
    max_rounds: number;
    enable_hitl: boolean;
    enable_agent_critic: boolean;
  }) => void;
  disabled?: boolean;
}

export default function RunConfigForm({ onSubmit, disabled }: Props) {
  const [subject, setSubject] = useState('');
  const [tradition, setTradition] = useState('chinese_xieyi');
  const [provider, setProvider] = useState('mock');
  const [nCandidates, setNCandidates] = useState(4);
  const [maxRounds, setMaxRounds] = useState(3);
  const [enableHitl, setEnableHitl] = useState(false);
  const [enableAgentCritic, setEnableAgentCritic] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!subject.trim()) return;
    onSubmit({
      subject: subject.trim(),
      tradition,
      provider,
      n_candidates: nCandidates,
      max_rounds: maxRounds,
      enable_hitl: enableHitl,
      enable_agent_critic: enableAgentCritic,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Subject
        </label>
        <textarea
          value={subject}
          onChange={e => setSubject(e.target.value)}
          placeholder="e.g., Dong Yuan landscape with hemp-fiber texture strokes"
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          rows={2}
          disabled={disabled}
        />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Tradition
          </label>
          <select
            value={tradition}
            onChange={e => setTradition(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            disabled={disabled}
          >
            {TRADITIONS.map(t => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>

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
            <option value="mock">Mock (instant)</option>
            <option value="together_flux">FLUX ($0.003/img)</option>
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
              <span className="ml-1 text-xs text-gray-400">uses DeepSeek for scoring + FixItPlan</span>
            </span>
          </label>
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
        </div>

        <button
          type="submit"
          disabled={disabled || !subject.trim()}
          className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {disabled ? 'Running...' : 'Run Pipeline'}
        </button>
      </div>
    </form>
  );
}
