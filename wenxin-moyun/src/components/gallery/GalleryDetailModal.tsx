/**
 * Gallery Detail Modal — Full artwork view with L1-L5 scores + rationale.
 * Triggered when user clicks a gallery card.
 */

import { useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { API_BASE_URL } from '@/config/api';
import { getTraditionLabel, L_LABELS } from '@/utils/tradition-labels';

interface GalleryItem {
  id: string;
  subject: string;
  tradition: string;
  scores: Record<string, number>;
  overall: number;
  best_image_url: string;
  total_rounds: number;
  total_latency_ms: number;
  created_at: number;
  likes_count: number;
}

interface Props {
  artwork: GalleryItem | null;
  onClose: () => void;
}

const L_COLORS: Record<string, string> = {
  L1: 'bg-primary-500',
  L2: 'bg-cultural-sage-500',
  L3: 'bg-cultural-bronze-500',
  L4: 'bg-cultural-amber-500',
  L5: 'bg-cultural-coral-500',
};

function resolveImageUrl(url: string | null | undefined): string | null {
  if (!url) return null;
  if (url.startsWith('data:') || url.startsWith('http://') || url.startsWith('https://')) return url;
  if (url.startsWith('mock://') || url.startsWith('gemini://')) return null;
  if (url.startsWith('/')) return `${API_BASE_URL}${url}`;
  return `${API_BASE_URL}/${url}`;
}

export default function GalleryDetailModal({ artwork, onClose }: Props) {
  // Escape key handler
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape') onClose();
  }, [onClose]);

  useEffect(() => {
    if (!artwork) return;
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [artwork, handleKeyDown]);

  if (!artwork) return null;

  const imageUrl = resolveImageUrl(artwork.best_image_url);
  const traditionLabel = getTraditionLabel(artwork.tradition);
  const scores = artwork.scores || {};
  const sortedDims = ['L1', 'L2', 'L3', 'L4', 'L5'].filter(d => scores[d] != null);

  // Find strongest and weakest
  let strongest = 'L1', weakest = 'L5';
  let maxS = -1, minS = 2;
  for (const d of sortedDims) {
    if (scores[d] > maxS) { maxS = scores[d]; strongest = d; }
    if (scores[d] < minS) { minS = scores[d]; weakest = d; }
  }

  const createdDate = artwork.created_at
    ? new Date(artwork.created_at * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    : '';

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.2 }}
      >
        {/* Backdrop */}
        <motion.div
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          onClick={onClose}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        />

        {/* Modal */}
        <motion.div
          role="dialog"
          aria-modal="true"
          aria-label={`Artwork detail: ${artwork.subject}`}
          className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-surface rounded-3xl shadow-2xl"
          initial={{ scale: 0.95, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.95, opacity: 0, y: 20 }}
          transition={{ type: 'spring', stiffness: 400, damping: 30 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Close button */}
          <button
            onClick={onClose}
            aria-label="Close"
            className="absolute top-4 right-4 z-10 min-w-[44px] min-h-[44px] w-11 h-11 flex items-center justify-center rounded-full bg-white/80 backdrop-blur-xl text-on-surface-variant hover:bg-white hover:text-on-surface transition-all shadow-ambient-sm"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Image hero */}
          <div className="relative aspect-[4/3] sm:aspect-[16/9] bg-surface-container-high rounded-t-3xl overflow-hidden">
            {imageUrl ? (
              <img
                src={imageUrl}
                alt={artwork.subject}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <span className="text-4xl text-outline/30">No Image</span>
              </div>
            )}
            {/* Tradition badge */}
            <span className="absolute bottom-4 left-4 text-[10px] font-bold uppercase tracking-widest px-4 py-1.5 rounded-full bg-white/90 backdrop-blur-xl text-on-surface-variant">
              {traditionLabel}
            </span>
          </div>

          {/* Content */}
          <div className="p-6 sm:p-8">
            {/* Title + meta */}
            <div className="mb-6">
              <h2 className="font-display text-2xl sm:text-3xl font-bold text-on-surface mb-2">
                {artwork.subject}
              </h2>
              <div className="flex items-center gap-4 text-xs text-on-surface-variant">
                {createdDate && <span>{createdDate}</span>}
                {artwork.total_rounds > 0 && <span>{artwork.total_rounds} round{artwork.total_rounds > 1 ? 's' : ''}</span>}
                {artwork.total_latency_ms > 0 && <span>{(artwork.total_latency_ms / 1000).toFixed(1)}s</span>}
              </div>
            </div>

            {/* Overall score */}
            <div className="flex items-center gap-4 mb-8">
              <div className="text-4xl font-bold text-primary-500">
                {(artwork.overall * 100).toFixed(0)}
              </div>
              <div>
                <div className="text-sm font-semibold text-on-surface">Cultural Score</div>
                <div className="text-xs text-on-surface-variant">Weighted L1-L5 evaluation</div>
              </div>
            </div>

            {/* L1-L5 scores */}
            <div className="space-y-3 mb-8">
              <h3 className="text-[10px] font-black uppercase tracking-widest text-primary-500/70">
                Dimension Analysis
              </h3>
              {sortedDims.map((dim) => {
                const score = scores[dim] ?? 0;
                const pct = Math.round(score * 100);
                const isStrongest = dim === strongest;
                const isWeakest = dim === weakest && strongest !== weakest;
                return (
                  <div key={dim} className="group">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-semibold text-on-surface">
                        {dim} {L_LABELS[dim] || dim}
                        {isStrongest && <span className="ml-1.5 text-cultural-sage-500 text-[10px]">Strongest</span>}
                        {isWeakest && <span className="ml-1.5 text-cultural-coral-500 text-[10px]">Needs work</span>}
                      </span>
                      <span className="text-xs font-bold text-on-surface-variant">{pct}%</span>
                    </div>
                    <div className="h-2 bg-surface-container-high rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-700 ${L_COLORS[dim] || 'bg-primary-500'}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Rationale placeholder — will be populated when API returns rationales */}
            {sortedDims.length > 0 && (
              <div className="bg-surface-container-low/50 p-4 rounded-2xl">
                <h3 className="text-[10px] font-black uppercase tracking-widest text-primary-500/70 mb-3">
                  Cultural Assessment
                </h3>
                <p className="text-xs text-on-surface-variant italic leading-relaxed">
                  {strongest !== weakest
                    ? `This artwork excels in ${L_LABELS[strongest]} (${Math.round((scores[strongest] ?? 0) * 100)}%) while ${L_LABELS[weakest]} (${Math.round((scores[weakest] ?? 0) * 100)}%) presents opportunities for cultural deepening. The overall cultural maturity score of ${Math.round(artwork.overall * 100)}% reflects a balanced evaluation across all five dimensions of the VULCA framework.`
                    : `This artwork achieves consistent scores across all cultural dimensions, reflecting a well-rounded cultural maturity at ${Math.round(artwork.overall * 100)}%.`
                  }
                </p>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
