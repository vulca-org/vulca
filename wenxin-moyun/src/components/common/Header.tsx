import { Link, useLocation } from 'react-router-dom';
import { Menu, X, Github } from 'lucide-react';
import { useState } from 'react';
import { IOSButton } from '../ios';
import { HeaderControls } from './ThemeToggle';
import VulcaLogo from './VulcaLogo';

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const primaryNav = [
    { name: 'Canvas', href: '/canvas' },
    { name: 'Gallery', href: '/gallery' },
  ];

  const isActive = (path: string) => {
    return location.pathname === path ||
           (path === '/canvas' && location.pathname.startsWith('/canvas'));
  };

  return (
    <header className="ios-glass border-b border-gray-200/20 dark:border-gray-700/20 sticky top-0 z-50 backdrop-blur-xl">
      <nav className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="group">
            <VulcaLogo size="lg" showSubtitle={false} variant="header" />
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-1">
            {primaryNav.map((item) => (
              <Link key={item.name} to={item.href}>
                <IOSButton
                  variant={isActive(item.href) ? "primary" : "text"}
                  size="sm"
                  data-testid={`nav-${item.name.toLowerCase()}`}
                >
                  {item.name}
                </IOSButton>
              </Link>
            ))}

            {/* GitHub icon link */}
            <a
              href="https://github.com/vulca-org/vulca"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-lg text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100/50 dark:hover:bg-gray-800/50 transition-colors"
              aria-label="GitHub"
            >
              <Github className="w-5 h-5" />
            </a>

            {/* Divider */}
            <div className="w-px h-6 bg-gray-200 dark:bg-gray-700 mx-2" />

            {/* Theme Toggle */}
            <HeaderControls />
          </div>

          {/* Mobile Controls */}
          <div className="flex items-center space-x-2 lg:hidden">
            <HeaderControls />
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="min-w-[44px] min-h-[44px] flex items-center justify-center rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100/50 dark:hover:bg-gray-800/50 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2 transition-colors duration-200"
              aria-label={isMenuOpen ? "Close menu" : "Open menu"}
            >
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="lg:hidden py-4 space-y-2 ios-glass rounded-xl mt-2 mb-4 border border-gray-200/20 dark:border-gray-700/20">
            <div className="px-3 space-y-1">
              {primaryNav.map((item) => (
                <Link key={item.name} to={item.href} onClick={() => setIsMenuOpen(false)}>
                  <IOSButton variant={isActive(item.href) ? "primary" : "text"} size="md" className="w-full justify-start">
                    {item.name}
                  </IOSButton>
                </Link>
              ))}
              <a
                href="https://github.com/vulca-org/vulca"
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => setIsMenuOpen(false)}
              >
                <IOSButton variant="text" size="md" className="w-full justify-start">
                  <Github className="w-4 h-4 mr-2" />
                  GitHub
                </IOSButton>
              </a>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}
