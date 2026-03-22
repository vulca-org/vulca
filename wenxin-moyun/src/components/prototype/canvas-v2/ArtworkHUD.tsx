/**
 * Artwork HUD — Full-bleed artwork with glass overlay elements.
 * Idle state: shows intent input + quick config panel.
 * Running/Complete: shows artwork + status HUD.
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { ArrowRight, ImagePlus, X, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import type { DraftCandidate } from '@/hooks/usePrototypePipeline';
import { API_BASE_URL } from '@/config/api';
import { useCanvasStore } from '@/store/canvasStore';

interface Props {
  bestImageUrl: string | null;
  candidates: DraftCandidate[];
  currentStage: string;
  subject: string;
  pipelineStatus: string;
  onStartPipeline?: (subject: string, tradition: string, provider: string, referenceImageBase64?: string) => void;
  onSelectCandidate?: (candidateId: string) => void;
  selectedCandidateId?: string | null;
}

const FALLBACK_TRADITIONS = [
  { value: 'default', label: 'Auto-detect' },
  { value: 'chinese_xieyi', label: 'Chinese Xieyi' },
  { value: 'chinese_gongbi', label: 'Chinese Gongbi' },
];

function resolveUrl(url: string | undefined | null): string | null {
  if (!url) return null;
  // Already absolute
  if (url.startsWith('data:') || url.startsWith('http://') || url.startsWith('https://')) return url;
  // Non-displayable schemes
  if (url.startsWith('mock://') || url.startsWith('gemini://')) return null;
  // Relative paths — prefix with API base URL
  if (url.startsWith('/')) return `${API_BASE_URL}${url}`;
  return `${API_BASE_URL}/${url}`;
}

const STAGE_LABELS: Record<string, string> = {
  scout: 'Scouting References',
  generate: 'Drafting Artwork',
  draft: 'Drafting Artwork',
  evaluate: 'Analyzing Dimensions',
  critic: 'Analyzing Dimensions',
  decide: 'Queen Deliberating',
};

export default function ArtworkHUD({ bestImageUrl, candidates, currentStage, subject, pipelineStatus, onStartPipeline, onSelectCandidate, selectedCandidateId }: Props) {
  const imageUrl = resolveUrl(bestImageUrl) || (candidates.length > 0 ? resolveUrl(candidates[0].image_url) : null);
  const isIdle = pipelineStatus === 'idle';
  const isRunning = pipelineStatus === 'running';
  const isComplete = pipelineStatus === 'completed';

  // Idle state: intent input
  const [intentText, setIntentText] = useState('');
  const [tradition, setTradition] = useState('default');
  const setStoreProvider = useCanvasStore(s => s.setCurrentProvider);
  const [provider, setProviderLocal] = useState('mock');
  const setProvider = (p: string) => {
    setProviderLocal(p);
    setStoreProvider(p); // Sync to Zustand store so Pipeline Editor Run uses the same provider
  };
  const [showConfig, setShowConfig] = useState(false);
  const [referencePreview, setReferencePreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [traditions, setTraditions] = useState(FALLBACK_TRADITIONS);

  // ── Zoom/Pan state for artwork viewer ──
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const panStart = useRef({ x: 0, y: 0, panX: 0, panY: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  // Register non-passive wheel listener to prevent page scroll when zooming
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const handler = (e: WheelEvent) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? -0.15 : 0.15;
      setZoom(z => Math.max(0.5, Math.min(5, z + delta)));
    };
    el.addEventListener('wheel', handler, { passive: false });
    return () => el.removeEventListener('wheel', handler);
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (zoom <= 1) return;
    setIsPanning(true);
    panStart.current = { x: e.clientX, y: e.clientY, panX: pan.x, panY: pan.y };
  }, [zoom, pan]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isPanning) return;
    setPan({
      x: panStart.current.panX + (e.clientX - panStart.current.x),
      y: panStart.current.panY + (e.clientY - panStart.current.y),
    });
  }, [isPanning]);

  const handleMouseUp = useCallback(() => setIsPanning(false), []);
  const resetView = useCallback(() => { setZoom(1); setPan({ x: 0, y: 0 }); }, []);

  // WU-4: Dynamic traditions loading from backend API
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/prototype/traditions`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data?.traditions?.length) {
          setTraditions([
            { value: 'default', label: 'Auto-detect' },
            ...data.traditions
              .filter((t: { name: string }) => t.name !== 'default')
              .map((t: { name: string; display_name?: string }) => ({
                value: t.name,
                label: t.display_name || t.name.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase()),
              })),
          ]);
        }
      })
      .catch(() => {}); // Use fallback silently
  }, []);

  const handleSubmit = () => {
    if (!intentText.trim() || !onStartPipeline) return;
    const refB64 = referencePreview?.replace(/^data:image\/[^;]+;base64,/, '') || undefined;
    onStartPipeline(intentText.trim(), tradition, provider, refB64);
  };

  const handleReferenceImage = useCallback((file: File) => {
    if (!file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = () => {
      setReferencePreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleReferenceImage(file);
  }, [handleReferenceImage]);

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

          {/* Reference image — always visible drop zone */}
          <div className="mb-4">
            {referencePreview ? (
              <div className="flex items-center gap-3">
                <div className="relative">
                  <img src={referencePreview} alt="Reference" className="w-16 h-16 rounded-xl object-cover shadow-ambient-md" />
                  <button
                    onClick={() => setReferencePreview(null)}
                    className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-on-surface text-white rounded-full flex items-center justify-center text-[10px] hover:bg-cultural-coral-500 transition-colors"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
                <div>
                  <p className="text-[11px] font-semibold text-on-surface">Reference image</p>
                  <p className="text-[10px] text-on-surface-variant">Style will guide generation</p>
                </div>
              </div>
            ) : (
              <label className={`flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer transition-all ${
                isDragging
                  ? 'bg-primary-50 ring-2 ring-primary-500'
                  : 'bg-surface-container-high/50 hover:bg-surface-container-high'
              }`}>
                <ImagePlus className="w-5 h-5 text-on-surface-variant/60 shrink-0" />
                <div>
                  <p className="text-[11px] text-on-surface-variant">
                    {isDragging ? 'Drop here' : 'Add reference image'} <span className="text-outline">(optional)</span>
                  </p>
                </div>
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleReferenceImage(file);
                    e.target.value = '';
                  }}
                />
              </label>
            )}
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
                    {traditions.map((t) => (
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
            <div
              key={c.candidate_id}
              className={`relative rounded-xl overflow-hidden bg-surface-container-high cursor-pointer hover:ring-2 hover:ring-primary-500 transition-all group ${
                selectedCandidateId === c.candidate_id ? 'ring-2 ring-primary-500 ring-offset-2' : ''
              }`}
              onClick={() => onSelectCandidate?.(c.candidate_id)}
            >
              <img src={c.resolvedUrl!} alt={c.prompt || subject} className="w-full h-full object-cover" onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none'; }} />
              <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                <span className="text-white text-[10px] font-medium">
                  {selectedCandidateId === c.candidate_id ? 'Selected' : 'Select this candidate'}
                </span>
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
        <div
          ref={containerRef}
          className="w-full h-full overflow-auto"
          style={{ cursor: isPanning ? 'grabbing' : 'grab' }}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          <img
            src={imageUrl}
            alt={subject || 'VULCA artwork'}
            className="select-none"
            draggable={false}
            style={{
              width: `${zoom * 100}%`,
              minWidth: '100%',
              height: 'auto',
              display: 'block',
              transform: `translate(${pan.x}px, ${pan.y}px)`,
              transition: isPanning ? 'none' : 'transform 0.2s ease-out',
            }}
            onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none'; }}
          />
        </div>
      ) : (
        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-surface-container to-surface-container-high">
          <div className="text-center">
            <span className="text-6xl block mb-4 opacity-20">🎨</span>
            <p className="text-sm text-on-surface-variant">
              {isRunning ? 'Generating artwork with cultural guidance...' : 'Waiting for pipeline...'}
            </p>
            {isRunning && (
              <p className="text-[11px] text-outline mt-2">Typically 1-2 minutes for Gemini generation + L1-L5 evaluation</p>
            )}
          </div>
        </div>
      )}

      {/* Zoom controls */}
      {imageUrl && (
        <div className="absolute bottom-4 left-4 pointer-events-auto flex items-center gap-1 bg-white/80 backdrop-blur-xl rounded-full px-2 py-1 shadow-ambient-md z-10">
          <button onClick={() => setZoom(z => Math.max(0.5, z - 0.25))} className="w-7 h-7 flex items-center justify-center rounded-full hover:bg-surface-container-high transition-colors" title="Zoom out">
            <ZoomOut className="w-3.5 h-3.5 text-on-surface-variant" />
          </button>
          <span className="text-[10px] font-medium text-on-surface-variant min-w-[36px] text-center">{Math.round(zoom * 100)}%</span>
          <button onClick={() => setZoom(z => Math.min(5, z + 0.25))} className="w-7 h-7 flex items-center justify-center rounded-full hover:bg-surface-container-high transition-colors" title="Zoom in">
            <ZoomIn className="w-3.5 h-3.5 text-on-surface-variant" />
          </button>
          {zoom !== 1 && (
            <button onClick={resetView} className="w-7 h-7 flex items-center justify-center rounded-full hover:bg-surface-container-high transition-colors" title="Reset view">
              <Maximize2 className="w-3.5 h-3.5 text-on-surface-variant" />
            </button>
          )}
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
