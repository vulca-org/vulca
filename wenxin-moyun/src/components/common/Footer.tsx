/**
 * Footer Component - Scale.com Style
 *
 * Comprehensive footer with:
 * - Product links
 * - Solutions links
 * - Company links
 * - Resources links
 * - Newsletter signup
 * - Social links
 * - Legal links
 */

import { Link } from 'react-router-dom';
import {
  Github,
  Twitter,
  Linkedin,
  Mail,
  Heart,
  ArrowRight,
  ExternalLink,
  Loader2
} from 'lucide-react';
import { IOSButton } from '../ios';
import { useState } from 'react';
import VulcaLogo from './VulcaLogo';
import { subscribeNewsletter } from '../../utils/supabase';

const footerLinks = {
  product: {
    title: 'Product',
    links: [
      { name: 'Canvas', href: '/canvas' },
      { name: 'Gallery', href: '/gallery' },
      { name: 'Pricing', href: '/pricing' },
      { name: 'Models', href: '/models' },
      { name: 'Exhibitions', href: '/exhibitions' },
    ]
  },
  solutions: {
    title: 'Solutions',
    links: [
      { name: 'AI Labs', href: '/solutions/ai-labs' },
      { name: 'Research', href: '/solutions/research' },
      { name: 'Museums', href: '/solutions/museums' },
      { name: 'Enterprise', href: '/pricing' },
    ]
  },
  company: {
    title: 'Company',
    links: [
      { name: 'Customers', href: '/customers' },
      { name: 'Trust & Security', href: '/trust' },
      { name: 'Book a Demo', href: '/demo' },
    ]
  },
  resources: {
    title: 'Resources',
    links: [
      { name: 'Research', href: '/research' },
      { name: 'GitHub', href: 'https://github.com/vulca-org/vulca', external: true },
    ]
  }
};

const socialLinks = [
  { name: 'GitHub', icon: Github, href: 'https://github.com/vulca-org/vulca' },
  { name: 'Twitter', icon: Twitter, href: 'https://twitter.com/vulca_ai' },
  { name: 'LinkedIn', icon: Linkedin, href: 'https://linkedin.com/company/vulca-ai' },
  { name: 'Email', icon: Mail, href: 'mailto:hello@vulcaart.art' },
];

export default function Footer() {
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubscribe = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setIsLoading(true);
    setError(null);

    const result = await subscribeNewsletter(email, 'footer');

    setIsLoading(false);

    if (result.success) {
      setSubscribed(true);
      setEmail('');
    } else {
      setError(result.error || 'Subscription failed');
    }
  };

  return (
    <footer className="bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 mt-auto">
      <div className="container mx-auto px-6 py-12">
        {/* Main Grid */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-8 mb-12">
          {/* Logo & Description */}
          <div className="col-span-2">
            <Link to="/" className="inline-block mb-4">
              <VulcaLogo size="md" showSubtitle={true} variant="footer" />
            </Link>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 max-w-xs">
              Comprehensive 47-dimensional evaluation framework for AI cultural understanding.
              Trusted by AI labs, researchers, and museums worldwide.
            </p>

            {/* Newsletter Signup */}
            <div className="mt-6">
              <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                Stay Updated
              </h4>
              {subscribed ? (
                <p className="text-sm text-green-600 dark:text-green-400">
                  Thanks for subscribing!
                </p>
              ) : (
                <form onSubmit={handleSubscribe} className="flex flex-col gap-2">
                  <div className="flex gap-2">
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email"
                      disabled={isLoading}
                      aria-label="Email address"
                      className="flex-1 px-3 py-2 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-600 disabled:opacity-50"
                    />
                    <IOSButton variant="primary" size="sm" type="submit" disabled={isLoading || !email} aria-label="Subscribe">
                      {isLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <ArrowRight className="w-4 h-4" />
                      )}
                    </IOSButton>
                  </div>
                  {error && (
                    <p className="text-xs text-red-500">{error}</p>
                  )}
                </form>
              )}
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">
              {footerLinks.product.title}
            </h4>
            <ul className="space-y-2">
              {footerLinks.product.links.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.href}
                    className="text-sm text-gray-600 dark:text-gray-400 hover:text-slate-700 dark:hover:text-slate-500 transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Solutions Links */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">
              {footerLinks.solutions.title}
            </h4>
            <ul className="space-y-2">
              {footerLinks.solutions.links.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.href}
                    className="text-sm text-gray-600 dark:text-gray-400 hover:text-slate-700 dark:hover:text-slate-500 transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">
              {footerLinks.company.title}
            </h4>
            <ul className="space-y-2">
              {footerLinks.company.links.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.href}
                    className="text-sm text-gray-600 dark:text-gray-400 hover:text-slate-700 dark:hover:text-slate-500 transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources Links */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">
              {footerLinks.resources.title}
            </h4>
            <ul className="space-y-2">
              {footerLinks.resources.links.map((link) => (
                <li key={link.name}>
                  {'external' in link && link.external ? (
                    <a
                      href={link.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-gray-600 dark:text-gray-400 hover:text-slate-700 dark:hover:text-slate-500 transition-colors inline-flex items-center gap-1"
                    >
                      {link.name}
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  ) : (
                    <Link
                      to={link.href}
                      className="text-sm text-gray-600 dark:text-gray-400 hover:text-slate-700 dark:hover:text-slate-500 transition-colors"
                    >
                      {link.name}
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-200 dark:border-gray-800 pt-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            {/* Copyright */}
            <div className="text-sm text-gray-500 dark:text-gray-400">
              <p className="flex items-center gap-1">
                Made with <Heart className="w-4 h-4 text-red-500" /> by VULCA Team
              </p>
              <p className="mt-1">© 2025-2026 VULCA. All rights reserved.</p>
            </div>

            {/* Social Links */}
            <div className="flex items-center gap-2">
              {socialLinks.map((social) => (
                <a
                  key={social.name}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 hover:text-slate-700 dark:hover:text-slate-500 transition-colors"
                  aria-label={social.name}
                >
                  <social.icon className="w-4 h-4" />
                </a>
              ))}
            </div>

            {/* Legal Links */}
            <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
              <Link to="/terms" className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors">
                Terms
              </Link>
              <Link to="/privacy" className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors">
                Privacy
              </Link>
              <Link to="/trust" className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors">
                Security
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
