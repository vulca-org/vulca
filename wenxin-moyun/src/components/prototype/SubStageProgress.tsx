/**
 * Timeline showing sub-stage progress within a pipeline stage.
 *
 * Displays each sub-step with a status icon, optional duration,
 * expandable text content, and image preview when available.
 * Uses Art Professional color palette.
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronRight, RefreshCw, Image as ImageIcon } from 'lucide-react';
import { API_BASE_URL } from '../../config/api';

export interface SubStage {
  name: string;
  displayName: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  durationMs?: number;
  /** Text content produced by this sub-stage */
  data?: string;
  /** Path to visual artifact (NB2-rendered image) */
  imagePath?: string;
  /** Artifact type: "text" | "json" | "image" */
  artifactType?: string;
}

interface Props {
  stages: SubStage[];
  recipeName?: string;
  /** Callback to regenerate a specific sub-stage */
  onRegenerate?: (stageName: string) => void;
}

const STATUS_CONFIG: Record<SubStage['status'], { icon: string; className: string }> = {
  completed: { icon: '\u2713', className: 'text-[#5F8A50]' },
  running:   { icon: '\u25CC', className: 'text-[#C87F4A] animate-pulse' },
  pending:   { icon: '\u25CB', className: 'text-gray-400' },
  failed:    { icon: '\u2715', className: 'text-[#C65D4D]' },
  skipped:   { icon: '\u2013', className: 'text-gray-300' },
};

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

/** Truncate text to maxLen and add ellipsis */
function truncate(text: string, maxLen: number): string {
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen) + '...';
}

export default function SubStageProgress({ stages, recipeName, onRegenerate }: Props) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  if (stages.length === 0) return null;

  const toggleExpand = (name: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  };

  const hasContent = (s: SubStage) => s.data || s.imagePath;

  /** Convert backend /static/ path to full URL */
  const resolveImageUrl = (path?: string): string | undefined => {
    if (!path) return undefined;
    if (path.startsWith('http://') || path.startsWith('https://') || path.startsWith('data:')) return path;
    const normalized = path.startsWith('/') ? path : `/${path}`;
    return `${API_BASE_URL}${normalized}`;
  };

  return (
    <div className="bg-surface-container-low border-l-2 border-[#C87F4A] pl-4 py-3 rounded-r-lg">
      {recipeName && (
        <p className="text-xs font-medium text-[#C87F4A] dark:text-[#DDA574] mb-2">
          {recipeName}
        </p>
      )}
      <div className="space-y-1">
        {stages.map((s) => {
          const cfg = STATUS_CONFIG[s.status];
          const isExpanded = expanded.has(s.name);
          const expandable = s.status === 'completed' && hasContent(s);

          return (
            <div key={s.name}>
              {/* Header row */}
              <div
                className={`flex items-center gap-2 text-xs ${expandable ? 'cursor-pointer hover:bg-[#F0EDE6] dark:hover:bg-gray-700/30 -mx-1 px-1 rounded' : ''}`}
                onClick={expandable ? () => toggleExpand(s.name) : undefined}
              >
                <span className={`w-4 text-center font-mono ${cfg.className}`}>
                  {cfg.icon}
                </span>

                {/* Expand chevron */}
                {expandable ? (
                  <span className="text-gray-400 w-3">
                    {isExpanded
                      ? <ChevronDown className="w-3 h-3" />
                      : <ChevronRight className="w-3 h-3" />
                    }
                  </span>
                ) : (
                  <span className="w-3" />
                )}

                <span className={`flex-1 ${s.status === 'skipped' ? 'text-gray-300 dark:text-gray-600' : 'text-gray-700 dark:text-gray-300'}`}>
                  {s.displayName}
                </span>

                {/* Image indicator */}
                {s.imagePath && (
                  <ImageIcon className="w-3 h-3 text-[#C87F4A]" />
                )}

                {s.durationMs != null && (
                  <span className="font-mono text-gray-400 dark:text-gray-500">
                    {formatDuration(s.durationMs)}
                  </span>
                )}

                {/* Regenerate button */}
                {onRegenerate && s.status === 'completed' && (
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); onRegenerate(s.name); }}
                    className="p-0.5 rounded hover:bg-[#C87F4A]/10 text-gray-400 hover:text-[#C87F4A] transition-colors"
                    title="Regenerate this stage"
                  >
                    <RefreshCw className="w-3 h-3" />
                  </button>
                )}
              </div>

              {/* Expanded content */}
              <AnimatePresence>
                {isExpanded && expandable && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="ml-9 mt-1.5 mb-2 space-y-2">
                      {/* Image preview */}
                      {resolveImageUrl(s.imagePath) && (
                        <div className="rounded-lg overflow-hidden border border-[#C87F4A]/20 max-w-[280px]">
                          <img
                            src={resolveImageUrl(s.imagePath)}
                            alt={s.displayName}
                            className="w-full h-auto object-cover"
                            loading="lazy"
                          />
                        </div>
                      )}

                      {/* Text content */}
                      {s.data && (
                        <div className="text-[11px] leading-relaxed text-gray-600 dark:text-gray-400 bg-white/60 dark:bg-gray-900/30 rounded-md px-2.5 py-2 border border-gray-200/50 dark:border-gray-700/50">
                          {s.artifactType === 'json' ? (
                            <pre className="whitespace-pre-wrap font-mono">
                              {truncate(s.data, 500)}
                            </pre>
                          ) : (
                            <p className="whitespace-pre-wrap">
                              {truncate(s.data, 500)}
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </div>
  );
}
