import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Search, BookOpen, AlertTriangle, Globe2, ChevronDown, ChevronRight, Sparkles } from 'lucide-react';
import {
  IOSButton,
  IOSCard,
  IOSCardContent,
  IOSCardGrid,
} from '../components/ios';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface TermEntry {
  term_en: string;
  term_zh: string;
  definition: string;
  category: string;
  l_levels: string[];
}

interface TabooRule {
  description: string;
  severity: string;
}

interface TraditionData {
  display_name: string;
  terms: TermEntry[];
  taboo_rules: TabooRule[];
  weights: Record<string, number>;
  pipeline_variant: string;
}

interface KnowledgeBaseData {
  traditions: Record<string, TraditionData>;
  stats: { total_terms: number; total_taboos: number; total_traditions: number };
}

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

const MOCK_DATA: KnowledgeBaseData = {
  traditions: {
    chinese_ink: {
      display_name: 'Chinese Ink Painting',
      pipeline_variant: 'ink_wash_pipeline',
      weights: { L1: 0.15, L2: 0.15, L3: 0.25, L4: 0.15, L5: 0.30 },
      terms: [
        { term_en: 'Xieyi', term_zh: '\u5199\u610F', definition: 'Freehand brushwork emphasizing spiritual resonance over physical likeness', category: 'Technique', l_levels: ['L3', 'L5'] },
        { term_en: 'Liu Bai', term_zh: '\u7559\u767D', definition: 'Intentional blank space conveying emptiness and depth', category: 'Composition', l_levels: ['L2', 'L3'] },
        { term_en: 'Mo Fen Wu Se', term_zh: '\u58A8\u5206\u4E94\u8272', definition: 'Five tonal values from a single ink — dry, wet, thick, light, charred', category: 'Material', l_levels: ['L1', 'L3'] },
        { term_en: 'Qi Yun Sheng Dong', term_zh: '\u6C14\u97F5\u751F\u52A8', definition: 'Spirit consonance giving life to painting (Xie He\'s first principle)', category: 'Aesthetics', l_levels: ['L5'] },
        { term_en: 'Cun Fa', term_zh: '\u7693\u6CD5', definition: 'Textural stroke methods for depicting rocks and mountains', category: 'Technique', l_levels: ['L1', 'L3'] },
      ],
      taboo_rules: [
        { description: 'Avoid saturated colors that conflict with ink wash aesthetics', severity: 'high' },
        { description: 'Do not fill all negative space — Liu Bai is essential', severity: 'critical' },
        { description: 'Avoid photorealistic rendering style', severity: 'medium' },
      ],
    },
    japanese_ukiyoe: {
      display_name: 'Japanese Ukiyo-e',
      pipeline_variant: 'ukiyoe_pipeline',
      weights: { L1: 0.20, L2: 0.20, L3: 0.20, L4: 0.15, L5: 0.25 },
      terms: [
        { term_en: 'Bokashi', term_zh: '\u6F38\u8B8A\u6478', definition: 'Gradation printing technique for color transitions', category: 'Technique', l_levels: ['L1'] },
        { term_en: 'Kento', term_zh: '\u898B\u5F53', definition: 'Registration marks for precise multi-block color alignment', category: 'Technique', l_levels: ['L1'] },
        { term_en: 'Bijin-ga', term_zh: '\u7F8E\u4EBA\u753B', definition: 'Genre of paintings depicting beautiful women', category: 'Genre', l_levels: ['L3', 'L5'] },
        { term_en: 'Nishiki-e', term_zh: '\u9326\u7D75', definition: 'Full-color woodblock prints using multiple blocks', category: 'Technique', l_levels: ['L1', 'L3'] },
      ],
      taboo_rules: [
        { description: 'Avoid 3D perspective — maintain flat compositional style', severity: 'high' },
        { description: 'Do not use oil-painting texture in Ukiyo-e context', severity: 'medium' },
      ],
    },
    persian_miniature: {
      display_name: 'Persian Miniature',
      pipeline_variant: 'persian_miniature_pipeline',
      weights: { L1: 0.20, L2: 0.15, L3: 0.25, L4: 0.20, L5: 0.20 },
      terms: [
        { term_en: 'Naqqashi', term_zh: '\u7EB3\u5361\u4EC0', definition: 'The art of miniature painting and fine brushwork', category: 'Technique', l_levels: ['L1', 'L3'] },
        { term_en: 'Tazhib', term_zh: '\u6CF0\u5FB7\u5E0C\u5E03', definition: 'Illumination and gilding in manuscript borders', category: 'Decoration', l_levels: ['L1', 'L3'] },
        { term_en: 'Shamseh', term_zh: '\u592A\u9633\u7EB9', definition: 'Radial sun-burst motif used as central medallion', category: 'Motif', l_levels: ['L3', 'L5'] },
      ],
      taboo_rules: [
        { description: 'Avoid depicting shadow and Western chiaroscuro', severity: 'high' },
        { description: 'Figurative representations must respect Islamic art context', severity: 'critical' },
      ],
    },
    indian_mughal: {
      display_name: 'Indian Mughal Painting',
      pipeline_variant: 'mughal_pipeline',
      weights: { L1: 0.20, L2: 0.20, L3: 0.20, L4: 0.20, L5: 0.20 },
      terms: [
        { term_en: 'Ragamala', term_zh: '\u62C9\u683C\u9A6C\u62C9', definition: 'Paintings depicting musical modes as visual narratives', category: 'Genre', l_levels: ['L3', 'L5'] },
        { term_en: 'Nasta\'liq', term_zh: '\u7EB3\u65AF\u5854\u5229\u514B', definition: 'Calligraphic script style used in manuscript margins', category: 'Calligraphy', l_levels: ['L1', 'L4'] },
        { term_en: 'Pardaz', term_zh: '\u5E15\u8FBE\u5179', definition: 'Fine detailed finishing technique in Mughal miniatures', category: 'Technique', l_levels: ['L1'] },
      ],
      taboo_rules: [
        { description: 'Respect iconographic traditions in religious scenes', severity: 'critical' },
        { description: 'Avoid anachronistic modern elements in court scenes', severity: 'medium' },
      ],
    },
    korean_minhwa: {
      display_name: 'Korean Minhwa',
      pipeline_variant: 'minhwa_pipeline',
      weights: { L1: 0.15, L2: 0.15, L3: 0.25, L4: 0.15, L5: 0.30 },
      terms: [
        { term_en: 'Chaekgeori', term_zh: '\u518C\u67B6\u56FE', definition: 'Still-life paintings of books and scholarly objects', category: 'Genre', l_levels: ['L3', 'L5'] },
        { term_en: 'Sipjangsaeng', term_zh: '\u5341\u957F\u751F', definition: 'Ten symbols of longevity motif system', category: 'Motif', l_levels: ['L3', 'L5'] },
        { term_en: 'Minhwa Style', term_zh: '\u6C11\u753B\u98CE\u683C', definition: 'Folk painting with bold colors and flat perspective', category: 'Style', l_levels: ['L1', 'L3'] },
      ],
      taboo_rules: [
        { description: 'Avoid mixing Minhwa motifs with Japanese visual elements', severity: 'high' },
        { description: 'Symbolic animals must maintain traditional associations', severity: 'medium' },
      ],
    },
    thai_traditional: {
      display_name: 'Thai Traditional Art',
      pipeline_variant: 'thai_pipeline',
      weights: { L1: 0.20, L2: 0.15, L3: 0.25, L4: 0.20, L5: 0.20 },
      terms: [
        { term_en: 'Lai Thai', term_zh: '\u6CF0\u5F0F\u82B1\u7EB9', definition: 'Traditional Thai ornamental patterns', category: 'Motif', l_levels: ['L1', 'L3'] },
        { term_en: 'Kranok', term_zh: '\u514B\u62C9\u8BFA\u514B', definition: 'Flame-like decorative motif in Thai art', category: 'Motif', l_levels: ['L3', 'L5'] },
      ],
      taboo_rules: [
        { description: 'Sacred Buddhist imagery must be treated with respect', severity: 'critical' },
        { description: 'Avoid placing Buddha figures in decorative/trivial contexts', severity: 'critical' },
      ],
    },
    byzantine_icon: {
      display_name: 'Byzantine Icon Art',
      pipeline_variant: 'byzantine_pipeline',
      weights: { L1: 0.15, L2: 0.20, L3: 0.20, L4: 0.25, L5: 0.20 },
      terms: [
        { term_en: 'Mandorla', term_zh: '\u5149\u8F6E', definition: 'Almond-shaped aureole surrounding holy figures', category: 'Iconography', l_levels: ['L3', 'L4'] },
        { term_en: 'Theotokos', term_zh: '\u5723\u6BCD\u50CF', definition: 'Iconographic type of the Virgin Mary with Christ child', category: 'Iconography', l_levels: ['L4', 'L5'] },
        { term_en: 'Gold Ground', term_zh: '\u91D1\u5E95', definition: 'Gold leaf background symbolizing divine light', category: 'Material', l_levels: ['L1', 'L5'] },
      ],
      taboo_rules: [
        { description: 'Do not alter canonical proportions of sacred figures', severity: 'critical' },
        { description: 'Avoid realistic shadow — use flat, divine illumination', severity: 'high' },
      ],
    },
    islamic_geometric: {
      display_name: 'Islamic Geometric Art',
      pipeline_variant: 'islamic_geo_pipeline',
      weights: { L1: 0.25, L2: 0.25, L3: 0.20, L4: 0.15, L5: 0.15 },
      terms: [
        { term_en: 'Girih', term_zh: '\u51E0\u4F55\u8774\u8776\u7EB9', definition: 'Set of five tile shapes forming complex tessellations', category: 'Pattern', l_levels: ['L1', 'L3'] },
        { term_en: 'Arabesque', term_zh: '\u963F\u62C9\u4F2F\u82B1\u7EB9', definition: 'Flowing vegetal scrollwork based on rhythmic linear patterns', category: 'Motif', l_levels: ['L1', 'L3'] },
        { term_en: 'Muqarnas', term_zh: '\u8702\u7A9D\u88C5\u9970', definition: 'Honeycomb-like vaulting ornament in Islamic architecture', category: 'Architecture', l_levels: ['L1', 'L3'] },
      ],
      taboo_rules: [
        { description: 'Avoid figurative imagery in geometric/arabesque contexts', severity: 'critical' },
        { description: 'Maintain mathematical precision in tessellation patterns', severity: 'high' },
      ],
    },
    tibetan_thangka: {
      display_name: 'Tibetan Thangka',
      pipeline_variant: 'thangka_pipeline',
      weights: { L1: 0.15, L2: 0.15, L3: 0.20, L4: 0.25, L5: 0.25 },
      terms: [
        { term_en: 'Thangka', term_zh: '\u5510\u5361', definition: 'Scroll painting on cotton or silk depicting Buddhist deity or mandala', category: 'Medium', l_levels: ['L1', 'L3'] },
        { term_en: 'Mandala', term_zh: '\u66FC\u8377\u7F57', definition: 'Geometric configuration of symbols representing the universe', category: 'Iconography', l_levels: ['L3', 'L5'] },
        { term_en: 'Iconometric Grid', term_zh: '\u5EA6\u91CF\u7F51\u683C', definition: 'Proportional grid system for sacred figure drawing', category: 'Technique', l_levels: ['L1', 'L4'] },
      ],
      taboo_rules: [
        { description: 'Deity proportions must follow canonical iconometric grids', severity: 'critical' },
        { description: 'Color symbolism (e.g., blue = Vairocana) must be preserved', severity: 'high' },
        { description: 'Avoid casual or secular reinterpretation of sacred imagery', severity: 'critical' },
      ],
    },
  },
  stats: { total_terms: 30, total_taboos: 22, total_traditions: 9 },
};

// ---------------------------------------------------------------------------
// Helper: severity badge
// ---------------------------------------------------------------------------

function SeverityBadge({ severity }: { severity: string }) {
  const map: Record<string, string> = {
    critical: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300',
    high: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
    medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300',
    low: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300',
  };
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${map[severity] ?? map['medium']}`}>
      {severity}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Helper: L-level badge
// ---------------------------------------------------------------------------

function LevelBadge({ level }: { level: string }) {
  const colors: Record<string, string> = {
    L1: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
    L2: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/40 dark:text-cyan-300',
    L3: 'bg-violet-100 text-violet-700 dark:bg-violet-900/40 dark:text-violet-300',
    L4: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300',
    L5: 'bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300',
  };
  return (
    <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${colors[level] ?? 'bg-gray-100 text-gray-600'}`}>
      {level}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Helper: weight bar
// ---------------------------------------------------------------------------

function WeightBar({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value * 100);
  return (
    <div className="flex items-center gap-2">
      <span className="w-6 text-xs font-mono text-gray-500 dark:text-gray-400">{label}</span>
      <div className="flex-1 h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full bg-slate-600 dark:bg-slate-400 transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-10 text-xs text-right font-mono text-gray-500 dark:text-gray-400">{pct}%</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Tradition Accordion Card
// ---------------------------------------------------------------------------

function TraditionCard({ id, data, searchQuery }: { id: string; data: TraditionData; searchQuery: string }) {
  const [expanded, setExpanded] = useState(false);

  const filteredTerms = useMemo(() => {
    if (!searchQuery) return data.terms;
    const q = searchQuery.toLowerCase();
    return data.terms.filter(
      (t) =>
        t.term_en.toLowerCase().includes(q) ||
        t.term_zh.includes(q) ||
        t.definition.toLowerCase().includes(q)
    );
  }, [data.terms, searchQuery]);

  // If there's a search active and no matching terms, hide the card
  if (searchQuery && filteredTerms.length === 0) return null;

  return (
    <IOSCard variant="elevated" padding="none" className="overflow-hidden">
      {/* Header — always visible */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-gray-50 dark:hover:bg-gray-800/40 transition-colors"
      >
        <div className="flex items-center gap-3 min-w-0">
          <Globe2 className="w-5 h-5 text-slate-500 dark:text-slate-400 flex-shrink-0" />
          <div className="min-w-0">
            <h3 className="text-base font-semibold text-gray-900 dark:text-white truncate">
              {data.display_name}
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
              {data.terms.length} terms &middot; {data.taboo_rules.length} taboo rules &middot; {data.pipeline_variant}
            </p>
          </div>
        </div>
        {expanded ? (
          <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
        ) : (
          <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
        )}
      </button>

      {/* Expanded content */}
      {expanded && (
        <IOSCardContent className="px-5 pb-5 space-y-5">
          {/* L1-L5 Weights */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">L1-L5 Weights</h4>
            <div className="space-y-1.5">
              {Object.entries(data.weights).map(([k, v]) => (
                <WeightBar key={k} label={k} value={v} />
              ))}
            </div>
          </div>

          {/* Terminology */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-1.5">
              <BookOpen className="w-4 h-4" />
              Terminology ({filteredTerms.length})
            </h4>
            <div className="space-y-2">
              {filteredTerms.map((t, i) => (
                <div
                  key={`${id}-term-${i}`}
                  className="bg-gray-50 dark:bg-gray-800/50 rounded-lg px-4 py-3"
                >
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <span className="font-medium text-sm text-gray-900 dark:text-white">{t.term_en}</span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">{t.term_zh}</span>
                    <span className="text-xs text-gray-400 dark:text-gray-500 bg-gray-200 dark:bg-gray-700 px-1.5 py-0.5 rounded">
                      {t.category}
                    </span>
                    {t.l_levels.map((l) => (
                      <LevelBadge key={l} level={l} />
                    ))}
                  </div>
                  <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">{t.definition}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Taboo Rules */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4" />
              Taboo Rules ({data.taboo_rules.length})
            </h4>
            <div className="space-y-2">
              {data.taboo_rules.map((r, i) => (
                <div
                  key={`${id}-taboo-${i}`}
                  className="flex items-start gap-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg px-4 py-3"
                >
                  <SeverityBadge severity={r.severity} />
                  <p className="text-xs text-gray-700 dark:text-gray-300 leading-relaxed flex-1">{r.description}</p>
                </div>
              ))}
            </div>
          </div>
        </IOSCardContent>
      )}
    </IOSCard>
  );
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function KnowledgeBasePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTradition, setSelectedTradition] = useState<string>('all');

  const data = MOCK_DATA;
  const traditionKeys = Object.keys(data.traditions);

  const visibleTraditions = useMemo(() => {
    if (selectedTradition === 'all') return traditionKeys;
    return traditionKeys.filter((k) => k === selectedTradition);
  }, [traditionKeys, selectedTradition]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-gray-50 to-white dark:from-black dark:via-gray-900 dark:to-black">
      <div className="container mx-auto px-4 py-8 max-w-5xl">

        {/* Page header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-3 bg-gradient-to-r from-slate-700 to-amber-700 bg-clip-text text-transparent">
            Cultural Knowledge Base
          </h1>
          <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto mb-4">
            Browse terminology, taboo rules, and L1-L5 evaluation weights across 9 cultural art traditions used by the VULCA pipeline.
          </p>
          <Link to="/evaluate">
            <IOSButton variant="primary" size="sm" className="inline-flex items-center gap-1.5">
              <Sparkles className="w-4 h-4" />
              Try Evaluate
            </IOSButton>
          </Link>
        </div>

        {/* Stats cards */}
        <IOSCardGrid columns={3} gap="sm" className="mb-8">
          <IOSCard variant="glass" padding="md">
            <IOSCardContent>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{data.stats.total_traditions}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Traditions</p>
            </IOSCardContent>
          </IOSCard>
          <IOSCard variant="glass" padding="md">
            <IOSCardContent>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{data.stats.total_terms}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Terms</p>
            </IOSCardContent>
          </IOSCard>
          <IOSCard variant="glass" padding="md">
            <IOSCardContent>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{data.stats.total_taboos}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Taboo Rules</p>
            </IOSCardContent>
          </IOSCard>
        </IOSCardGrid>

        {/* Filters row */}
        <div className="flex flex-col md:flex-row gap-3 mb-6">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search terms..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-slate-500/40 transition"
            />
          </div>

          {/* Tradition filter */}
          <select
            value={selectedTradition}
            onChange={(e) => setSelectedTradition(e.target.value)}
            className="px-4 py-2.5 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-slate-500/40 transition min-w-[200px]"
          >
            <option value="all">All Traditions</option>
            {traditionKeys.map((k) => (
              <option key={k} value={k}>
                {data.traditions[k].display_name}
              </option>
            ))}
          </select>

          {searchQuery && (
            <IOSButton variant="text" size="sm" onClick={() => setSearchQuery('')}>
              Clear
            </IOSButton>
          )}
        </div>

        {/* Tradition list */}
        <div className="space-y-3">
          {visibleTraditions.map((key) => (
            <TraditionCard key={key} id={key} data={data.traditions[key]} searchQuery={searchQuery} />
          ))}

          {visibleTraditions.length === 0 && (
            <div className="text-center py-16">
              <Globe2 className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
              <p className="text-gray-500 dark:text-gray-400">No traditions match your filter.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
