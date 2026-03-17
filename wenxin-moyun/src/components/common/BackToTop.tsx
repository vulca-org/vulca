import { useState, useEffect } from 'react';
import { ArrowUp } from 'lucide-react';

/**
 * Floating "Back to Top" button.
 * Appears when the user scrolls past 600px, fades in/out smoothly.
 */
export default function BackToTop() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const THRESHOLD = 600;

    const handleScroll = () => {
      setVisible(window.scrollY > THRESHOLD);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <button
      onClick={scrollToTop}
      aria-label="Back to top"
      className="fixed bottom-6 right-6 z-40 w-10 h-10 flex items-center justify-center rounded-full bg-slate-700 text-white shadow-lg transition-opacity duration-300 hover:bg-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2"
      style={{
        opacity: visible ? 1 : 0,
        pointerEvents: visible ? 'auto' : 'none',
      }}
    >
      <ArrowUp className="w-5 h-5" />
    </button>
  );
}
