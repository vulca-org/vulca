import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { API_BASE_URL } from '../../config/api';

/**
 * Shows a small amber banner when the backend API is unreachable.
 * Checks the health endpoint on mount with a 5s timeout.
 * Dismissible via the X button.
 */
export default function OfflineBanner() {
  const [offline, setOffline] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    fetch(`${API_BASE_URL}/api/v1/health/`, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) setOffline(true);
      })
      .catch(() => {
        setOffline(true);
      })
      .finally(() => {
        clearTimeout(timeout);
      });

    return () => {
      controller.abort();
      clearTimeout(timeout);
    };
  }, []);

  if (!offline || dismissed) return null;

  return (
    <div className="bg-amber-50 dark:bg-amber-950/40 border-b border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300 text-xs text-center py-1.5 px-4 relative">
      Running in demo mode &mdash; some features may be limited
      <button
        onClick={() => setDismissed(true)}
        className="absolute right-2 top-1/2 -translate-y-1/2 p-0.5 rounded hover:bg-amber-200/50 dark:hover:bg-amber-800/30 transition-colors"
        aria-label="Dismiss"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}
