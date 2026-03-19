import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import apiClient from '../services/api';
import { setItem } from '../utils/storageUtils';

interface LoginErrorShape {
  response?: {
    data?: {
      detail?: string;
    };
  };
}

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const formParams = new URLSearchParams();
      formParams.append('username', formData.username);
      formParams.append('password', formData.password);

      const response = await apiClient.post('/auth/login', formParams, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      if (response.data.access_token) {
        setItem('access_token', response.data.access_token);
        setItem('username', formData.username);
        const from = new URLSearchParams(window.location.search).get('from') || '/';
        navigate(from);
      }
    } catch (err) {
      const loginError = err as LoginErrorShape;
      setError(loginError.response?.data?.detail || 'Login failed, please check username and password');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setError('');
    setIsLoading(true);
    try {
      const formParams = new URLSearchParams();
      formParams.append('username', 'demo');
      formParams.append('password', 'demo123');

      const response = await apiClient.post('/auth/login', formParams, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      if (response.data.access_token) {
        setItem('access_token', response.data.access_token);
        setItem('username', 'demo');
        const from = new URLSearchParams(window.location.search).get('from') || '/';
        navigate(from);
      }
    } catch (err) {
      const loginError = err as LoginErrorShape;
      setError(loginError.response?.data?.detail || 'Demo login failed. The server may be unavailable.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface flex flex-col">
      {/* Nav */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link to="/" className="text-xl font-bold tracking-tighter text-on-surface">VULCA AI</Link>
          <nav className="hidden sm:flex items-center gap-6">
            <Link to="/canvas" className="text-sm text-on-surface-variant hover:text-on-surface transition-colors">Canvas</Link>
            <Link to="/gallery" className="text-sm text-on-surface-variant hover:text-on-surface transition-colors">Gallery</Link>
            <a href="https://github.com/vulca-org/vulca" target="_blank" rel="noopener noreferrer" className="text-sm text-on-surface-variant hover:text-on-surface transition-colors">GitHub</a>
          </nav>
        </div>
        <Link to="/login">
          <button className="text-sm font-medium text-primary-500 hover:text-primary-600 transition-colors">Sign In</button>
        </Link>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-[460px]"
        >
          {/* Card */}
          <div className="bg-white rounded-2xl shadow-ambient-xl p-8 sm:p-10">
            {/* Icon + Title */}
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-primary-500 rounded-2xl mx-auto mb-5 flex items-center justify-center shadow-lg shadow-primary-500/20">
                <span className="material-symbols-outlined text-white text-3xl">token</span>
              </div>
              <h1 className="font-display text-3xl font-bold text-on-surface mb-2">Welcome Back</h1>
              <p className="text-on-surface-variant text-sm">Sign in to your VULCA AI workspace</p>
            </div>

            {/* GitHub OAuth (placeholder) */}
            <button
              onClick={handleDemoLogin}
              className="w-full flex items-center justify-center gap-3 bg-gray-900 text-white py-3.5 rounded-xl font-medium text-sm hover:bg-gray-800 active:scale-[0.98] transition-all mb-6"
            >
              <span className="material-symbols-outlined text-lg">play_circle</span>
              Quick Demo (no account needed)
            </button>

            {/* Divider */}
            <div className="relative mb-6">
              <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-surface-container-high" /></div>
              <div className="relative flex justify-center text-xs"><span className="px-3 bg-white text-on-surface-variant uppercase tracking-wider">or continue with email</span></div>
            </div>

            {/* Error */}
            {error && (
              <div id="login-error" role="alert" aria-live="assertive" className="mb-4 p-3 bg-error-50 border border-error-200 rounded-lg text-error-700 text-sm">
                {error}
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-on-surface mb-2">
                  Email address
                </label>
                <input
                  id="username"
                  name="username"
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
                  className="w-full px-5 py-3.5 bg-surface-container-high rounded-xl text-on-surface text-sm placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:bg-white transition-all"
                  placeholder="name@company.com"
                  required
                  aria-invalid={error ? 'true' : undefined}
                  aria-describedby={error ? 'login-error' : undefined}
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label htmlFor="password" className="block text-sm font-medium text-on-surface">
                    Password
                  </label>
                  <button type="button" className="text-xs font-medium text-primary-500 hover:text-primary-600 transition-colors">
                    Forgot password?
                  </button>
                </div>
                <input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                  className="w-full px-5 py-3.5 bg-surface-container-high rounded-xl text-on-surface text-sm placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:bg-white transition-all"
                  placeholder="••••••••"
                  required
                  aria-invalid={error ? 'true' : undefined}
                  aria-describedby={error ? 'login-error' : undefined}
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                data-testid="login-submit"
                className="w-full bg-primary-500 text-white py-3.5 rounded-xl font-semibold text-sm hover:bg-primary-600 active:scale-[0.98] transition-all shadow-lg shadow-primary-500/20 disabled:opacity-50 disabled:pointer-events-none"
              >
                {isLoading ? 'Signing in...' : 'Continue'}
              </button>
            </form>

            {/* Register link */}
            <p className="text-center text-sm text-on-surface-variant mt-6">
              Don't have an account?{' '}
              <Link to="/register" className="font-semibold text-primary-500 hover:text-primary-600 transition-colors">
                Sign up for free
              </Link>
            </p>
          </div>

          {/* Legal */}
          <p className="text-center text-[11px] text-outline mt-6 leading-relaxed">
            By continuing, you agree to VULCA AI's{' '}
            <Link to="/terms" className="underline hover:text-on-surface-variant">Terms of Service</Link>{' '}
            and{' '}
            <Link to="/privacy" className="underline hover:text-on-surface-variant">Privacy Policy</Link>.
          </p>
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="py-6 px-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-outline">
        <span className="font-bold text-on-surface-variant">VULCA AI</span>
        <div className="flex items-center gap-6">
          <Link to="/privacy" className="hover:text-on-surface-variant transition-colors">Privacy Policy</Link>
          <Link to="/terms" className="hover:text-on-surface-variant transition-colors">Terms of Service</Link>
          <a href="https://github.com/vulca-org/vulca" target="_blank" rel="noopener noreferrer" className="hover:text-on-surface-variant transition-colors">GitHub</a>
        </div>
      </footer>
    </div>
  );
};

export default LoginPage;
