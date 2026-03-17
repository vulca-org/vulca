import { Link } from 'react-router-dom';
import { Github } from 'lucide-react';
import { isGuestMode } from '../../utils/guestSession';

export default function Footer() {
  const guest = isGuestMode();

  return (
    <footer className="border-t border-gray-200 dark:border-gray-800 mt-auto">
      <div className="container mx-auto px-4 py-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-sm text-gray-500 dark:text-gray-400">
          <div className="flex flex-wrap justify-center items-center gap-3 sm:gap-4">
            <Link to="/canvas" className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors">Canvas</Link>
            <Link to="/gallery" className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors">Gallery</Link>
            <a
              href="https://github.com/vulca-org/vulca"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors inline-flex items-center gap-1"
            >
              <Github className="w-3.5 h-3.5" />
              GitHub
            </a>
            <Link to="/research" className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors">Docs</Link>
            {guest && (
              <Link to="/login" className="hover:text-[#C87F4A] dark:hover:text-[#DDA574] transition-colors">Sign In</Link>
            )}
            <span className="text-gray-400 dark:text-gray-600">Apache 2.0</span>
          </div>
          <span>&copy; 2025-2026 VULCA</span>
        </div>
      </div>
    </footer>
  );
}
