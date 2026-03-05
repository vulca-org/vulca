/**
 * BatchInputPanel — batch evaluation mode for running multiple subjects.
 *
 * Visible when template === 'batch_eval' and edit mode is active.
 * Supports multi-line text input (one subject per line) and CSV drag-drop.
 * Runs N sequential POST /runs, polls GET /runs/{id} for completion,
 * then shows a summary table with CSV export.
 */

import { useState, useCallback, useRef } from 'react';
import { IOSButton } from '../ios';
import { API_PREFIX } from '../../config/api';

interface BatchResult {
  subject: string;
  taskId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  scores: Record<string, number>;
  total: number | null;
  error?: string;
}

interface Props {
  tradition: string;
  provider: string;
  template: string;
  disabled?: boolean;
}

function parseCSV(text: string): string[] {
  return text
    .split('\n')
    .map((line) => line.split(',')[0]?.trim())
    .filter(Boolean);
}

export default function BatchInputPanel({ tradition, provider, template, disabled }: Props) {
  const [input, setInput] = useState('');
  const [results, setResults] = useState<BatchResult[]>([]);
  const [running, setRunning] = useState(false);
  const abortRef = useRef(false);

  const subjects = input
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target?.result as string;
      const parsed = parseCSV(text);
      setInput(parsed.join('\n'));
    };
    reader.readAsText(file);
  }, []);

  const pollForCompletion = async (taskId: string): Promise<{ status: string; scores: Record<string, number>; total: number | null; error?: string }> => {
    for (let i = 0; i < 300; i++) {
      if (abortRef.current) return { status: 'failed', scores: {}, total: null, error: 'Aborted' };
      await new Promise((r) => setTimeout(r, 1000));
      try {
        const res = await fetch(`${API_PREFIX}/prototype/runs/${taskId}`);
        if (!res.ok) continue;
        const data = await res.json();
        if (data.status === 'completed' || data.status === 'failed') {
          // Extract scores from stages if available
          const scores: Record<string, number> = {};
          let total: number | null = null;
          for (const stage of data.stages || []) {
            if (stage.stage === 'critic' && stage.payload?.scored_candidates) {
              const best = stage.payload.scored_candidates[0];
              if (best) {
                for (const ds of best.dimension_scores || []) {
                  scores[ds.dimension] = ds.score;
                }
                total = best.weighted_total ?? null;
              }
            }
          }
          return { status: data.status, scores, total, error: data.error };
        }
      } catch {
        // Retry
      }
    }
    return { status: 'failed', scores: {}, total: null, error: 'Timeout' };
  };

  const handleRun = async () => {
    if (subjects.length === 0) return;
    setRunning(true);
    abortRef.current = false;

    const initial: BatchResult[] = subjects.map((s) => ({
      subject: s,
      taskId: '',
      status: 'pending',
      scores: {},
      total: null,
    }));
    setResults(initial);

    for (let i = 0; i < subjects.length; i++) {
      if (abortRef.current) break;

      setResults((prev) =>
        prev.map((r, idx) => (idx === i ? { ...r, status: 'running' } : r)),
      );

      try {
        const res = await fetch(`${API_PREFIX}/prototype/runs`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            subject: subjects[i],
            tradition,
            provider,
            template,
            n_candidates: 4,
            max_rounds: 1,
            use_graph: false,
          }),
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const { task_id } = await res.json();

        setResults((prev) =>
          prev.map((r, idx) => (idx === i ? { ...r, taskId: task_id } : r)),
        );

        const result = await pollForCompletion(task_id);
        setResults((prev) =>
          prev.map((r, idx) =>
            idx === i
              ? { ...r, status: result.status as BatchResult['status'], scores: result.scores, total: result.total, error: result.error }
              : r,
          ),
        );
      } catch (err) {
        setResults((prev) =>
          prev.map((r, idx) =>
            idx === i ? { ...r, status: 'failed', error: String(err) } : r,
          ),
        );
      }
    }

    setRunning(false);
  };

  const handleAbort = () => {
    abortRef.current = true;
  };

  const handleExportCSV = () => {
    const dims = ['L1', 'L2', 'L3', 'L4', 'L5'];
    const header = ['Subject', ...dims, 'Total', 'Status'].join(',');
    const rows = results.map((r) =>
      [
        `"${r.subject}"`,
        ...dims.map((d) => (r.scores[d] ?? '').toString()),
        r.total?.toFixed(3) ?? '',
        r.status,
      ].join(','),
    );
    const csv = [header, ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `vulca-batch-${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const completedCount = results.filter((r) => r.status === 'completed').length;

  return (
    <div className="space-y-3">
      <div className="text-sm font-semibold text-gray-900 dark:text-white">
        Batch Evaluation
      </div>

      {/* Input area */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        className="relative"
      >
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter one subject per line, or drag a CSV file here..."
          rows={6}
          disabled={running || disabled}
          className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 placeholder-gray-400 resize-none"
        />
        <div className="absolute bottom-2 right-2 text-[10px] text-gray-400">
          {subjects.length} subject{subjects.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex items-center gap-2">
        {!running ? (
          <IOSButton
            variant="primary"
            size="sm"
            onClick={handleRun}
            disabled={subjects.length === 0 || disabled}
          >
            Run Batch ({subjects.length})
          </IOSButton>
        ) : (
          <IOSButton variant="destructive" size="sm" onClick={handleAbort}>
            Abort
          </IOSButton>
        )}
        {results.length > 0 && !running && (
          <IOSButton variant="secondary" size="sm" onClick={handleExportCSV}>
            Export CSV
          </IOSButton>
        )}
        {running && (
          <span className="text-xs text-gray-500">
            {completedCount}/{results.length} done
          </span>
        )}
      </div>

      {/* Results table */}
      {results.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="text-left py-1 px-2 font-semibold text-gray-700 dark:text-gray-300">Subject</th>
                {['L1', 'L2', 'L3', 'L4', 'L5'].map((d) => (
                  <th key={d} className="text-center py-1 px-1 font-semibold text-gray-700 dark:text-gray-300 w-12">
                    {d}
                  </th>
                ))}
                <th className="text-center py-1 px-1 font-semibold text-gray-700 dark:text-gray-300 w-14">Total</th>
                <th className="text-center py-1 px-2 font-semibold text-gray-700 dark:text-gray-300 w-16">Status</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r, i) => (
                <tr key={i} className="border-b border-gray-100 dark:border-gray-800">
                  <td className="py-1 px-2 text-gray-800 dark:text-gray-200 max-w-[200px] truncate">
                    {r.subject}
                  </td>
                  {['L1', 'L2', 'L3', 'L4', 'L5'].map((d) => (
                    <td key={d} className="text-center py-1 px-1 font-mono text-gray-600 dark:text-gray-400">
                      {r.scores[d]?.toFixed(2) ?? '—'}
                    </td>
                  ))}
                  <td className="text-center py-1 px-1 font-mono font-semibold text-gray-800 dark:text-gray-200">
                    {r.total?.toFixed(3) ?? '—'}
                  </td>
                  <td className="text-center py-1 px-2">
                    <span
                      className={[
                        'inline-block px-1.5 py-0.5 rounded-full text-[10px] font-medium',
                        r.status === 'completed'
                          ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                          : r.status === 'running'
                            ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                            : r.status === 'failed'
                              ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                              : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400',
                      ].join(' ')}
                      title={r.error}
                    >
                      {r.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
