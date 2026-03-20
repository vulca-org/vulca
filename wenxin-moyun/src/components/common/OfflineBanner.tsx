import { useEffect } from 'react';
import toast from 'react-hot-toast';
import { API_BASE_URL } from '../../config/api';

/**
 * Checks backend health on mount. If offline, shows a small toast
 * in the bottom-right corner instead of a top banner (per design spec).
 */
export default function OfflineBanner() {
  useEffect(() => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    fetch(`${API_BASE_URL}/api/v1/health/`, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) showOfflineToast();
      })
      .catch(() => {
        showOfflineToast();
      })
      .finally(() => {
        clearTimeout(timeout);
      });

    return () => {
      controller.abort();
      clearTimeout(timeout);
    };
  }, []);

  return null; // No visible banner — toast only
}

function showOfflineToast() {
  toast('Running in demo mode — some features may be limited', {
    icon: '⚡',
    duration: 6000,
    position: 'bottom-right',
    style: {
      fontSize: '12px',
      padding: '8px 14px',
      borderRadius: '12px',
      background: '#f9f9ff',
      color: '#181c22',
      boxShadow: '0 4px 24px rgba(28,28,25,0.08)',
    },
  });
}
