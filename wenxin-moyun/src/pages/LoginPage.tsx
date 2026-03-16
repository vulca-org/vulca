import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LogIn, User, Lock, ArrowLeft } from 'lucide-react';
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
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // OAuth2 requires form-data format for login
      const formParams = new URLSearchParams();
      formParams.append('username', formData.username);
      formParams.append('password', formData.password);

      const response = await apiClient.post('/auth/login', formParams, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      if (response.data.access_token) {
        setItem('access_token', response.data.access_token);
        setItem('username', formData.username);
        
        // Redirect to the page they came from or home
        const from = new URLSearchParams(window.location.search).get('from') || '/';
        navigate(from);
      }
    } catch (err) {
      const loginError = err as LoginErrorShape;
      console.error('Login failed:', err);
      setError(loginError.response?.data?.detail || 'Login failed, please check username and password');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = () => {
    setFormData({
      username: 'demo',
      password: 'demo123'
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-amber-50 to-[#FAF0E6] flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <div className="glass-effect rounded-2xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-gradient-to-br from-amber-700 to-slate-700 rounded-2xl mx-auto mb-4 flex items-center justify-center">
              <LogIn className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-3xl font-bold gradient-text mb-2">Welcome Back</h2>
            <p className="text-gray-600 dark:text-gray-400">Sign in to VULCA Platform</p>
          </div>

          {/* Error Message */}
          {error && (
            <div id="login-error" role="alert" aria-live="assertive" className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-300 text-sm">
              {error}
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Username <span className="text-red-500" aria-hidden="true">*</span>
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
                <input
                  id="username"
                  name="username"
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-amber-600"
                  placeholder="Enter your username"
                  required
                  aria-invalid={error ? 'true' : undefined}
                  aria-describedby={error ? 'login-error' : undefined}
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Password <span className="text-red-500" aria-hidden="true">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
                <input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-amber-600"
                  placeholder="Enter your password"
                  required
                  aria-invalid={error ? 'true' : undefined}
                  aria-describedby={error ? 'login-error' : undefined}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              data-testid="login-submit"
              className="w-full py-3 bg-gradient-to-r from-amber-700 to-slate-700 text-white rounded-lg font-medium hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-amber-600 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          {/* Demo Account */}
          <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <div className="text-center text-sm text-gray-600 dark:text-gray-400">
              <p className="mb-2">Try it out</p>
              <button
                type="button"
                onClick={handleDemoLogin}
                className="text-amber-700 dark:text-amber-500 hover:text-[#C87F4A] dark:hover:text-amber-400 font-medium"
              >
                Use demo account
              </button>
            </div>
          </div>

          {/* Register Link */}
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Don't have an account?{' '}
              <button
                onClick={() => navigate('/register')}
                className="text-amber-700 dark:text-amber-500 hover:text-[#C87F4A] dark:hover:text-amber-400 font-medium"
              >
                Register
              </button>
            </p>
          </div>

          {/* Back to Home */}
          <div className="mt-4 text-center">
            <button
              onClick={() => navigate('/')}
              className="inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Return to Home
            </button>
          </div>
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center text-sm text-gray-500 dark:text-gray-400">
          <p>VULCA - Cultural AI Evaluation Platform</p>
          <p className="mt-1">© 2025-2026 VULCA Team. All rights reserved</p>
        </div>
      </motion.div>
    </div>
  );
};

export default LoginPage;
