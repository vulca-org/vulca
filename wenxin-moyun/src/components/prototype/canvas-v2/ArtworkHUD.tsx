/**
 * Artwork HUD — Full-bleed artwork with glass overlay elements.
 * Idle state: shows intent input + quick config panel.
 * Running/Complete: shows artwork + status HUD.
 */

import { useState, useCallback } from 'react';
import { ArrowRight, ImagePlus, X } from 'lucide-react';
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
  const [referencePreview, setReferencePreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleSubmit = () => {
    if (!intentText.trim() || !onStartPipeline) return;
    onStartPipeline(intentText.trim(), tradition, provider);
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (!file || !file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = () => {
      setReferencePreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const stageLabel = STAGE_LABELS[currentStage] || (currentStage ? currentStage.replace(/_/g, ' ') : 'Initializing');

  // ── Idle state: input form ──
  if (isIdle && !imageUrl) {
    return (
      <div
        className={`flex-1 relative rounded-2xl overflow-hidden bg-surface-container-lowest flex flex-col items-center justify-center p-8 transition-all ${isDragging ? 'ring-2 ring-primary-500 ring-offset-2' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
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

          {/* Reference image preview */}
          {referencePreview && (
            <div className="mb-4 relative inline-block">
              <img src={referencePreview} alt="Reference" className="w-20 h-20 rounded-xl object-cover shadow-ambient-md" />
              <button
                onClick={() => setReferencePreview(null)}
                className="absolute -top-2 -right-2 w-5 h-5 bg-on-surface text-white rounded-full flex items-center justify-center text-[10px] hover:bg-error-500 transition-colors"
              >
                <X className="w-3 h-3" />
              </button>
              <span className="text-[9px] text-on-surface-variant mt-1 block">Reference</span>
            </div>
          )}

          {/* Drop hint */}
          {isDragging && (
            <div className="mb-4 flex items-center gap-2 text-primary-500 text-sm font-medium animate-pulse">
              <ImagePlus className="w-5 h-5" />
              Drop reference image here
            </div>
          )}

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

              {/* Reference image upload (if not already dropped) */}
              {!referencePreview && (
                <label className="block mb-4 cursor-pointer">
                  <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-surface-container-lowest text-on-surface-variant text-sm hover:bg-surface-container-high transition-colors">
                    <ImagePlus className="w-4 h-4" />
                    <span>Add reference image (optional)</span>
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (!file) return;
                      e.target.value = '';
                      const reader = new FileReader();
                      reader.onload = () => setReferencePreview(reader.result as string);
                      reader.readAsDataURL(file);
                    }}
                  />
                </label>
              )}

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

  // ── Multiple candidates: show grid for user to pick ──
  const resolvedCandidates = candidates.map(c => ({ ...c, resolvedUrl: resolveUrl(c.image_url) })).filter(c => c.resolvedUrl);
  const showCandidateGrid = resolvedCandidates.length > 1 && !bestImageUrl && isRunning;

  if (showCandidateGrid) {
    return (
      <div className="flex-1 relative rounded-2xl overflow-hidden bg-surface-container-lowest p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-[11px] font-bold uppercase tracking-widest text-primary-500">Candidates — Round {candidates[0]?.seed ? '1' : '?'}</h3>
          <span className="text-[10px] text-on-surface-variant">Click to select best</span>
        </div>
        <div className="grid grid-cols-2 gap-3 h-[calc(100%-2rem)]">
          {resolvedCandidates.slice(0, 4).map((c) => (
            <div key={c.candidate_id} className="relative rounded-xl overflow-hidden bg-surface-container-high cursor-pointer hover:ring-2 hover:ring-primary-500 transition-all group">
              <img src={c.resolvedUrl!} alt={c.prompt || subject} className="w-full h-full object-cover" onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none'; }} />
              <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                <span className="text-white text-[10px] font-medium">Select this candidate</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // ── Running / Complete state: single artwork + HUD ──
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
