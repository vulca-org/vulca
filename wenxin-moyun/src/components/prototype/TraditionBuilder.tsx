/**
 * M7.2 Build Mode — visual TRADITION.yaml builder.
 *
 * Weight sliders (auto-normalize), terminology editor, taboo editor,
 * live YAML preview, download button.
 */

import { useState, useMemo, useCallback } from 'react';
import { IOSButton, IOSCard, IOSCardContent } from '../ios';

const L_LEVELS = ['L1', 'L2', 'L3', 'L4', 'L5'] as const;
const L_NAMES: Record<string, string> = {
  L1: 'Visual Perception',
  L2: 'Technical Analysis',
  L3: 'Cultural Context',
  L4: 'Critical Interpretation',
  L5: 'Philosophical Aesthetic',
};
const CATEGORIES = ['technique', 'aesthetics', 'composition', 'philosophy', 'material'] as const;
const SEVERITIES = ['low', 'medium', 'high', 'critical'] as const;
const VARIANTS = ['default', 'chinese_xieyi', 'western_academic'] as const;

interface TermEntry {
  id: string;
  term: string;
  term_zh: string;
  definition: string;
  category: string;
  l_levels: string[];
}

interface TabooEntry {
  id: string;
  rule: string;
  severity: string;
  l_levels: string[];
  explanation: string;
}

function newTerm(): TermEntry {
  return { id: crypto.randomUUID(), term: '', term_zh: '', definition: '', category: 'technique', l_levels: [] };
}

function newTaboo(): TabooEntry {
  return { id: crypto.randomUUID(), rule: '', severity: 'medium', l_levels: [], explanation: '' };
}

export default function TraditionBuilder() {
  const [name, setName] = useState('');
  const [displayEn, setDisplayEn] = useState('');
  const [displayZh, setDisplayZh] = useState('');
  const [displayJa, setDisplayJa] = useState('');
  const [weights, setWeights] = useState<Record<string, number>>({
    L1: 0.20, L2: 0.20, L3: 0.20, L4: 0.20, L5: 0.20,
  });
  const [terms, setTerms] = useState<TermEntry[]>([newTerm()]);
  const [taboos, setTaboos] = useState<TabooEntry[]>([newTaboo()]);
  const [variant, setVariant] = useState<string>('default');
  const [showYaml, setShowYaml] = useState(false);

  const handleWeightChange = useCallback((key: string, value: number) => {
    setWeights(prev => {
      const updated = { ...prev, [key]: value };
      const total = Object.values(updated).reduce((a, b) => a + b, 0);
      if (total < 0.01) return prev;
      // Normalize
      const normalized: Record<string, number> = {};
      for (const k of L_LEVELS) {
        normalized[k] = Math.round((updated[k] / total) * 100) / 100;
      }
      // Fix rounding to exactly 1.0
      const diff = 1.0 - Object.values(normalized).reduce((a, b) => a + b, 0);
      normalized[key] = Math.round((normalized[key] + diff) * 100) / 100;
      return normalized;
    });
  }, []);

  const updateTerm = (id: string, field: keyof TermEntry, value: unknown) => {
    setTerms(prev => prev.map(t => t.id === id ? { ...t, [field]: value } : t));
  };

  const updateTaboo = (id: string, field: keyof TabooEntry, value: unknown) => {
    setTaboos(prev => prev.map(t => t.id === id ? { ...t, [field]: value } : t));
  };

  const toggleLLevel = (id: string, level: string, type: 'term' | 'taboo') => {
    if (type === 'term') {
      setTerms(prev => prev.map(t => {
        if (t.id !== id) return t;
        const ls = t.l_levels.includes(level)
          ? t.l_levels.filter(l => l !== level)
          : [...t.l_levels, level];
        return { ...t, l_levels: ls };
      }));
    } else {
      setTaboos(prev => prev.map(t => {
        if (t.id !== id) return t;
        const ls = t.l_levels.includes(level)
          ? t.l_levels.filter(l => l !== level)
          : [...t.l_levels, level];
        return { ...t, l_levels: ls };
      }));
    }
  };

  // Validation
  const errors = useMemo(() => {
    const errs: string[] = [];
    if (!name) errs.push('Name is required');
    else if (!/^[a-z][a-z0-9_]*$/.test(name)) errs.push('Name must be snake_case');
    if (!displayEn) errs.push('English display name required');
    const wSum = Object.values(weights).reduce((a, b) => a + b, 0);
    if (Math.abs(wSum - 1.0) > 0.02) errs.push(`Weights sum to ${wSum.toFixed(3)}`);
    const validTerms = terms.filter(t => t.term && t.l_levels.length > 0);
    if (validTerms.length < 1) errs.push('At least 1 complete terminology entry');
    const validTaboos = taboos.filter(t => t.rule && t.severity);
    if (validTaboos.length < 1) errs.push('At least 1 taboo rule');
    return errs;
  }, [name, displayEn, weights, terms, taboos]);

  // Generate YAML
  const yamlOutput = useMemo(() => {
    const lines: string[] = [];
    lines.push(`name: ${name || 'your_tradition'}`);
    lines.push(`display_name:`);
    lines.push(`  en: "${displayEn}"`);
    if (displayZh) lines.push(`  zh: "${displayZh}"`);
    if (displayJa) lines.push(`  ja: "${displayJa}"`);
    lines.push('');
    lines.push('weights:');
    for (const l of L_LEVELS) {
      lines.push(`  ${l}: ${weights[l].toFixed(2)}`);
    }
    lines.push('');
    lines.push('terminology:');
    for (const t of terms.filter(t => t.term)) {
      lines.push(`  - term: "${t.term}"`);
      if (t.term_zh) lines.push(`    term_zh: "${t.term_zh}"`);
      lines.push(`    definition:`);
      lines.push(`      en: "${t.definition}"`);
      lines.push(`    category: ${t.category}`);
      lines.push(`    l_levels: [${t.l_levels.join(', ')}]`);
    }
    lines.push('');
    lines.push('taboos:');
    for (const t of taboos.filter(t => t.rule)) {
      lines.push(`  - rule: "${t.rule}"`);
      lines.push(`    severity: ${t.severity}`);
      if (t.l_levels.length > 0) lines.push(`    l_levels: [${t.l_levels.join(', ')}]`);
      if (t.explanation) lines.push(`    explanation: "${t.explanation}"`);
    }
    lines.push('');
    lines.push('pipeline:');
    lines.push(`  variant: ${variant}`);
    return lines.join('\n');
  }, [name, displayEn, displayZh, displayJa, weights, terms, taboos, variant]);

  const downloadYaml = () => {
    const blob = new Blob([yamlOutput], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${name || 'tradition'}.yaml`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4 max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-gray-900 dark:text-white">Tradition Builder</h2>
        <div className="flex gap-2">
          <IOSButton variant="secondary" size="sm" onClick={() => setShowYaml(!showYaml)}>
            {showYaml ? 'Hide YAML' : 'Preview YAML'}
          </IOSButton>
          <IOSButton variant="primary" size="sm" onClick={downloadYaml} disabled={errors.length > 0}>
            Download .yaml
          </IOSButton>
        </div>
      </div>

      {/* Validation Errors */}
      {errors.length > 0 && (
        <div className="rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-3">
          <div className="text-xs font-semibold text-red-700 dark:text-red-300 mb-1">Validation Issues</div>
          {errors.map((e, i) => (
            <div key={i} className="text-xs text-red-600 dark:text-red-400">- {e}</div>
          ))}
        </div>
      )}

      {/* YAML Preview */}
      {showYaml && (
        <IOSCard variant="elevated" padding="md" animate={false}>
          <IOSCardContent>
            <pre className="text-xs font-mono bg-gray-50 dark:bg-gray-900 p-3 rounded-lg overflow-x-auto max-h-80 overflow-y-auto whitespace-pre">
              {yamlOutput}
            </pre>
          </IOSCardContent>
        </IOSCard>
      )}

      {/* Basic Info */}
      <IOSCard variant="elevated" padding="md" animate={false}>
        <IOSCardContent>
          <h3 className="text-sm font-semibold mb-3">Basic Info</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-gray-500 block mb-1">Name (snake_case)</label>
              <input
                type="text"
                value={name}
                onChange={e => setName(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
                placeholder="korean_minhwa"
                className="w-full px-3 py-1.5 text-sm border rounded-lg dark:bg-gray-800 dark:border-gray-700"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 block mb-1">English Name</label>
              <input
                type="text"
                value={displayEn}
                onChange={e => setDisplayEn(e.target.value)}
                placeholder="Korean Folk Painting"
                className="w-full px-3 py-1.5 text-sm border rounded-lg dark:bg-gray-800 dark:border-gray-700"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 block mb-1">Chinese Name (optional)</label>
              <input
                type="text"
                value={displayZh}
                onChange={e => setDisplayZh(e.target.value)}
                className="w-full px-3 py-1.5 text-sm border rounded-lg dark:bg-gray-800 dark:border-gray-700"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 block mb-1">Japanese Name (optional)</label>
              <input
                type="text"
                value={displayJa}
                onChange={e => setDisplayJa(e.target.value)}
                className="w-full px-3 py-1.5 text-sm border rounded-lg dark:bg-gray-800 dark:border-gray-700"
              />
            </div>
          </div>
        </IOSCardContent>
      </IOSCard>

      {/* Weights */}
      <IOSCard variant="elevated" padding="md" animate={false}>
        <IOSCardContent>
          <h3 className="text-sm font-semibold mb-3">L1-L5 Weights (auto-normalized to 1.0)</h3>
          <div className="space-y-3">
            {L_LEVELS.map(l => (
              <div key={l} className="flex items-center gap-3">
                <span className="text-xs font-medium w-32 text-gray-600 dark:text-gray-400">
                  {l} {L_NAMES[l]}
                </span>
                <input
                  type="range"
                  min={0}
                  max={0.5}
                  step={0.01}
                  value={weights[l]}
                  onChange={e => handleWeightChange(l, parseFloat(e.target.value))}
                  className="flex-1 accent-[#C87F4A]"
                />
                <span className="text-xs font-mono w-10 text-right">{weights[l].toFixed(2)}</span>
              </div>
            ))}
          </div>
        </IOSCardContent>
      </IOSCard>

      {/* Terminology */}
      <IOSCard variant="elevated" padding="md" animate={false}>
        <IOSCardContent>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold">Terminology ({terms.length})</h3>
            <IOSButton variant="secondary" size="sm" onClick={() => setTerms(prev => [...prev, newTerm()])}>
              + Add Term
            </IOSButton>
          </div>
          <div className="space-y-3">
            {terms.map((t, idx) => (
              <div key={t.id} className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-gray-400 w-4">#{idx + 1}</span>
                  <input
                    type="text"
                    value={t.term}
                    onChange={e => updateTerm(t.id, 'term', e.target.value)}
                    placeholder="Term (English)"
                    className="flex-1 px-2 py-1 text-xs border rounded dark:bg-gray-700 dark:border-gray-600"
                  />
                  <input
                    type="text"
                    value={t.term_zh}
                    onChange={e => updateTerm(t.id, 'term_zh', e.target.value)}
                    placeholder="中文"
                    className="w-20 px-2 py-1 text-xs border rounded dark:bg-gray-700 dark:border-gray-600"
                  />
                  <select
                    value={t.category}
                    onChange={e => updateTerm(t.id, 'category', e.target.value)}
                    className="px-2 py-1 text-xs border rounded dark:bg-gray-700 dark:border-gray-600"
                  >
                    {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                  <button
                    onClick={() => setTerms(prev => prev.filter(x => x.id !== t.id))}
                    className="text-red-400 hover:text-red-600 text-xs"
                  >
                    ×
                  </button>
                </div>
                <input
                  type="text"
                  value={t.definition}
                  onChange={e => updateTerm(t.id, 'definition', e.target.value)}
                  placeholder="Definition"
                  className="w-full px-2 py-1 text-xs border rounded dark:bg-gray-700 dark:border-gray-600"
                />
                <div className="flex gap-1">
                  {L_LEVELS.map(l => (
                    <button
                      key={l}
                      onClick={() => toggleLLevel(t.id, l, 'term')}
                      className={[
                        'px-2 py-0.5 text-[10px] rounded-full border transition-colors',
                        t.l_levels.includes(l)
                          ? 'bg-[#C87F4A]/10 border-[#C87F4A]/30 text-[#C87F4A] dark:bg-[#C87F4A]/15 dark:border-[#C87F4A] dark:text-[#DDA574]'
                          : 'border-gray-300 text-gray-400 dark:border-gray-600',
                      ].join(' ')}
                    >
                      {l}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </IOSCardContent>
      </IOSCard>

      {/* Taboos */}
      <IOSCard variant="elevated" padding="md" animate={false}>
        <IOSCardContent>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold">Taboos ({taboos.length})</h3>
            <IOSButton variant="secondary" size="sm" onClick={() => setTaboos(prev => [...prev, newTaboo()])}>
              + Add Taboo
            </IOSButton>
          </div>
          <div className="space-y-3">
            {taboos.map((t, idx) => (
              <div key={t.id} className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-gray-400 w-4">#{idx + 1}</span>
                  <input
                    type="text"
                    value={t.rule}
                    onChange={e => updateTaboo(t.id, 'rule', e.target.value)}
                    placeholder="Do not..."
                    className="flex-1 px-2 py-1 text-xs border rounded dark:bg-gray-700 dark:border-gray-600"
                  />
                  <select
                    value={t.severity}
                    onChange={e => updateTaboo(t.id, 'severity', e.target.value)}
                    className="px-2 py-1 text-xs border rounded dark:bg-gray-700 dark:border-gray-600"
                  >
                    {SEVERITIES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                  <button
                    onClick={() => setTaboos(prev => prev.filter(x => x.id !== t.id))}
                    className="text-red-400 hover:text-red-600 text-xs"
                  >
                    ×
                  </button>
                </div>
                <input
                  type="text"
                  value={t.explanation}
                  onChange={e => updateTaboo(t.id, 'explanation', e.target.value)}
                  placeholder="Explanation (why this is problematic)"
                  className="w-full px-2 py-1 text-xs border rounded dark:bg-gray-700 dark:border-gray-600"
                />
                <div className="flex gap-1">
                  {L_LEVELS.map(l => (
                    <button
                      key={l}
                      onClick={() => toggleLLevel(t.id, l, 'taboo')}
                      className={[
                        'px-2 py-0.5 text-[10px] rounded-full border transition-colors',
                        t.l_levels.includes(l)
                          ? 'bg-[#B8923D]/10 border-[#B8923D]/30 text-[#8F7030] dark:bg-[#B8923D]/10 dark:border-[#B8923D]/30 dark:text-[#D4A94E]'
                          : 'border-gray-300 text-gray-400 dark:border-gray-600',
                      ].join(' ')}
                    >
                      {l}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </IOSCardContent>
      </IOSCard>

      {/* Pipeline */}
      <IOSCard variant="elevated" padding="md" animate={false}>
        <IOSCardContent>
          <h3 className="text-sm font-semibold mb-3">Pipeline Variant</h3>
          <div className="flex gap-2">
            {VARIANTS.map(v => (
              <button
                key={v}
                onClick={() => setVariant(v)}
                className={[
                  'px-3 py-1.5 text-xs rounded-lg border transition-colors',
                  variant === v
                    ? 'bg-[#C87F4A]/10 border-[#C87F4A]/30 text-[#C87F4A] dark:bg-[#C87F4A]/15 dark:border-[#C87F4A] dark:text-[#DDA574]'
                    : 'border-gray-300 text-gray-500 hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-800',
                ].join(' ')}
              >
                {v}
              </button>
            ))}
          </div>
        </IOSCardContent>
      </IOSCard>
    </div>
  );
}
