import { useState, useMemo, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Palette, Sparkles, Loader2, ChevronDown, ChevronUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  IOSButton,
  IOSCard,
  IOSCardContent,
  IOSCardGrid,
} from '../components/ios';
import { API_PREFIX, API_BASE_URL } from '../config/api';
import GalleryCardActions from '../components/gallery/GalleryCardActions';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface GalleryItem {
  id: string;
  subject: string;
  tradition: string;
  media_type: string;
  scores: Record<string, number>;
  overall: number;
  best_image_url: string;
  total_rounds: number;
  total_latency_ms: number;
  created_at: number;
}

interface EvolutionStats {
  total_sessions: number;
  traditions_active: string[];
  evolutions_count: number;
  emerged_concepts: { name: string; description: string }[];
  archetypes: string[];
  last_evolved_at: string | null;
}

interface DigestionInsights {
  agent_insights: Record<string, string>;
  tradition_insights: Record<string, string>;
}

// ---------------------------------------------------------------------------
// Tradition display labels
// ---------------------------------------------------------------------------

const TRADITION_LABELS: Record<string, string> = {
  chinese_ink: 'Chinese Ink',
  chinese_xieyi: 'Chinese Xieyi',
  japanese_ukiyoe: 'Japanese Ukiyo-e',
  persian_miniature: 'Persian Miniature',
  indian_mughal: 'Mughal Painting',
  korean_minhwa: 'Korean Minhwa',
  islamic_geometric: 'Islamic Geometric',
  byzantine_icon: 'Byzantine Icon',
  tibetan_thangka: 'Tibetan Thangka',
  default: 'Default',
};

// Gradient placeholders per tradition (used when no image URL)
const TRADITION_GRADIENTS: Record<string, string> = {
  chinese_ink: 'linear-gradient(135deg, #2c3e50 0%, #bdc3c7 50%, #ecf0f1 100%)',
  chinese_xieyi: 'linear-gradient(135deg, #334155 0%, #94a3b8 50%, #e2e8f0 100%)',
  japanese_ukiyoe: 'linear-gradient(135deg, #1a3a5c 0%, #5b8fb9 40%, #f5e6ca 100%)',
  persian_miniature: 'linear-gradient(135deg, #1a472a 0%, #c5a03f 50%, #8b2942 100%)',
  indian_mughal: 'linear-gradient(135deg, #8b4513 0%, #daa520 50%, #cd5c5c 100%)',
  korean_minhwa: 'linear-gradient(135deg, #b22222 0%, #ffd700 40%, #228b22 100%)',
  islamic_geometric: 'linear-gradient(135deg, #0c3547 0%, #1e6f5c 40%, #d4a437 100%)',
  byzantine_icon: 'linear-gradient(135deg, #8b6914 0%, #daa520 30%, #4a0e0e 100%)',
  tibetan_thangka: 'linear-gradient(135deg, #6b3a2a 0%, #c62828 40%, #f9a825 100%)',
  default: 'linear-gradient(135deg, #334155 0%, #C87F4A 50%, #B8923D 100%)',
};

// ---------------------------------------------------------------------------
// Mock data (shown when API is unavailable)
// ---------------------------------------------------------------------------

const MOCK_GALLERY: GalleryItem[] = [
  {
    id: 'art-001', subject: 'Misty Mountains at Dawn', tradition: 'chinese_ink',
    media_type: 'image', scores: { L1: 0.91, L2: 0.88, L3: 0.95, L4: 0.93, L5: 0.90 },
    overall: 0.914, best_image_url: '', total_rounds: 3, total_latency_ms: 12400, created_at: 1741132800,
  },
  {
    id: 'art-002', subject: 'The Great Wave Reimagined', tradition: 'japanese_ukiyoe',
    media_type: 'image', scores: { L1: 0.89, L2: 0.85, L3: 0.92, L4: 0.88, L5: 0.87 },
    overall: 0.882, best_image_url: '', total_rounds: 2, total_latency_ms: 9800, created_at: 1741046400,
  },
  {
    id: 'art-003', subject: 'Garden of Paradise', tradition: 'persian_miniature',
    media_type: 'image', scores: { L1: 0.87, L2: 0.83, L3: 0.90, L4: 0.92, L5: 0.86 },
    overall: 0.876, best_image_url: '', total_rounds: 3, total_latency_ms: 15200, created_at: 1741046400,
  },
  {
    id: 'art-004', subject: 'Court of the Mughal Emperor', tradition: 'indian_mughal',
    media_type: 'image', scores: { L1: 0.86, L2: 0.84, L3: 0.88, L4: 0.90, L5: 0.85 },
    overall: 0.866, best_image_url: '', total_rounds: 2, total_latency_ms: 8400, created_at: 1740960000,
  },
  {
    id: 'art-005', subject: 'Longevity Symbols', tradition: 'korean_minhwa',
    media_type: 'image', scores: { L1: 0.84, L2: 0.82, L3: 0.89, L4: 0.86, L5: 0.91 },
    overall: 0.864, best_image_url: '', total_rounds: 3, total_latency_ms: 11600, created_at: 1740960000,
  },
  {
    id: 'art-006', subject: 'Alhambra Tessellation', tradition: 'islamic_geometric',
    media_type: 'image', scores: { L1: 0.93, L2: 0.91, L3: 0.88, L4: 0.85, L5: 0.83 },
    overall: 0.880, best_image_url: '', total_rounds: 2, total_latency_ms: 7800, created_at: 1740873600,
  },
  {
    id: 'art-007', subject: 'Theotokos of Compassion', tradition: 'byzantine_icon',
    media_type: 'image', scores: { L1: 0.85, L2: 0.87, L3: 0.86, L4: 0.92, L5: 0.88 },
    overall: 0.876, best_image_url: '', total_rounds: 2, total_latency_ms: 9200, created_at: 1740787200,
  },
  {
    id: 'art-008', subject: 'Medicine Buddha Mandala', tradition: 'tibetan_thangka',
    media_type: 'image', scores: { L1: 0.82, L2: 0.84, L3: 0.87, L4: 0.93, L5: 0.91 },
    overall: 0.874, best_image_url: '', total_rounds: 3, total_latency_ms: 14000, created_at: 1740700800,
  },
];

// ---------------------------------------------------------------------------
// Score bar
// ---------------------------------------------------------------------------

function ScoreBar({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value * 100);
  const barColor =
    value >= 0.9 ? 'bg-[#5F8A50] dark:bg-[#87A878]' :
    value >= 0.8 ? 'bg-slate-500 dark:bg-slate-400' :
    'bg-amber-500 dark:bg-amber-400';

  return (
    <div className="flex items-center gap-1.5">
      <span className="w-5 text-[10px] font-mono text-gray-400">{label}</span>
      <div className="flex-1 h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${barColor} transition-all duration-300`} style={{ width: `${pct}%` }} />
      </div>
      <span className="w-8 text-[10px] text-right font-mono text-gray-500 dark:text-gray-400">{pct}%</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Evolution banner
// ---------------------------------------------------------------------------

function EvolutionBanner({ stats }: { stats: EvolutionStats | null }) {
  if (!stats || stats.total_sessions === 0) return null;

  return (
    <div className="mb-6 rounded-xl border border-[#5F8A50]/20 dark:border-[#5F8A50]/30 bg-[#5F8A50]/5 dark:bg-[#5F8A50]/10 p-4">
      <div className="flex flex-wrap items-center gap-4 text-sm">
        <div className="flex items-center gap-2">
          <span className="text-[#5F8A50] dark:text-[#87A878] font-semibold">System Evolution</span>
        </div>
        <div className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
          <span className="font-mono text-[#C87F4A]">{stats.total_sessions}</span>
          <span>sessions learned</span>
        </div>
        {stats.traditions_active.length > 0 && (
          <div className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
            <span className="font-mono text-[#C87F4A]">{stats.traditions_active.length}</span>
            <span>traditions active</span>
          </div>
        )}
        {stats.evolutions_count > 0 && (
          <div className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
            <span className="font-mono text-[#C87F4A]">{stats.evolutions_count}</span>
            <span>evolutions</span>
          </div>
        )}
        {stats.emerged_concepts.length > 0 && (
          <div className="hidden sm:flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
            <span className="font-mono text-[#C87F4A]">{stats.emerged_concepts.length}</span>
            <span>emerged concepts</span>
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Agent role display config
// ---------------------------------------------------------------------------

const AGENT_CONFIG: Record<string, { emoji: string; label: string; color: string }> = {
  scout: { emoji: '\uD83D\uDD0D', label: 'Scout', color: '#B8923D' },
  draft: { emoji: '\uD83C\uDFA8', label: 'Draft', color: '#C87F4A' },
  critic: { emoji: '\uD83D\uDCDD', label: 'Critic', color: '#5F8A50' },
  queen: { emoji: '\uD83D\uDC51', label: 'Queen', color: '#C65D4D' },
};

// ---------------------------------------------------------------------------
// Evolution Insights Panel (collapsible)
// ---------------------------------------------------------------------------

function EvolutionInsightsPanel({ insights }: { insights: DigestionInsights | null }) {
  const [isOpen, setIsOpen] = useState(false);
  const [expandedTradition, setExpandedTradition] = useState<string | null>(null);

  if (!insights) return null;

  const hasAgentInsights = insights.agent_insights && Object.keys(insights.agent_insights).length > 0;
  const hasTraditionInsights = insights.tradition_insights && Object.keys(insights.tradition_insights).length > 0;

  if (!hasAgentInsights && !hasTraditionInsights) return null;

  return (
    <div className="mb-6">
      {/* Toggle button */}
      <IOSButton
        variant="glass"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 rounded-xl border border-[#C87F4A]/20 dark:border-[#C87F4A]/30 bg-[#C87F4A]/5 dark:bg-[#C87F4A]/10 text-left"
      >
        <div className="flex items-center gap-2">
          <span className="text-[#C87F4A] dark:text-[#DDA574] font-semibold text-sm">
            Evolution Insights
          </span>
          <span className="text-[10px] text-gray-400 dark:text-gray-500">
            {hasAgentInsights ? `${Object.keys(insights.agent_insights).length} agents` : ''}
            {hasAgentInsights && hasTraditionInsights ? ' · ' : ''}
            {hasTraditionInsights ? `${Object.keys(insights.tradition_insights).length} traditions` : ''}
          </span>
        </div>
        {isOpen
          ? <ChevronUp className="w-4 h-4 text-gray-400" />
          : <ChevronDown className="w-4 h-4 text-gray-400" />
        }
      </IOSButton>

      {/* Collapsible content */}
      {isOpen && (
        <div className="mt-3 space-y-4">
          {/* Agent Insights */}
          {hasAgentInsights && (
            <div>
              <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
                Agent Insights
              </h3>
              <IOSCardGrid columns={2} gap="sm">
                {Object.entries(AGENT_CONFIG).map(([role, config]) => {
                  const insight = insights.agent_insights[role];
                  if (!insight) return null;
                  return (
                    <IOSCard key={role} variant="elevated" padding="md">
                      <IOSCardContent>
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-lg">{config.emoji}</span>
                          <span className="font-semibold text-sm" style={{ color: config.color }}>
                            {config.label}
                          </span>
                        </div>
                        <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
                          {insight}
                        </p>
                      </IOSCardContent>
                    </IOSCard>
                  );
                })}
              </IOSCardGrid>
            </div>
          )}

          {/* Tradition Insights */}
          {hasTraditionInsights && (
            <div>
              <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
                Tradition Insights
              </h3>
              <div className="space-y-1.5">
                {Object.entries(insights.tradition_insights).map(([tradition, insight]) => {
                  const isExpanded = expandedTradition === tradition;
                  const displayName = TRADITION_LABELS[tradition] ?? tradition.replace(/_/g, ' ');
                  return (
                    <div key={tradition} className="rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                      <IOSButton
                        variant="text"
                        onClick={() => setExpandedTradition(isExpanded ? null : tradition)}
                        className="w-full flex items-center justify-between px-3 py-2.5 text-left"
                      >
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          {displayName}
                        </span>
                        {isExpanded
                          ? <ChevronUp className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                          : <ChevronDown className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                        }
                      </IOSButton>
                      {isExpanded && (
                        <div className="px-3 pb-3 border-t border-gray-100 dark:border-gray-800">
                          <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed pt-2">
                            {insight}
                          </p>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Artwork card
// ---------------------------------------------------------------------------

function ArtworkCard({ artwork, likeCount, onSelect }: { artwork: GalleryItem; likeCount: number; onSelect: (a: GalleryItem) => void }) {
  const traditionLabel = TRADITION_LABELS[artwork.tradition] ?? artwork.tradition.replace(/_/g, ' ');
  const gradient = TRADITION_GRADIENTS[artwork.tradition] ?? TRADITION_GRADIENTS.default;
  const resolvedImageUrl = (() => {
    const url = artwork.best_image_url;
    if (!url) return null;
    if (url.startsWith('data:') || url.startsWith('http://') || url.startsWith('https://')) return url;
    if (url.startsWith('/static/') || url.startsWith('static/')) {
      const normalized = url.startsWith('/') ? url : `/${url}`;
      return `${API_BASE_URL}${normalized}`;
    }
    return url;
  })();
  const hasImage = !!resolvedImageUrl;

  return (
    <motion.div
      className="group cursor-pointer"
      onClick={() => onSelect(artwork)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === 'Enter') onSelect(artwork); }}
      whileHover={{ scale: 1.02 }}
      transition={{ type: 'spring', stiffness: 400, damping: 30 }}
    >
      {/* Image — vertical aspect 4/5, large rounded corners */}
      <div className="aspect-[4/5] rounded-3xl overflow-hidden relative bg-surface-container-high shadow-ambient-md group-hover:shadow-ambient-xl transition-shadow duration-500">
        <div className="absolute inset-0" style={{ background: gradient }} />
        {hasImage && (
          <img
            src={resolvedImageUrl}
            alt={artwork.subject}
            className="absolute inset-0 w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-700"
            loading="lazy"
            onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none'; }}
          />
        )}
        {/* Tradition badge — top right */}
        <span className="absolute top-5 right-5 text-[10px] font-bold uppercase tracking-widest px-4 py-1.5 rounded-full bg-white/90 backdrop-blur-xl text-on-surface-variant">
          {traditionLabel}
        </span>
      </div>

      {/* Title + minimal info */}
      <div className="pt-5 pb-2 px-1">
        <h3 className="font-semibold text-base text-on-surface line-clamp-2 group-hover:text-primary-500 transition-colors">
          {artwork.subject}
        </h3>
      </div>
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Sort options
// ---------------------------------------------------------------------------

type SortOption = 'newest' | 'score' | 'rounds';

const SORT_LABELS: Record<SortOption, string> = {
  newest: 'Newest First',
  score: 'Highest Score',
  rounds: 'Most Rounds',
};

const PAGE_SIZE = 9; // Gallery "curated" feel — 3x3 grid per page

export default function GalleryPage() {
  const [artworks, setArtworks] = useState<GalleryItem[]>(MOCK_GALLERY);
  const [totalCount, setTotalCount] = useState<number>(MOCK_GALLERY.length);
  const [evolutionStats, setEvolutionStats] = useState<EvolutionStats | null>(null);
  const [digestionInsights, setDigestionInsights] = useState<DigestionInsights | null>(null);
  const [likeCounts, setLikeCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [isLive, setIsLive] = useState(false);  // true if data came from API
  const [selectedTradition, setSelectedTradition] = useState<string>('all');
  const [minScore, setMinScore] = useState<number>(0);
  const [selectedArtwork, setSelectedArtwork] = useState<GalleryItem | null>(null);
  const [sortBy, setSortBy] = useState<SortOption>('newest');
  const [currentOffset, setCurrentOffset] = useState(0);

  // Fetch gallery items from API with pagination + sorting
  const fetchGalleryPage = useCallback(async (
    offset: number,
    sort: SortOption,
    tradition: string,
    append: boolean,
  ) => {
    if (append) {
      setLoadingMore(true);
    } else {
      setLoading(true);
    }

    try {
      const params = new URLSearchParams({
        limit: String(PAGE_SIZE),
        offset: String(offset),
        sort_by: sort,
        sort_order: 'desc',
      });
      if (tradition !== 'all') {
        params.set('tradition', tradition);
      }

      const res = await fetch(`${API_PREFIX}/prototype/gallery?${params.toString()}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      if (Array.isArray(data.items)) {
        if (data.items.length > 0 || data.total === 0) {
          if (append) {
            setArtworks(prev => [...prev, ...data.items]);
          } else {
            setArtworks(data.items.length > 0 ? data.items : MOCK_GALLERY);
          }
          setTotalCount(data.total ?? data.items.length);
          setCurrentOffset(offset + data.items.length);
          if (data.items.length > 0) {
            setIsLive(true);
          }
        }
      }
    } catch {
      // API unavailable — keep mock data on initial load
      if (!append) {
        setArtworks(MOCK_GALLERY);
        setTotalCount(MOCK_GALLERY.length);
        setIsLive(false);
      }
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, []);

  // Initial fetch + evolution/insights
  useEffect(() => {
    let cancelled = false;

    fetchGalleryPage(0, sortBy, selectedTradition, false);

    async function fetchEvolution() {
      try {
        const res = await fetch(`${API_PREFIX}/prototype/evolution`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (!cancelled) setEvolutionStats(data);
      } catch {
        // Evolution stats unavailable — no banner
      }
    }

    async function fetchDigestionInsights() {
      try {
        const res = await fetch(`${API_PREFIX}/digestion/status`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (!cancelled) {
          const agentInsights = data.agent_insights ?? {};
          const traditionInsights = data.tradition_insights ?? {};
          if (Object.keys(agentInsights).length > 0 || Object.keys(traditionInsights).length > 0) {
            setDigestionInsights({
              agent_insights: agentInsights,
              tradition_insights: traditionInsights,
            });
          }
        }
      } catch {
        // Digestion insights unavailable — no panel
      }
    }

    async function fetchLikes() {
      try {
        const res = await fetch(`${API_PREFIX}/prototype/gallery/likes`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (!cancelled && data && typeof data === 'object') {
          setLikeCounts(data);
        }
      } catch {
        // Likes unavailable — show zero counts
      }
    }

    fetchEvolution();
    fetchDigestionInsights();
    fetchLikes();

    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Re-fetch when sort or tradition filter changes (reset to page 1)
  useEffect(() => {
    // Skip the initial render (handled by the fetch above)
    fetchGalleryPage(0, sortBy, selectedTradition, false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sortBy, selectedTradition]);

  const handleLoadMore = () => {
    fetchGalleryPage(currentOffset, sortBy, selectedTradition, true);
  };

  const traditions = useMemo(
    () => Array.from(new Set(artworks.map(a => a.tradition))),
    [artworks],
  );

  // Client-side min-score filter (applied on top of server-side tradition/sort)
  const filtered = useMemo(() => {
    if (minScore <= 0) return artworks;
    return artworks.filter((a) => a.overall >= minScore);
  }, [artworks, minScore]);

  const hasMore = isLive && currentOffset < totalCount;

  // Display range: "Showing 1-50 of 670"
  const rangeStart = filtered.length > 0 ? 1 : 0;
  const rangeEnd = filtered.length;

  return (
    <div className="min-h-screen bg-surface dark:bg-[#0F0D0B]">
      <div className="max-w-[1440px] mx-auto px-6 sm:px-10 py-10">

        {/* Page header — Gallery hero */}
        <div className="mb-12">
          <h1 className="font-display text-5xl sm:text-6xl lg:text-7xl font-bold text-on-surface mb-2 tracking-tight leading-[0.95]">
            CULTURAL<br />
            <span className="text-primary-500">GALLERY</span>
          </h1>
          <p className="text-on-surface-variant max-w-lg mt-4 text-sm leading-relaxed">
            A curated showcase of cultural artifacts, digital heritage, and artistic expressions generated through the VULCA pipeline.
          </p>
          <div className="flex items-center gap-3 mt-5">
            <Link to="/canvas">
              <button className="bg-primary-500 text-white px-6 py-2.5 rounded-full font-medium text-sm hover:bg-primary-600 active:scale-95 transition-all inline-flex items-center gap-1.5">
                <Sparkles className="w-4 h-4" />
                Create Your Own
              </button>
            </Link>
            {!isLive && !loading && (
              <span className="text-[10px] text-outline px-3 py-1 rounded-full bg-surface-container-high">
                Demo data — start the backend to see live creations
              </span>
            )}
          </div>
        </div>

        {/* Evolution banner (P2) */}
        <EvolutionBanner stats={evolutionStats} />

        {/* Evolution Insights Panel (collapsible) */}
        <EvolutionInsightsPanel insights={digestionInsights} />

        {/* Tradition pills */}
        <div className="flex flex-wrap gap-2 mb-4">
          {['all', ...traditions].map((t) => {
            const label = t === 'all' ? 'All' : (TRADITION_LABELS[t] ?? t.replace(/_/g, ' '));
            const isActive = selectedTradition === t;
            return (
              <button
                key={t}
                onClick={() => setSelectedTradition(t)}
                className={`px-4 py-2 rounded-full text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/20'
                    : 'bg-surface-container-lowest text-on-surface-variant hover:bg-surface-container-high'
                }`}
              >
                {label}
              </button>
            );
          })}
        </div>

        {/* Sort pills + score filter + count */}
        <div className="flex flex-wrap gap-2 mb-8 items-center">
          {(Object.entries(SORT_LABELS) as [SortOption, string][]).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setSortBy(key)}
              className={`px-4 py-2 rounded-full text-xs font-semibold transition-all ${
                sortBy === key
                  ? 'bg-on-surface text-white'
                  : 'bg-surface-container-lowest text-on-surface-variant hover:bg-surface-container-high'
              }`}
            >
              {label}
            </button>
          ))}

          <span className="mx-1 text-surface-container-high">|</span>

          {[0, 0.80, 0.85, 0.90].map((score) => (
            <button
              key={score}
              onClick={() => setMinScore(score)}
              className={`px-3 py-2 rounded-full text-xs font-semibold transition-all ${
                minScore === score
                  ? 'bg-on-surface text-white'
                  : 'bg-surface-container-lowest text-on-surface-variant hover:bg-surface-container-high'
              }`}
            >
              {score === 0 ? 'Any Score' : `≥${Math.round(score * 100)}%`}
            </button>
          ))}

          {(selectedTradition !== 'all' || minScore > 0 || sortBy !== 'newest') && (
            <button
              onClick={() => { setSelectedTradition('all'); setMinScore(0); setSortBy('newest'); }}
              className="px-3 py-2 rounded-full text-xs font-semibold text-primary-500 hover:bg-primary-50 transition-all"
            >
              Reset
            </button>
          )}

          <span className="text-xs text-on-surface-variant/60 sm:ml-auto flex items-center gap-1.5">
            {loading && <Loader2 className="w-3 h-3 animate-spin" />}
            {isLive
              ? `Showing ${rangeStart}–${rangeEnd} of ${totalCount}`
              : `${filtered.length} artwork${filtered.length !== 1 ? 's' : ''}`
            }
            {isLive && (
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-[#5F8A50]" title="Live data" />
            )}
          </span>
        </div>

        {/* Gallery grid — 3-column curated layout per design spec */}
        {filtered.length > 0 ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 sm:gap-10">
              {filtered.map((artwork) => (
                <ArtworkCard key={artwork.id} artwork={artwork} likeCount={likeCounts[artwork.id] ?? 0} onSelect={setSelectedArtwork} />
              ))}
            </div>

            {/* Load More / Pagination footer */}
            {hasMore && (
              <div className="flex flex-col items-center gap-3 mt-8">
                <IOSButton
                  variant="secondary"
                  size="sm"
                  onClick={handleLoadMore}
                  disabled={loadingMore}
                  className="inline-flex items-center gap-2 min-w-[160px] justify-center"
                >
                  {loadingMore ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    <>Load More</>
                  )}
                </IOSButton>
                <span className="text-[11px] text-gray-400 dark:text-gray-500">
                  {totalCount - currentOffset} more artwork{totalCount - currentOffset !== 1 ? 's' : ''} available
                </span>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-24">
            <Palette className="w-14 h-14 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
              No artworks yet
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 max-w-md mx-auto mb-4">
              Create your first artwork in the Canvas — it will appear here automatically.
            </p>
            <Link to="/canvas">
              <IOSButton variant="primary" size="sm" className="inline-flex items-center gap-1.5">
                <Sparkles className="w-4 h-4" />
                Open Canvas
              </IOSButton>
            </Link>
          </div>
        )}
      </div>

      {/* Detail Modal with AnimatePresence */}
      <AnimatePresence>
        {selectedArtwork && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
            onClick={() => setSelectedArtwork(null)}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <motion.div
              className="bg-surface-container-lowest rounded-2xl shadow-ambient-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              transition={{ type: 'spring', stiffness: 400, damping: 30 }}
            >
              <div className="aspect-[16/9] relative rounded-t-2xl overflow-hidden bg-surface-container-high">
                {selectedArtwork.best_image_url ? (
                  <img
                    src={(() => {
                      const url = selectedArtwork.best_image_url;
                      if (url.startsWith('data:') || url.startsWith('http')) return url;
                      if (url.startsWith('/static/') || url.startsWith('static/'))
                        return `${API_BASE_URL}${url.startsWith('/') ? url : `/${url}`}`;
                      return url;
                    })()}
                    alt={selectedArtwork.subject}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center" style={{ background: TRADITION_GRADIENTS[selectedArtwork.tradition] ?? TRADITION_GRADIENTS.default }}>
                    <span className="text-white text-4xl">🎨</span>
                  </div>
                )}
                <button onClick={() => setSelectedArtwork(null)} className="absolute top-4 right-4 w-10 h-10 rounded-full bg-black/40 text-white flex items-center justify-center hover:bg-black/60 transition-colors backdrop-blur-sm" aria-label="Close">✕</button>
              </div>
              <div className="p-8">
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h2 className="font-display text-2xl font-bold text-on-surface mb-2">{selectedArtwork.subject}</h2>
                    <span className="text-[11px] font-bold uppercase tracking-widest text-primary-500 bg-primary-50 px-3 py-1 rounded-full">
                      {TRADITION_LABELS[selectedArtwork.tradition] ?? selectedArtwork.tradition.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-3xl font-bold text-on-surface">{Math.round(selectedArtwork.overall * 100)}%</span>
                    <p className="text-[11px] text-on-surface-variant">Overall Score</p>
                  </div>
                </div>
                <div className="mb-6">
                  <h3 className="text-[11px] font-bold uppercase tracking-widest text-outline mb-3">Dimension Scores</h3>
                  <div className="grid grid-cols-5 gap-3">
                    {Object.entries(selectedArtwork.scores).map(([dim, score]) => (
                      <div key={dim} className="text-center">
                        <div className={`w-full aspect-square rounded-xl flex items-center justify-center text-sm font-bold mb-1 ${score >= 0.9 ? 'bg-primary-500 text-white' : 'bg-surface-container-high text-on-surface-variant'}`}>{dim}</div>
                        <span className="text-[10px] font-bold text-on-surface-variant">{Math.round(score * 100)}%</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="flex items-center gap-4 text-[11px] text-on-surface-variant">
                  <span>{selectedArtwork.total_rounds} round{selectedArtwork.total_rounds !== 1 ? 's' : ''}</span>
                  <span>{(selectedArtwork.total_latency_ms / 1000).toFixed(1)}s</span>
                  {selectedArtwork.created_at && <span>{new Date(selectedArtwork.created_at * 1000).toLocaleDateString()}</span>}
                </div>
                <div className="flex items-center gap-3 mt-6 pt-6">
                  <GalleryCardActions sessionId={selectedArtwork.id} subject={selectedArtwork.subject} tradition={selectedArtwork.tradition} initialLikes={likeCounts[selectedArtwork.id] ?? 0} />
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
