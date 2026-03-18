/**
 * M7.2 Explore Mode — interactive cultural knowledge browser.
 *
 * - Tradition cards with weights, terms, taboos
 * - Cross-tradition terminology search
 * - Weight comparison radar (select 2-3 traditions)
 */

import { useState, useMemo } from 'react';
import { IOSCard, IOSCardContent } from '../ios';

// Static tradition data (loaded from YAML at build time via API, fallback to inline)
interface TraditionInfo {
  name: string;
  displayName: string;
  weights: Record<string, number>;
  terms: { term: string; term_zh: string; l_levels: string[]; category: string; definition: string }[];
  taboos: { rule: string; severity: string }[];
  pipeline: string;
}

const TRADITIONS: TraditionInfo[] = [
  {
    name: 'chinese_xieyi', displayName: 'Chinese Freehand Ink (Xieyi)', pipeline: 'chinese_xieyi',
    weights: { L1: 0.10, L2: 0.15, L3: 0.25, L4: 0.20, L5: 0.30 },
    terms: [
      { term: 'hemp-fiber texture stroke', term_zh: '披麻皴', l_levels: ['L2', 'L3'], category: 'technique', definition: 'Long flowing hemp-like brushstrokes for earth surfaces' },
      { term: 'spirit resonance', term_zh: '气韵生动', l_levels: ['L4', 'L5'], category: 'aesthetics', definition: "Xie He's first principle: living spirit and vitality" },
      { term: 'reserved white space', term_zh: '留白', l_levels: ['L2', 'L3', 'L5'], category: 'composition', definition: 'Deliberate unpainted areas as compositional element' },
      { term: 'intention before brush', term_zh: '意在笔先', l_levels: ['L4', 'L5'], category: 'philosophy', definition: 'Conceptual vision must precede execution' },
      { term: 'splashed ink', term_zh: '泼墨', l_levels: ['L2', 'L4'], category: 'technique', definition: 'Bold spontaneous ink application for atmospheric effects' },
      { term: 'Six Principles', term_zh: '六法论', l_levels: ['L3', 'L4', 'L5'], category: 'aesthetics', definition: "Xie He's foundational evaluation criteria" },
    ],
    taboos: [
      { rule: 'Do not misidentify deliberate xieyi brushwork as technical deficiency', severity: 'high' },
      { rule: 'Do not apply anachronistic standards across historical periods', severity: 'medium' },
    ],
  },
  {
    name: 'chinese_gongbi', displayName: 'Chinese Meticulous (Gongbi)', pipeline: 'default',
    weights: { L1: 0.15, L2: 0.30, L3: 0.25, L4: 0.15, L5: 0.15 },
    terms: [
      { term: 'meticulous heavy-color', term_zh: '工笔重彩', l_levels: ['L2', 'L3'], category: 'technique', definition: 'Precise brushwork with richly layered mineral pigments' },
      { term: 'triple alum nine washes', term_zh: '三矾九染', l_levels: ['L2'], category: 'technique', definition: 'Alum fixative between successive color washes' },
      { term: 'plain line drawing', term_zh: '白描', l_levels: ['L1', 'L2'], category: 'technique', definition: 'Monochrome ink-line technique without color' },
    ],
    taboos: [{ rule: 'Do not equate gongbi precision with lack of creativity', severity: 'medium' }],
  },
  {
    name: 'japanese_traditional', displayName: 'Japanese Traditional', pipeline: 'default',
    weights: { L1: 0.15, L2: 0.20, L3: 0.20, L4: 0.20, L5: 0.25 },
    terms: [
      { term: 'wabi-sabi', term_zh: '侘寂', l_levels: ['L4', 'L5'], category: 'aesthetics', definition: 'Beauty in transience and imperfection' },
      { term: 'ma', term_zh: '间', l_levels: ['L2', 'L3', 'L5'], category: 'composition', definition: 'Void space as active compositional element' },
      { term: 'ukiyo-e', term_zh: '浮世绘', l_levels: ['L2', 'L3'], category: 'technique', definition: 'Woodblock prints of the floating world' },
      { term: 'kintsugi', term_zh: '金継ぎ', l_levels: ['L3', 'L5'], category: 'philosophy', definition: 'Golden repair of broken pottery' },
    ],
    taboos: [
      { rule: 'Do not interpret minimalism or imperfection as lack of skill', severity: 'high' },
      { rule: 'Do not conflate Japanese and Chinese traditions as single category', severity: 'high' },
    ],
  },
  {
    name: 'western_academic', displayName: 'Western Academic', pipeline: 'western_academic',
    weights: { L1: 0.20, L2: 0.25, L3: 0.15, L4: 0.25, L5: 0.15 },
    terms: [
      { term: 'chiaroscuro', term_zh: '明暗对照法', l_levels: ['L1', 'L2'], category: 'technique', definition: 'Strong light-dark contrasts for 3D modeling' },
      { term: 'contrapposto', term_zh: '对立式平衡', l_levels: ['L1', 'L2'], category: 'composition', definition: 'Weight-shifted asymmetric figure pose' },
      { term: 'sfumato', term_zh: '晕涂法', l_levels: ['L2', 'L3'], category: 'technique', definition: 'Subtle tone blending by Leonardo' },
    ],
    taboos: [
      { rule: 'Do not apply Eastern criteria to dismiss Western perspective', severity: 'medium' },
      { rule: 'Avoid Orientalist bias in cross-cultural comparison', severity: 'high' },
    ],
  },
  {
    name: 'islamic_geometric', displayName: 'Islamic Geometric', pipeline: 'default',
    weights: { L1: 0.25, L2: 0.30, L3: 0.20, L4: 0.15, L5: 0.10 },
    terms: [
      { term: 'tessellation', term_zh: '密铺', l_levels: ['L1', 'L2', 'L5'], category: 'composition', definition: 'Plane tiling with no gaps expressing divine order' },
      { term: 'arabesque', term_zh: '蔓藤花纹', l_levels: ['L2', 'L3', 'L5'], category: 'aesthetics', definition: 'Flowing vegetal ornament symbolizing infinite creation' },
      { term: 'muqarnas', term_zh: '蜂窝拱', l_levels: ['L2', 'L3'], category: 'technique', definition: '3D stalactite-like ornamental vaulting' },
    ],
    taboos: [
      { rule: 'Do not characterize geometric abstraction as lacking expression', severity: 'medium' },
      { rule: 'Do not reduce Islamic art to prohibition of figural representation', severity: 'medium' },
    ],
  },
  {
    name: 'watercolor', displayName: 'Watercolor', pipeline: 'default',
    weights: { L1: 0.20, L2: 0.25, L3: 0.15, L4: 0.20, L5: 0.20 },
    terms: [
      { term: 'wet-on-wet', term_zh: '湿画法', l_levels: ['L2'], category: 'technique', definition: 'Wet paint on wet surface for natural blending' },
      { term: 'reserved whites', term_zh: '水彩留白', l_levels: ['L1', 'L2'], category: 'technique', definition: 'Unpainted paper for highlights' },
      { term: 'granulation', term_zh: '色粒效果', l_levels: ['L2'], category: 'technique', definition: 'Textural effect from heavy pigment particles' },
    ],
    taboos: [
      { rule: 'Do not treat deliberate watercolor effects as mistakes', severity: 'medium' },
      { rule: 'Do not evaluate watercolor by oil painting standards', severity: 'medium' },
    ],
  },
  {
    name: 'african_traditional', displayName: 'African Traditional', pipeline: 'default',
    weights: { L1: 0.15, L2: 0.20, L3: 0.30, L4: 0.20, L5: 0.15 },
    terms: [
      { term: 'adinkra', term_zh: '阿丁克拉符号', l_levels: ['L3', 'L4', 'L5'], category: 'aesthetics', definition: 'Akan symbols encoding philosophical concepts' },
      { term: 'kente patterns', term_zh: '肯特布纹样', l_levels: ['L2', 'L3'], category: 'material', definition: 'Symbolic woven strip-cloth patterns from Ghana' },
      { term: 'lost-wax casting', term_zh: '青铜失蜡铸造', l_levels: ['L2', 'L3'], category: 'technique', definition: 'Benin/Ife bronze casting technique' },
    ],
    taboos: [
      { rule: "Do not use colonialist terminology ('primitive', 'tribal')", severity: 'critical' },
      { rule: 'Do not evaluate African proportions by Western anatomical standards', severity: 'high' },
    ],
  },
  {
    name: 'south_asian', displayName: 'South Asian', pipeline: 'default',
    weights: { L1: 0.15, L2: 0.20, L3: 0.25, L4: 0.15, L5: 0.25 },
    terms: [
      { term: 'rasa', term_zh: '拉萨/味', l_levels: ['L4', 'L5'], category: 'aesthetics', definition: 'Emotional flavor evoked through art (navarasa)' },
      { term: 'mandala', term_zh: '曼陀罗', l_levels: ['L3', 'L5'], category: 'composition', definition: 'Sacred geometric cosmic diagram' },
      { term: 'miniature painting', term_zh: '细密画', l_levels: ['L2', 'L3'], category: 'technique', definition: 'Highly detailed small-scale painting traditions' },
    ],
    taboos: [
      { rule: 'Do not interpret religious imagery outside theological context', severity: 'high' },
      { rule: 'Do not judge flat spatial representation as failure to achieve perspective', severity: 'medium' },
    ],
  },
];

const COLORS = ['#334155', '#5F8A50', '#B8923D', '#C87F4A', '#C65D4D', '#6B8E7A'];
const SEVERITY_COLORS: Record<string, string> = {
  critical: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  high: 'bg-[#B8923D]/10 text-[#8F7030] dark:bg-[#B8923D]/10 dark:text-[#D4A94E]',
  medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  low: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400',
};

export default function TraditionExplorer() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selected, setSelected] = useState<string[]>([]);
  const [expandedTradition, setExpandedTradition] = useState<string | null>(null);

  const toggleSelect = (name: string) => {
    setSelected(prev =>
      prev.includes(name)
        ? prev.filter(n => n !== name)
        : prev.length < 3
        ? [...prev, name]
        : prev
    );
  };

  // Cross-tradition search
  const searchResults = useMemo(() => {
    if (!searchQuery.trim()) return [];
    const q = searchQuery.toLowerCase();
    const results: { tradition: string; term: string; term_zh: string; l_levels: string[]; definition: string }[] = [];
    for (const t of TRADITIONS) {
      for (const term of t.terms) {
        if (
          term.term.toLowerCase().includes(q) ||
          term.term_zh.includes(searchQuery) ||
          term.definition.toLowerCase().includes(q)
        ) {
          results.push({ tradition: t.displayName, ...term });
        }
      }
    }
    return results;
  }, [searchQuery]);

  const selectedTraditions = TRADITIONS.filter(t => selected.includes(t.name));

  return (
    <div className="space-y-4 max-w-4xl mx-auto">
      {/* Search Bar */}
      <div className="relative">
        <input
          type="text"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          placeholder="Search terminology across all traditions..."
          className="w-full px-4 py-2.5 text-sm border rounded-xl dark:bg-gray-800 dark:border-gray-700 pl-10"
        />
        <span className="absolute left-3 top-2.5 text-gray-400">🔍</span>
      </div>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <IOSCard variant="elevated" padding="md" animate={false}>
          <IOSCardContent>
            <h3 className="text-sm font-semibold mb-2">
              Found {searchResults.length} term(s) matching "{searchQuery}"
            </h3>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {searchResults.map((r, i) => (
                <div key={i} className="flex items-start gap-2 p-2 rounded-lg bg-gray-50 dark:bg-gray-800">
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#C87F4A]/10 text-[#C87F4A] dark:bg-[#C87F4A]/15 dark:text-[#DDA574] shrink-0">
                    {r.tradition}
                  </span>
                  <div>
                    <div className="text-xs font-medium">{r.term} <span className="text-gray-400">{r.term_zh}</span></div>
                    <div className="text-[11px] text-gray-500">{r.definition}</div>
                    <div className="flex gap-1 mt-1">
                      {r.l_levels.map(l => (
                        <span key={l} className="text-[9px] px-1 py-0.5 rounded bg-gray-200 dark:bg-gray-700">{l}</span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </IOSCardContent>
        </IOSCard>
      )}

      {/* Weight Comparison Radar */}
      {selectedTraditions.length >= 2 && (
        <IOSCard variant="elevated" padding="md" animate={false}>
          <IOSCardContent>
            <h3 className="text-sm font-semibold mb-2">Weight Comparison</h3>
            <div className="flex items-center gap-4 mb-3">
              {selectedTraditions.map((t, i) => (
                <div key={t.name} className="flex items-center gap-1 text-xs">
                  <span className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[i] }} />
                  {t.displayName}
                </div>
              ))}
            </div>
            <ComparisonRadar traditions={selectedTraditions} />
          </IOSCardContent>
        </IOSCard>
      )}

      {/* Instruction */}
      <div className="text-xs text-gray-500 dark:text-gray-400">
        Click tradition cards to select 2-3 for weight comparison. Click header to expand details.
      </div>

      {/* Tradition Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {TRADITIONS.map(t => {
          const isSelected = selected.includes(t.name);
          const isExpanded = expandedTradition === t.name;

          return (
            <IOSCard
              key={t.name}
              variant="elevated"
              padding="sm"
              animate={false}
              className={isSelected ? 'ring-2 ring-[#C87F4A]' : ''}
            >
              <IOSCardContent>
                {/* Header */}
                <div
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => setExpandedTradition(isExpanded ? null : t.name)}
                >
                  <div>
                    <div className="text-sm font-semibold">{t.displayName}</div>
                    <div className="text-[11px] text-gray-500">{t.name} | {t.pipeline}</div>
                  </div>
                  <button
                    onClick={e => { e.stopPropagation(); toggleSelect(t.name); }}
                    className={[
                      'px-2 py-1 text-[10px] rounded-lg border transition-colors',
                      isSelected
                        ? 'bg-[#C87F4A]/10 border-[#C87F4A]/30 text-[#C87F4A] dark:bg-[#C87F4A]/15'
                        : 'border-gray-300 text-gray-400 hover:bg-gray-50 dark:border-gray-600',
                    ].join(' ')}
                  >
                    {isSelected ? 'Selected' : 'Compare'}
                  </button>
                </div>

                {/* Weights mini-bar */}
                <div className="flex gap-0.5 mt-2">
                  {['L1', 'L2', 'L3', 'L4', 'L5'].map(l => (
                    <div
                      key={l}
                      className="h-2 rounded-full bg-[#C87F4A] dark:bg-[#C87F4A]"
                      style={{ width: `${(t.weights[l] || 0) * 100}%`, opacity: 0.3 + (t.weights[l] || 0) }}
                      title={`${l}: ${(t.weights[l] || 0).toFixed(2)}`}
                    />
                  ))}
                </div>

                {/* Expanded details */}
                {isExpanded && (
                  <div className="mt-3 space-y-2">
                    {/* Weights */}
                    <div className="text-[11px] text-gray-600 dark:text-gray-400">
                      {['L1', 'L2', 'L3', 'L4', 'L5'].map(l => (
                        <span key={l} className="mr-2">{l}: {(t.weights[l] || 0).toFixed(2)}</span>
                      ))}
                    </div>

                    {/* Terms */}
                    <div>
                      <div className="text-[10px] font-semibold text-gray-500 mb-1">Terminology ({t.terms.length})</div>
                      {t.terms.map((term, i) => (
                        <div key={i} className="text-[11px] py-0.5">
                          <span className="font-medium">{term.term}</span>
                          <span className="text-gray-400 ml-1">{term.term_zh}</span>
                          <span className="text-gray-400 ml-1">[{term.l_levels.join(',')}]</span>
                        </div>
                      ))}
                    </div>

                    {/* Taboos */}
                    <div>
                      <div className="text-[10px] font-semibold text-gray-500 mb-1">Taboos ({t.taboos.length})</div>
                      {t.taboos.map((taboo, i) => (
                        <div key={i} className="text-[11px] py-0.5 flex items-start gap-1">
                          <span className={`text-[9px] px-1 py-0.5 rounded shrink-0 ${SEVERITY_COLORS[taboo.severity] || ''}`}>
                            {taboo.severity}
                          </span>
                          <span className="text-gray-600 dark:text-gray-400">{taboo.rule}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </IOSCardContent>
            </IOSCard>
          );
        })}
      </div>
    </div>
  );
}

/** Radar chart comparing 2-3 traditions' weights */
function ComparisonRadar({ traditions }: { traditions: TraditionInfo[] }) {
  const dims = ['L1', 'L2', 'L3', 'L4', 'L5'];
  const cx = 130, cy = 130, radius = 100;
  const angleStep = (2 * Math.PI) / dims.length;

  const L_LABELS: Record<string, string> = {
    L1: 'Visual', L2: 'Technical', L3: 'Cultural', L4: 'Critical', L5: 'Philosophical',
  };

  const getPoint = (dimIdx: number, value: number) => {
    const angle = -Math.PI / 2 + dimIdx * angleStep;
    return { x: cx + radius * value * Math.cos(angle), y: cy + radius * value * Math.sin(angle) };
  };

  return (
    <svg viewBox="0 0 260 260" className="w-full max-w-[260px] mx-auto">
      {[0.1, 0.2, 0.3, 0.4, 0.5].map(v => (
        <circle key={v} cx={cx} cy={cy} r={radius * v / 0.5} fill="none" stroke="currentColor" strokeOpacity={0.1} />
      ))}
      {dims.map((dim, i) => {
        const pt = getPoint(i, 1);
        const labelPt = getPoint(i, 1.2);
        return (
          <g key={dim}>
            <line x1={cx} y1={cy} x2={pt.x} y2={pt.y} stroke="currentColor" strokeOpacity={0.1} />
            <text x={labelPt.x} y={labelPt.y} textAnchor="middle" dominantBaseline="middle" className="text-[9px] fill-gray-500">
              {L_LABELS[dim]}
            </text>
          </g>
        );
      })}
      {traditions.map((t, tIdx) => {
        const points = dims.map((dim, i) => {
          const val = (t.weights[dim] || 0) / 0.5; // scale: 0.5 = edge
          const pt = getPoint(i, Math.min(val, 1));
          return `${pt.x},${pt.y}`;
        }).join(' ');
        const color = COLORS[tIdx];
        return (
          <g key={t.name}>
            <polygon points={points} fill={color} fillOpacity={0.15} stroke={color} strokeWidth={2} />
            {dims.map((dim, i) => {
              const val = (t.weights[dim] || 0) / 0.5;
              const pt = getPoint(i, Math.min(val, 1));
              return <circle key={dim} cx={pt.x} cy={pt.y} r={3} fill={color} />;
            })}
          </g>
        );
      })}
    </svg>
  );
}
