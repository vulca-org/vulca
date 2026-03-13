/**
 * Tradition auto-detection hook.
 *
 * Tier 1: fast local keyword match (instant).
 * Tier 2: debounced backend heuristic classification (500ms).
 */

import { useEffect, useRef } from 'react';
import { API_PREFIX } from '@/config/api';
import { useCanvasStore } from '@/store/canvasStore';

const PROTO_AUTH = { Authorization: 'Bearer demo-key' } as const;

/** Keyword → tradition mapping for auto-detection from subject text. */
const TRADITION_KEYWORDS: Array<{ keywords: string[]; tradition: string }> = [
  { keywords: ['japanese', 'zen', 'ukiyo', 'wabi', 'sabi'], tradition: 'japanese_wabi_sabi' },
  { keywords: ['persian', 'islamic', 'miniature', 'arabesque'], tradition: 'persian_miniature' },
  { keywords: ['african', 'mask', 'ubuntu'], tradition: 'african_ubuntu' },
  { keywords: ['indian', 'mughal', 'rajput'], tradition: 'indian_miniature' },
  { keywords: ['korean', 'hangul', 'joseon'], tradition: 'korean_minhwa' },
  { keywords: ['western', 'oil', 'renaissance', 'baroque'], tradition: 'western_classical' },
  { keywords: ['aboriginal', 'dreamtime'], tradition: 'aboriginal_dreamtime' },
  { keywords: ['chinese', 'ink', '水墨', '工笔', 'xieyi'], tradition: 'chinese_xieyi' },
];

/** Tier 1: fast local keyword match. Returns tradition or null. */
function detectTraditionLocal(subject: string): string | null {
  const lower = subject.toLowerCase();
  for (const { keywords, tradition } of TRADITION_KEYWORDS) {
    if (keywords.some(kw => lower.includes(kw))) return tradition;
  }
  return null;
}

/** Tier 2: backend heuristic classification. */
async function classifyTraditionRemote(
  subject: string,
): Promise<{ tradition: string; confidence: number; method: string } | null> {
  try {
    const res = await fetch(
      `${API_PREFIX}/prototype/classify-tradition?subject=${encodeURIComponent(subject)}`,
      { headers: PROTO_AUTH },
    );
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

/**
 * Watches `currentSubject` from the canvas store and auto-detects the tradition.
 * Skipped when the user has manually selected a tradition.
 */
export function useTraditionDetection(): void {
  const currentSubject = useCanvasStore((s) => s.currentSubject);
  const traditionManuallySet = useCanvasStore((s) => s.traditionManuallySet);
  const setCurrentTradition = useCanvasStore((s) => s.setCurrentTradition);
  const setTraditionClassifying = useCanvasStore((s) => s.setTraditionClassifying);

  const classifyTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const manualRef = useRef(traditionManuallySet);
  manualRef.current = traditionManuallySet;

  useEffect(() => {
    if (manualRef.current) return;

    if (classifyTimerRef.current) {
      clearTimeout(classifyTimerRef.current);
      classifyTimerRef.current = null;
    }

    if (!currentSubject.trim()) {
      setCurrentTradition('chinese_xieyi');
      setTraditionClassifying(false);
      return;
    }

    // Tier 1: instant local keyword match
    const localResult = detectTraditionLocal(currentSubject);
    if (localResult) {
      setCurrentTradition(localResult);
      setTraditionClassifying(false);
      return;
    }

    // Tier 2: debounced backend heuristic classification
    setTraditionClassifying(true);
    classifyTimerRef.current = setTimeout(async () => {
      const result = await classifyTraditionRemote(currentSubject);
      if (!manualRef.current && result && result.confidence > 0) {
        setCurrentTradition(result.tradition);
      }
      setTraditionClassifying(false);
    }, 500);

    return () => {
      if (classifyTimerRef.current) {
        clearTimeout(classifyTimerRef.current);
      }
    };
  }, [currentSubject, setCurrentTradition, setTraditionClassifying]);
}
