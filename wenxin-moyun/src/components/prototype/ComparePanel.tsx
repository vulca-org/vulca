/**
 * M7.3 Compare Mode — multi-image cultural evaluation comparison.
 *
 * Drop 2-6 images, auto-detect tradition, overlay L1-L5 radar charts.
 * Each image calls /api/v1/evaluate independently.
 */

import { useState, useCallback } from 'react';
import { IOSButton, IOSCard, IOSCardContent } from '../ios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const L_LABELS: Record<string, string> = {
  L1: 'Visual Perception',
  L2: 'Technical Analysis',
  L3: 'Cultural Context',
  L4: 'Critical Interpretation',
  L5: 'Philosophical Aesthetic',
};

interface EvalResult {
  id: string;
  filename: string;
  imageUrl: string;
  scores: Record<string, number>;
  weightedTotal: number;
  tradition: string;
  status: 'pending' | 'loading' | 'done' | 'error';
  error?: string;
}

function ScoreBar({ score, color }: { score: number; color: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${score * 100}%`, backgroundColor: color }}
        />
      </div>
      <span className="text-[11px] font-mono w-10 text-right">{score.toFixed(3)}</span>
    </div>
  );
}

const COLORS = ['#007AFF', '#34C759', '#FF9500', '#AF52DE', '#FF2D55', '#5AC8FA'];

export default function ComparePanel() {
  const [results, setResults] = useState<EvalResult[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const fileToBase64 = (file: File): Promise<string> =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        resolve(result.split(',')[1]); // strip data:... prefix
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });

  const evaluateImage = useCallback(async (id: string, base64: string) => {
    setResults(prev =>
      prev.map(r => (r.id === id ? { ...r, status: 'loading' as const } : r))
    );

    try {
      const resp = await fetch(`${API_BASE}/api/v1/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_base64: base64 }),
      });

      if (!resp.ok) throw new Error(`API ${resp.status}`);

      const data = await resp.json();
      setResults(prev =>
        prev.map(r =>
          r.id === id
            ? {
                ...r,
                status: 'done' as const,
                scores: data.scores || {},
                weightedTotal: data.weighted_total || 0,
                tradition: data.tradition_used || 'unknown',
              }
            : r
        )
      );
    } catch (e) {
      setResults(prev =>
        prev.map(r =>
          r.id === id
            ? { ...r, status: 'error' as const, error: String(e) }
            : r
        )
      );
    }
  }, []);

  const handleFiles = useCallback(
    async (files: FileList) => {
      const imageFiles = Array.from(files)
        .filter(f => f.type.startsWith('image/'))
        .slice(0, 6 - results.length); // max 6

      const newResults: EvalResult[] = [];

      for (const file of imageFiles) {
        const id = crypto.randomUUID();
        const url = URL.createObjectURL(file);
        newResults.push({
          id,
          filename: file.name,
          imageUrl: url,
          scores: {},
          weightedTotal: 0,
          tradition: '',
          status: 'pending',
        });
      }

      setResults(prev => [...prev, ...newResults]);

      // Evaluate each image
      for (const nr of newResults) {
        const file = imageFiles[newResults.indexOf(nr)];
        const b64 = await fileToBase64(file);
        evaluateImage(nr.id, b64);
      }
    },
    [results.length, evaluateImage]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      if (e.dataTransfer.files.length > 0) {
        handleFiles(e.dataTransfer.files);
      }
    },
    [handleFiles]
  );

  const removeResult = (id: string) => {
    setResults(prev => {
      const r = prev.find(x => x.id === id);
      if (r) URL.revokeObjectURL(r.imageUrl);
      return prev.filter(x => x.id !== id);
    });
  };

  const doneResults = results.filter(r => r.status === 'done');

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <div
        className={[
          'border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer',
          isDragging
            ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-blue-300',
          results.length >= 6 ? 'opacity-50 pointer-events-none' : '',
        ].join(' ')}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => {
          if (results.length >= 6) return;
          const input = document.createElement('input');
          input.type = 'file';
          input.accept = 'image/*';
          input.multiple = true;
          input.onchange = (e) => {
            const files = (e.target as HTMLInputElement).files;
            if (files) handleFiles(files);
          };
          input.click();
        }}
      >
        <div className="text-3xl mb-2">🖼️</div>
        <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Drop 2-6 images to compare
        </div>
        <div className="text-xs text-gray-500 mt-1">
          {results.length}/6 images loaded
        </div>
      </div>

      {/* Image Cards Grid */}
      {results.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {results.map((r, idx) => (
            <IOSCard key={r.id} variant="elevated" padding="sm" animate={false}>
              <IOSCardContent>
                <div className="relative">
                  <img
                    src={r.imageUrl}
                    alt={r.filename}
                    className="w-full h-32 object-cover rounded-lg"
                  />
                  <button
                    onClick={() => removeResult(r.id)}
                    className="absolute top-1 right-1 w-5 h-5 bg-black/50 rounded-full text-white text-xs flex items-center justify-center hover:bg-black/70"
                  >
                    ×
                  </button>
                  {/* Color indicator */}
                  <div
                    className="absolute top-1 left-1 w-3 h-3 rounded-full border border-white"
                    style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                  />
                </div>

                <div className="mt-2 text-xs truncate text-gray-600 dark:text-gray-400">
                  {r.filename}
                </div>

                {r.status === 'loading' && (
                  <div className="mt-2 text-xs text-blue-500 animate-pulse">Evaluating...</div>
                )}

                {r.status === 'error' && (
                  <div className="mt-2 text-xs text-red-500">{r.error}</div>
                )}

                {r.status === 'done' && (
                  <div className="mt-2 space-y-1">
                    <div className="flex justify-between text-[11px]">
                      <span className="text-gray-500">{r.tradition}</span>
                      <span className="font-semibold">{r.weightedTotal.toFixed(3)}</span>
                    </div>
                    {Object.entries(L_LABELS).map(([key]) => (
                      <ScoreBar
                        key={key}
                        score={r.scores[key] || 0}
                        color={COLORS[idx % COLORS.length]}
                      />
                    ))}
                  </div>
                )}
              </IOSCardContent>
            </IOSCard>
          ))}
        </div>
      )}

      {/* Comparison Overlay Radar */}
      {doneResults.length >= 2 && (
        <IOSCard variant="elevated" padding="md" animate={false}>
          <IOSCardContent>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
              L1-L5 Comparison
            </h3>
            {/* SVG Radar Chart */}
            <OverlayRadar results={doneResults} />

            {/* Difference table */}
            <div className="mt-4">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-gray-500 border-b dark:border-gray-700">
                    <th className="text-left py-1">Dimension</th>
                    {doneResults.map((r) => (
                      <th key={r.id} className="text-right py-1">
                        <span
                          className="inline-block w-2 h-2 rounded-full mr-1"
                          style={{ backgroundColor: COLORS[results.indexOf(r) % COLORS.length] }}
                        />
                        {r.filename.slice(0, 12)}
                      </th>
                    ))}
                    <th className="text-right py-1">Max Gap</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(L_LABELS).map(([key, label]) => {
                    const values = doneResults.map(r => r.scores[key] || 0);
                    const gap = Math.max(...values) - Math.min(...values);
                    return (
                      <tr key={key} className="border-b dark:border-gray-800">
                        <td className="py-1 text-gray-700 dark:text-gray-300">{label}</td>
                        {doneResults.map((r) => (
                          <td key={r.id} className="text-right font-mono py-1">
                            {(r.scores[key] || 0).toFixed(3)}
                          </td>
                        ))}
                        <td className={`text-right font-mono py-1 ${gap > 0.1 ? 'text-red-500 font-bold' : 'text-gray-400'}`}>
                          {gap.toFixed(3)}
                        </td>
                      </tr>
                    );
                  })}
                  <tr className="font-semibold">
                    <td className="py-1">Weighted Total</td>
                    {doneResults.map(r => (
                      <td key={r.id} className="text-right font-mono py-1">{r.weightedTotal.toFixed(3)}</td>
                    ))}
                    <td className="text-right font-mono py-1">
                      {(Math.max(...doneResults.map(r => r.weightedTotal)) - Math.min(...doneResults.map(r => r.weightedTotal))).toFixed(3)}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </IOSCardContent>
        </IOSCard>
      )}

      {/* Actions */}
      {results.length > 0 && (
        <div className="flex gap-2">
          <IOSButton
            variant="secondary"
            size="sm"
            onClick={() => {
              results.forEach(r => URL.revokeObjectURL(r.imageUrl));
              setResults([]);
            }}
          >
            Clear All
          </IOSButton>
        </div>
      )}
    </div>
  );
}

/** SVG radar chart overlaying multiple results */
function OverlayRadar({ results }: { results: EvalResult[] }) {
  const dims = ['L1', 'L2', 'L3', 'L4', 'L5'];
  const cx = 150, cy = 150, radius = 110;
  const angleStep = (2 * Math.PI) / dims.length;

  const getPoint = (dimIdx: number, value: number) => {
    const angle = -Math.PI / 2 + dimIdx * angleStep;
    return {
      x: cx + radius * value * Math.cos(angle),
      y: cy + radius * value * Math.sin(angle),
    };
  };

  return (
    <svg viewBox="0 0 300 300" className="w-full max-w-[300px] mx-auto">
      {/* Grid circles */}
      {[0.2, 0.4, 0.6, 0.8, 1.0].map(v => (
        <circle
          key={v}
          cx={cx} cy={cy} r={radius * v}
          fill="none"
          stroke="currentColor"
          strokeOpacity={0.1}
          strokeWidth={1}
        />
      ))}

      {/* Axis lines + labels */}
      {dims.map((dim, i) => {
        const pt = getPoint(i, 1);
        const labelPt = getPoint(i, 1.15);
        return (
          <g key={dim}>
            <line x1={cx} y1={cy} x2={pt.x} y2={pt.y} stroke="currentColor" strokeOpacity={0.15} strokeWidth={1} />
            <text
              x={labelPt.x} y={labelPt.y}
              textAnchor="middle" dominantBaseline="middle"
              className="text-[10px] fill-gray-500"
            >
              {dim}
            </text>
          </g>
        );
      })}

      {/* Data polygons */}
      {results.map((r, rIdx) => {
        const allResults = results; // use parent scope
        const color = COLORS[allResults.indexOf(r) % COLORS.length] || COLORS[rIdx % COLORS.length];
        const points = dims.map((dim, i) => {
          const pt = getPoint(i, r.scores[dim] || 0);
          return `${pt.x},${pt.y}`;
        }).join(' ');

        return (
          <g key={r.id}>
            <polygon
              points={points}
              fill={color}
              fillOpacity={0.1}
              stroke={color}
              strokeWidth={2}
              strokeOpacity={0.8}
            />
            {dims.map((dim, i) => {
              const pt = getPoint(i, r.scores[dim] || 0);
              return (
                <circle key={dim} cx={pt.x} cy={pt.y} r={3} fill={color} />
              );
            })}
          </g>
        );
      })}
    </svg>
  );
}
