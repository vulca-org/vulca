/**
 * useRunHistory — fetches recent pipeline runs from the Gallery API
 * for display in the Run History panel on Canvas.
 */

import { useState, useEffect, useCallback } from 'react';
import { API_PREFIX, getProtoAuthHeaders } from '../config/api';

export interface RunHistoryItem {
  id: string;
  subject: string;
  tradition: string;
  overall: number;
  scores: Record<string, number>;
  best_image_url: string;
  total_rounds: number;
  total_latency_ms: number;
  created_at: number;
}

interface UseRunHistoryReturn {
  items: RunHistoryItem[];
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

export function useRunHistory(limit = 10): UseRunHistoryReturn {
  const [items, setItems] = useState<RunHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `${API_PREFIX}/prototype/gallery?limit=${limit}&sort_by=newest`,
        { headers: getProtoAuthHeaders() },
      );
      if (!res.ok) throw new Error(`Gallery API ${res.status}`);
      const data = await res.json();
      const raw: RunHistoryItem[] = data.items ?? [];

      // Deduplicate: by id first, then collapse entries with identical subject+score+timestamp
      const seenIds = new Set<string>();
      const seenKeys = new Set<string>();
      const deduped: RunHistoryItem[] = [];
      for (const item of raw) {
        if (seenIds.has(item.id)) continue;
        seenIds.add(item.id);
        const compositeKey = `${item.subject}|${item.overall}|${item.created_at}`;
        if (seenKeys.has(compositeKey)) continue;
        seenKeys.add(compositeKey);
        deduped.push(item);
      }
      setItems(deduped);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load history');
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return { items, loading, error, refresh: fetchHistory };
}
