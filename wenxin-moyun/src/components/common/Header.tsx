import { Link, useLocation } from 'react-router-dom';
import { Menu, X, ChevronDown, Calendar } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { IOSButton } from '../ios';
import { HeaderControls } from './ThemeToggle';
import VulcaLogo from './VulcaLogo';

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isMoreOpen, setIsMoreOpen] = useState(false);
  const moreRef = useRef<HTMLDivElement>(null);
  const location = useLocation();

  // Close dropdowns when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (moreRef.current && !moreRef.current.contains(event.target as Node)) {
        setIsMoreOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Primary navigation — product core
  const primaryNav = [
    { name: 'Canvas', href: '/canvas' },
    { name: 'Gallery', href: '/gallery' },
    { name: 'About', href: '/research' },
  ];

  // "More" dropdown — support + academic reference
  const moreItems = [
    { name: 'Models', href: '/models' },
    { name: 'Exhibitions', href: '/exhibitions' },
    { name: 'Research', href: '/research' },
    { name: 'Solutions', href: '/solutions' },
    { name: 'Pricing', href: '/pricing' },
    { name: 'Trust', href: '/trust' },
  ];

  const isActive = (path: string) => {
    return location.pathname === path ||
           (path === '/models' && location.pathname.startsWith('/model')) ||
           (path === '/canvas' && location.pathname.startsWith('/canvas')) ||
           (path === '/exhibitions' && location.pathname.startsWith('/exhibitions')) ||
           (path === '/solutions' && location.pathname.startsWith('/solutions'));
  };

  const isMoreActive = moreItems.some((item) => isActive(item.href));

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
            {/* Primary nav items */}
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

            {/* More Dropdown */}
            <div className="relative" ref={moreRef}>
              <IOSButton
                variant={isMoreOpen || isMoreActive ? "primary" : "text"}
                size="sm"
                onClick={() => setIsMoreOpen(!isMoreOpen)}
                className="flex items-center gap-1"
                aria-haspopup="menu"
                aria-expanded={isMoreOpen}
                aria-controls="more-dropdown-menu"
              >
                More
                <ChevronDown className={`w-4 h-4 transition-transform ${isMoreOpen ? 'rotate-180' : ''}`} />
              </IOSButton>

              {isMoreOpen && (
                <div
                  id="more-dropdown-menu"
                  role="menu"
                  className="absolute top-full right-0 mt-2 w-48 ios-glass rounded-xl border border-gray-200/20 dark:border-gray-700/20 shadow-lg py-2 z-50"
                >
                  {moreItems.map((item) => (
                    <Link
                      key={item.name}
                      to={item.href}
                      role="menuitem"
                      onClick={() => setIsMoreOpen(false)}
                      className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100/50 dark:hover:bg-gray-800/50"
                    >
                      {item.name}
                    </Link>
                  ))}
                </div>
              )}
            </div>

            {/* Divider */}
            <div className="w-px h-6 bg-gray-200 dark:bg-gray-700 mx-2" />

            {/* Theme Toggle */}
            <HeaderControls />

            {/* Book a Demo CTA */}
            <Link to="/demo">
              <IOSButton
                variant="primary"
                size="sm"
                className="ml-2 flex items-center gap-1.5"
                data-testid="book-demo-cta"
              >
                <Calendar className="w-4 h-4" />
                Book a Demo
              </IOSButton>
            </Link>
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
            {/* Book a Demo - Prominent on mobile */}
            <div className="px-3 pb-3 border-b border-gray-200/20 dark:border-gray-700/20">
              <Link to="/demo" onClick={() => setIsMenuOpen(false)}>
                <IOSButton variant="primary" size="md" className="w-full flex items-center justify-center gap-2">
                  <Calendar className="w-5 h-5" />
                  Book a Demo
                </IOSButton>
              </Link>
            </div>

            {/* Primary nav items */}
            <div className="px-3 space-y-1">
              {primaryNav.map((item) => (
                <Link key={item.name} to={item.href} onClick={() => setIsMenuOpen(false)}>
                  <IOSButton variant={isActive(item.href) ? "primary" : "text"} size="md" className="w-full justify-start">
                    {item.name}
                  </IOSButton>
                </Link>
              ))}
            </div>

            {/* More section */}
            <div className="border-t border-gray-200/20 dark:border-gray-700/20 pt-2 px-3">
              <div className="text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider px-3 py-2">
                More
              </div>
              {moreItems.map((item) => (
                <Link key={item.name} to={item.href} onClick={() => setIsMenuOpen(false)}>
                  <IOSButton variant={isActive(item.href) ? "primary" : "text"} size="sm" className="w-full justify-start">
                    {item.name}
                  </IOSButton>
                </Link>
              ))}
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}
