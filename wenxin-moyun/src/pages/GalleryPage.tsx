import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Filter, Palette, Layers, Sparkles } from 'lucide-react';
import {
  IOSButton,
  IOSCard,
  IOSCardContent,
  IOSCardGrid,
} from '../components/ios';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ArtworkItem {
  id: string;
  subject: string;
  tradition: string;
  tradition_label: string;
  template: string;
  scores: { L1: number; L2: number; L3: number; L4: number; L5: number };
  overall: number;
  gradient: string;            // CSS gradient used as image placeholder
  generated_at: string;
}

// ---------------------------------------------------------------------------
// Mock data (6-8 sample artworks with gradient placeholders)
// ---------------------------------------------------------------------------

const MOCK_ARTWORKS: ArtworkItem[] = [
  {
    id: 'art-001',
    subject: 'Misty Mountains at Dawn',
    tradition: 'chinese_ink',
    tradition_label: 'Chinese Ink',
    template: 'ink_wash_pipeline',
    scores: { L1: 0.91, L2: 0.88, L3: 0.95, L4: 0.93, L5: 0.90 },
    overall: 0.914,
    gradient: 'linear-gradient(135deg, #2c3e50 0%, #bdc3c7 50%, #ecf0f1 100%)',
    generated_at: '2026-03-05',
  },
  {
    id: 'art-002',
    subject: 'The Great Wave Reimagined',
    tradition: 'japanese_ukiyoe',
    tradition_label: 'Japanese Ukiyo-e',
    template: 'ukiyoe_pipeline',
    scores: { L1: 0.89, L2: 0.85, L3: 0.92, L4: 0.88, L5: 0.87 },
    overall: 0.882,
    gradient: 'linear-gradient(135deg, #1a3a5c 0%, #5b8fb9 40%, #f5e6ca 100%)',
    generated_at: '2026-03-04',
  },
  {
    id: 'art-003',
    subject: 'Garden of Paradise',
    tradition: 'persian_miniature',
    tradition_label: 'Persian Miniature',
    template: 'persian_miniature_pipeline',
    scores: { L1: 0.87, L2: 0.83, L3: 0.90, L4: 0.92, L5: 0.86 },
    overall: 0.876,
    gradient: 'linear-gradient(135deg, #1a472a 0%, #c5a03f 50%, #8b2942 100%)',
    generated_at: '2026-03-04',
  },
  {
    id: 'art-004',
    subject: 'Court of the Mughal Emperor',
    tradition: 'indian_mughal',
    tradition_label: 'Mughal Painting',
    template: 'mughal_pipeline',
    scores: { L1: 0.86, L2: 0.84, L3: 0.88, L4: 0.90, L5: 0.85 },
    overall: 0.866,
    gradient: 'linear-gradient(135deg, #8b4513 0%, #daa520 50%, #cd5c5c 100%)',
    generated_at: '2026-03-03',
  },
  {
    id: 'art-005',
    subject: 'Longevity Symbols',
    tradition: 'korean_minhwa',
    tradition_label: 'Korean Minhwa',
    template: 'minhwa_pipeline',
    scores: { L1: 0.84, L2: 0.82, L3: 0.89, L4: 0.86, L5: 0.91 },
    overall: 0.864,
    gradient: 'linear-gradient(135deg, #b22222 0%, #ffd700 40%, #228b22 100%)',
    generated_at: '2026-03-03',
  },
  {
    id: 'art-006',
    subject: 'Alhambra Tessellation',
    tradition: 'islamic_geometric',
    tradition_label: 'Islamic Geometric',
    template: 'islamic_geo_pipeline',
    scores: { L1: 0.93, L2: 0.91, L3: 0.88, L4: 0.85, L5: 0.83 },
    overall: 0.880,
    gradient: 'linear-gradient(135deg, #0c3547 0%, #1e6f5c 40%, #d4a437 100%)',
    generated_at: '2026-03-02',
  },
  {
    id: 'art-007',
    subject: 'Theotokos of Compassion',
    tradition: 'byzantine_icon',
    tradition_label: 'Byzantine Icon',
    template: 'byzantine_pipeline',
    scores: { L1: 0.85, L2: 0.87, L3: 0.86, L4: 0.92, L5: 0.88 },
    overall: 0.876,
    gradient: 'linear-gradient(135deg, #8b6914 0%, #daa520 30%, #4a0e0e 100%)',
    generated_at: '2026-03-01',
  },
  {
    id: 'art-008',
    subject: 'Medicine Buddha Mandala',
    tradition: 'tibetan_thangka',
    tradition_label: 'Tibetan Thangka',
    template: 'thangka_pipeline',
    scores: { L1: 0.82, L2: 0.84, L3: 0.87, L4: 0.93, L5: 0.91 },
    overall: 0.874,
    gradient: 'linear-gradient(135deg, #1a237e 0%, #c62828 40%, #f9a825 100%)',
    generated_at: '2026-02-28',
  },
];

// Unique traditions for filter
const ALL_TRADITIONS = Array.from(new Set(MOCK_ARTWORKS.map((a) => a.tradition)));

// ---------------------------------------------------------------------------
// Score bar
// ---------------------------------------------------------------------------

function ScoreBar({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value * 100);
  const barColor =
    value >= 0.9 ? 'bg-green-500 dark:bg-green-400' :
    value >= 0.8 ? 'bg-blue-500 dark:bg-blue-400' :
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
// Artwork card
// ---------------------------------------------------------------------------

function ArtworkCard({ artwork }: { artwork: ArtworkItem }) {
  const overallPct = Math.round(artwork.overall * 100);
  const overallColor =
    artwork.overall >= 0.9 ? 'text-green-600 dark:text-green-400' :
    artwork.overall >= 0.85 ? 'text-blue-600 dark:text-blue-400' :
    'text-amber-600 dark:text-amber-400';

  return (
    <IOSCard variant="elevated" padding="none" className="overflow-hidden h-full flex flex-col">
      {/* Gradient placeholder image */}
      <div
        className="w-full aspect-[4/3] relative"
        style={{ background: artwork.gradient }}
      >
        {/* Tradition label overlay */}
        <span className="absolute top-2 left-2 text-[10px] font-medium px-2 py-0.5 rounded-full bg-black/40 text-white backdrop-blur-sm">
          {artwork.tradition_label}
        </span>
        {/* Overall score badge */}
        <span className={`absolute top-2 right-2 text-xs font-bold px-2 py-0.5 rounded-full bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm ${overallColor}`}>
          {overallPct}%
        </span>
      </div>

      {/* Content */}
      <IOSCardContent className="p-4 flex-1 flex flex-col">
        <h3 className="font-semibold text-sm text-gray-900 dark:text-white mb-1 line-clamp-2">
          {artwork.subject}
        </h3>
        <p className="text-[11px] text-gray-400 dark:text-gray-500 mb-3">
          {artwork.template} &middot; {artwork.generated_at}
        </p>

        {/* L1-L5 score bars */}
        <div className="space-y-1 mt-auto">
          {Object.entries(artwork.scores).map(([k, v]) => (
            <ScoreBar key={k} label={k} value={v} />
          ))}
        </div>
      </IOSCardContent>
    </IOSCard>
  );
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function GalleryPage() {
  const [selectedTradition, setSelectedTradition] = useState<string>('all');
  const [minScore, setMinScore] = useState<number>(0);

  const filtered = useMemo(() => {
    return MOCK_ARTWORKS.filter((a) => {
      if (selectedTradition !== 'all' && a.tradition !== selectedTradition) return false;
      if (a.overall < minScore) return false;
      return true;
    });
  }, [selectedTradition, minScore]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-gray-50 to-white dark:from-black dark:via-gray-900 dark:to-black">
      <div className="container mx-auto px-4 py-8 max-w-6xl">

        {/* Page header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-3 bg-gradient-to-r from-slate-700 to-amber-700 bg-clip-text text-transparent">
            Pipeline Gallery
          </h1>
          <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto mb-4">
            Generated cultural artworks from the VULCA evaluation pipeline, scored across L1-L5 dimensions.
          </p>
          <Link to="/evaluate">
            <IOSButton variant="primary" size="sm" className="inline-flex items-center gap-1.5">
              <Sparkles className="w-4 h-4" />
              Evaluate Your Own
            </IOSButton>
          </Link>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-3 mb-6 items-start sm:items-center">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={selectedTradition}
              onChange={(e) => setSelectedTradition(e.target.value)}
              className="px-3 py-2 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-slate-500/40 transition"
            >
              <option value="all">All Traditions</option>
              {ALL_TRADITIONS.map((t) => {
                const label = MOCK_ARTWORKS.find((a) => a.tradition === t)?.tradition_label ?? t;
                return (
                  <option key={t} value={t}>{label}</option>
                );
              })}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-gray-400" />
            <select
              value={String(minScore)}
              onChange={(e) => setMinScore(Number(e.target.value))}
              className="px-3 py-2 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-slate-500/40 transition"
            >
              <option value="0">Min Score: Any</option>
              <option value="0.80">Min Score: 80%</option>
              <option value="0.85">Min Score: 85%</option>
              <option value="0.90">Min Score: 90%</option>
            </select>
          </div>

          {(selectedTradition !== 'all' || minScore > 0) && (
            <IOSButton variant="text" size="sm" onClick={() => { setSelectedTradition('all'); setMinScore(0); }}>
              Reset
            </IOSButton>
          )}

          <span className="text-xs text-gray-400 dark:text-gray-500 sm:ml-auto">
            {filtered.length} artwork{filtered.length !== 1 ? 's' : ''}
          </span>
        </div>

        {/* Gallery grid */}
        {filtered.length > 0 ? (
          <IOSCardGrid columns={4} gap="md">
            {filtered.map((artwork) => (
              <ArtworkCard key={artwork.id} artwork={artwork} />
            ))}
          </IOSCardGrid>
        ) : (
          <div className="text-center py-24">
            <Palette className="w-14 h-14 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
              No artworks yet
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 max-w-md mx-auto">
              No artworks yet — run a pipeline to generate your first artwork.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
