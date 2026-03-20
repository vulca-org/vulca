/**
 * Artwork HUD — Full-bleed artwork with glass overlay elements.
 * Idle state: shows intent input + quick config panel.
 * Running/Complete: shows artwork + status HUD.
 */

import { useState } from 'react';
import { ArrowRight } from 'lucide-react';
import type { DraftCandidate } from '@/hooks/usePrototypePipeline';
import { API_BASE_URL } from '@/config/api';

interface Props {
  bestImageUrl: string | null;
  candidates: DraftCandidate[];
  currentStage: string;
  subject: string;
  pipelineStatus: string;
  onStartPipeline?: (subject: string, tradition: string, provider: string) => void;
}

const TRADITIONS = [
  { value: 'default', label: 'Auto-detect' },
  { value: 'chinese_xieyi', label: 'Chinese Xieyi' },
  { value: 'chinese_gongbi', label: 'Chinese Gongbi' },
  { value: 'japanese_wabi_sabi', label: 'Japanese Wabi-Sabi' },
  { value: 'persian_miniature', label: 'Persian Miniature' },
  { value: 'western_classical', label: 'Western Classical' },
  { value: 'african_ubuntu', label: 'African Ubuntu' },
  { value: 'indian_miniature', label: 'Indian Miniature' },
  { value: 'korean_minhwa', label: 'Korean Minhwa' },
];

function resolveUrl(url: string | undefined | null): string | null {
  if (!url) return null;
  if (url.startsWith('data:') || url.startsWith('http://') || url.startsWith('https://')) return url;
  if (url.startsWith('/static/') || url.startsWith('static/')) {
    return `${API_BASE_URL}${url.startsWith('/') ? url : `/${url}`}`;
  }
  return url;
}

const STAGE_LABELS: Record<string, string> = {
  scout: 'Scouting References',
  generate: 'Drafting Artwork',
  draft: 'Drafting Artwork',
  evaluate: 'Analyzing Dimensions',
  critic: 'Analyzing Dimensions',
  decide: 'Queen Deliberating',
};

export default function ArtworkHUD({ bestImageUrl, candidates, currentStage, subject, pipelineStatus, onStartPipeline }: Props) {
  const imageUrl = resolveUrl(bestImageUrl) || (candidates.length > 0 ? resolveUrl(candidates[0].image_url) : null);
  const isIdle = pipelineStatus === 'idle';
  const isRunning = pipelineStatus === 'running';
  const isComplete = pipelineStatus === 'completed';

  // Idle state: intent input
  const [intentText, setIntentText] = useState('');
  const [tradition, setTradition] = useState('default');
  const [provider, setProvider] = useState('mock');
  const [showConfig, setShowConfig] = useState(false);

  const handleSubmit = () => {
    if (!intentText.trim() || !onStartPipeline) return;
    onStartPipeline(intentText.trim(), tradition, provider);
  };

  const stageLabel = STAGE_LABELS[currentStage] || (currentStage ? currentStage.replace(/_/g, ' ') : 'Initializing');

  // ── Idle state: input form ──
  if (isIdle && !imageUrl) {
    return (
      <div className="flex-1 relative rounded-2xl overflow-hidden bg-surface-container-lowest flex flex-col items-center justify-center p-8">
        <div className="max-w-lg w-full text-center">
          <div className="text-5xl mb-6 opacity-30">🎨</div>
          <h2 className="font-display text-2xl font-bold text-on-surface mb-2">Create Cultural Art</h2>
          <p className="text-sm text-on-surface-variant mb-8">Describe your creation intent and let the AI Collective bring it to life.</p>

          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={intentText}
              onChange={(e) => setIntentText(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') { if (showConfig) { handleSubmit(); } else { setShowConfig(true); } } }}
              placeholder="e.g. 水墨山水, Edo-period landscape, Persian garden..."
              className="flex-1 px-5 py-3.5 bg-surface-container-high rounded-xl text-on-surface text-sm placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:bg-surface-container-lowest transition-all"
            />
            <button
              onClick={() => { if (intentText.trim()) setShowConfig(true); }}
              disabled={!intentText.trim()}
              className="bg-primary-500 text-white px-6 py-3.5 rounded-xl font-medium text-sm hover:bg-primary-600 active:scale-95 transition-all disabled:opacity-40 disabled:pointer-events-none flex items-center gap-2"
            >
              Next <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Quick config panel */}
          {showConfig && (
            <div className="bg-surface-container-low rounded-xl p-5 text-left animate-fade-in">
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="text-[11px] font-bold uppercase tracking-widest text-outline block mb-2">Tradition</label>
                  <select
                    value={tradition}
                    onChange={(e) => setTradition(e.target.value)}
                    className="w-full px-4 py-2.5 bg-surface-container-lowest rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                  >
                    {TRADITIONS.map((t) => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-[11px] font-bold uppercase tracking-widest text-outline block mb-2">Mode</label>
                  <select
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                    className="w-full px-4 py-2.5 bg-surface-container-lowest rounded-lg text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                  >
                    <option value="mock">Preview (free, instant)</option>
                    <option value="auto">Generate (requires API key)</option>
                  </select>
                </div>
              </div>
              <button
                onClick={handleSubmit}
                className="w-full bg-primary-500 text-white py-3 rounded-xl font-semibold text-sm hover:bg-primary-600 active:scale-[0.98] transition-all shadow-lg shadow-primary-500/20"
              >
                Start Pipeline
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  // ── Running / Complete state: artwork + HUD ──
  return (
    <div className="flex-1 relative rounded-2xl overflow-hidden bg-surface-container-high shadow-ambient-xl group">
      {imageUrl ? (
        <img
          src={imageUrl}
          alt={subject || 'VULCA artwork'}
          className="w-full h-full object-cover"
          onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none'; }}
        />
      ) : (
        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-surface-container to-surface-container-high">
          <div className="text-center">
            <span className="text-6xl block mb-4 opacity-20">🎨</span>
            <p className="text-sm text-on-surface-variant">
              {isRunning ? 'Generating artwork...' : 'Waiting for pipeline...'}
            </p>
          </div>
        </div>
      )}

      {/* Glass HUD overlay */}
      <div className="absolute inset-0 pointer-events-none p-6 flex flex-col justify-between">
        <div className="flex justify-between items-start">
          {(isRunning || isComplete) && (
            <div className="pointer-events-auto bg-white/70 backdrop-blur-xl rounded-lg p-3 shadow-ambient-md max-w-xs">
              <h3 className="text-[10px] font-black uppercase tracking-wider text-primary-600 mb-1">
                {isComplete ? 'Analysis Complete' : 'Synthesis Node'}
              </h3>
              <p className="text-base font-bold text-on-surface leading-tight line-clamp-2">
                {subject || 'Untitled Artwork'}
              </p>
              {isRunning && (
                <div className="flex items-center gap-2 mt-2">
                  <span className="w-2 h-2 rounded-full bg-primary-500 animate-pulse" />
                  <span className="text-[10px] font-medium text-on-surface-variant uppercase tracking-widest">
                    {stageLabel}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>

        {isRunning && (
          <>
            <div className="absolute top-[30%] left-[45%] w-12 h-12 flex items-center justify-center">
              <div className="absolute inset-0 rounded-full bg-primary-500/30 animate-ping" />
              <div className="w-3 h-3 rounded-full bg-primary-500 border-2 border-white" />
            </div>
            <div className="absolute top-[60%] left-[25%] w-12 h-12 flex items-center justify-center">
              <div className="w-3 h-3 rounded-full bg-primary-500/60 border-2 border-white" />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
