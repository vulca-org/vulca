/**
 * StateHandlers - Unified state components for loading, error, and empty states
 * Follows iOS design system and product manual section 2.5 requirements
 */

import type { ReactNode } from 'react';
import { motion } from 'framer-motion';
import {
  AlertCircle,
  Search,
  RefreshCw,
  WifiOff,
  FileQuestion,
  Inbox,
  ImageOff
} from 'lucide-react';
import { IOSButton } from '../ios';

// ============================================
// Empty State Component
// ============================================

interface EmptyStateProps {
  icon?: ReactNode;
  title?: string;
  description?: string;
  action?: ReactNode;
  variant?: 'default' | 'search' | 'data' | 'image';
}

const emptyStateIcons = {
  default: <Inbox className="w-8 h-8 text-gray-400" />,
  search: <Search className="w-8 h-8 text-gray-400" />,
  data: <FileQuestion className="w-8 h-8 text-gray-400" />,
  image: <ImageOff className="w-8 h-8 text-gray-400" />,
};

export function EmptyState({
  icon,
  title = 'No Data Found',
  description = 'There is no content to display at the moment.',
  action,
  variant = 'default'
}: EmptyStateProps) {
  const defaultIcon = emptyStateIcons[variant];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="text-center py-12"
    >
      <div className="bg-gray-50 dark:bg-gray-900/50 rounded-2xl p-8 max-w-md mx-auto">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-200 dark:bg-gray-800 flex items-center justify-center">
          {icon || defaultIcon}
        </div>
        <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
          {title}
        </h3>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          {description}
        </p>
        {action && <div className="flex flex-col sm:flex-row gap-3 justify-center">{action}</div>}
      </div>
    </motion.div>
  );
}

// ============================================
// Error State Component
// ============================================

interface ErrorStateProps {
  error: string;
  errorDetails?: string | object;
  onRetry?: () => void;
  onDismiss?: () => void;
  variant?: 'inline' | 'fullpage' | 'toast';
  isOffline?: boolean;
}

export function ErrorState({
  error,
  errorDetails,
  onRetry,
  onDismiss,
  variant = 'inline',
  isOffline = false
}: ErrorStateProps) {
  const Icon = isOffline ? WifiOff : AlertCircle;
  const title = isOffline ? 'Connection Issue' : 'Error';

  if (variant === 'fullpage') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-16"
      >
        <div className="bg-red-50 dark:bg-red-900/20 rounded-2xl p-8 max-w-md mx-auto border border-red-200 dark:border-red-800">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
            <Icon className="w-8 h-8 text-red-500" />
          </div>
          <h3 className="text-xl font-semibold text-red-800 dark:text-red-200 mb-2">
            {title}
          </h3>
          <p className="text-red-600 dark:text-red-300 mb-6">
            {error}
          </p>
          {errorDetails && (
            <details className="mb-4 text-left">
              <summary className="text-xs text-red-500 cursor-pointer">
                Technical Details
              </summary>
              <pre className="text-xs text-red-600 dark:text-red-400 mt-2 p-3 bg-red-100 dark:bg-red-900/30 rounded overflow-x-auto">
                {typeof errorDetails === 'string' ? errorDetails : JSON.stringify(errorDetails, null, 2)}
              </pre>
            </details>
          )}
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            {onRetry && (
              <IOSButton variant="primary" onClick={onRetry}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Again
              </IOSButton>
            )}
            {onDismiss && (
              <IOSButton variant="secondary" onClick={onDismiss}>
                Dismiss
              </IOSButton>
            )}
          </div>
        </div>
      </motion.div>
    );
  }

  // Inline variant (default)
  return (
    <div
      role="alert"
      aria-live="polite"
      className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4"
    >
      <div className="flex items-start">
        <Icon className="w-5 h-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" aria-hidden="true" />
        <div className="flex-1">
          <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
            {title}
          </h3>
          <p className="text-sm text-red-700 dark:text-red-300 mt-1">{error}</p>
          {errorDetails && (
            <details className="mt-2">
              <summary className="text-xs text-red-600 dark:text-red-400 cursor-pointer">
                Technical Details
              </summary>
              <pre className="text-xs text-red-600 dark:text-red-400 mt-1 p-2 bg-red-100 dark:bg-red-900/30 rounded overflow-x-auto">
                {typeof errorDetails === 'string' ? errorDetails : JSON.stringify(errorDetails, null, 2)}
              </pre>
            </details>
          )}
          {(onRetry || onDismiss) && (
            <div className="mt-3 flex gap-2">
              {onRetry && (
                <IOSButton variant="primary" size="sm" onClick={onRetry}>
                  <RefreshCw className="w-3 h-3 mr-1" />
                  Retry
                </IOSButton>
              )}
              {onDismiss && (
                <IOSButton variant="secondary" size="sm" onClick={onDismiss}>
                  Dismiss
                </IOSButton>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================
// Loading State Component
// ============================================

interface LoadingStateProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'inline' | 'fullpage' | 'overlay';
}

const spinnerSizes = {
  sm: 'w-4 h-4',
  md: 'w-8 h-8',
  lg: 'w-12 h-12',
};

export function LoadingState({
  message = 'Loading...',
  size = 'md',
  variant = 'inline'
}: LoadingStateProps) {
  const spinnerSize = spinnerSizes[size];

  if (variant === 'fullpage') {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <div className={`${spinnerSize} animate-spin mx-auto`}>
            <svg className="w-full h-full text-slate-600" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400">{message}</p>
        </div>
      </div>
    );
  }

  if (variant === 'overlay') {
    return (
      <div className="absolute inset-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm flex items-center justify-center z-10 rounded-lg">
        <div className="text-center space-y-2">
          <div className={`${spinnerSize} animate-spin mx-auto`}>
            <svg className="w-full h-full text-slate-600" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400">{message}</p>
        </div>
      </div>
    );
  }

  // Inline variant (default)
  return (
    <div className="flex items-center justify-center py-8">
      <div className={`${spinnerSize} animate-spin mr-3`}>
        <svg className="w-full h-full text-slate-600" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      </div>
      <span className="text-gray-600 dark:text-gray-400">{message}</span>
    </div>
  );
}

// ============================================
// No Permission State Component
// ============================================

interface NoPermissionStateProps {
  title?: string;
  description?: string;
  onLogin?: () => void;
  onGoBack?: () => void;
}

export function NoPermissionState({
  title = 'Access Denied',
  description = 'You do not have permission to view this content.',
  onLogin,
  onGoBack
}: NoPermissionStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="text-center py-16"
    >
      <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-2xl p-8 max-w-md mx-auto border border-yellow-200 dark:border-yellow-800">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-yellow-100 dark:bg-yellow-900/30 flex items-center justify-center">
          <AlertCircle className="w-8 h-8 text-yellow-500" />
        </div>
        <h3 className="text-xl font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
          {title}
        </h3>
        <p className="text-yellow-600 dark:text-yellow-300 mb-6">
          {description}
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          {onLogin && (
            <IOSButton variant="primary" onClick={onLogin}>
              Sign In
            </IOSButton>
          )}
          {onGoBack && (
            <IOSButton variant="secondary" onClick={onGoBack}>
              Go Back
            </IOSButton>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// ============================================
// State Handler Wrapper
// ============================================

interface StateHandlerProps {
  loading?: boolean;
  error?: string | null;
  errorDetails?: string | object;
  isEmpty?: boolean;
  isOffline?: boolean;
  hasPermission?: boolean;
  onRetry?: () => void;
  onDismiss?: () => void;
  onLogin?: () => void;
  onGoBack?: () => void;
  loadingMessage?: string;
  emptyIcon?: ReactNode;
  emptyTitle?: string;
  emptyDescription?: string;
  emptyAction?: ReactNode;
  emptyVariant?: 'default' | 'search' | 'data' | 'image';
  children: ReactNode;
}

export function StateHandler({
  loading = false,
  error = null,
  errorDetails,
  isEmpty = false,
  isOffline = false,
  hasPermission = true,
  onRetry,
  onDismiss,
  onLogin,
  onGoBack,
  loadingMessage,
  emptyIcon,
  emptyTitle,
  emptyDescription,
  emptyAction,
  emptyVariant,
  children
}: StateHandlerProps) {
  // Loading state
  if (loading) {
    return <LoadingState message={loadingMessage} variant="fullpage" />;
  }

  // Permission state
  if (!hasPermission) {
    return <NoPermissionState onLogin={onLogin} onGoBack={onGoBack} />;
  }

  // Error state
  if (error) {
    return (
      <ErrorState
        error={error}
        errorDetails={errorDetails}
        onRetry={onRetry}
        onDismiss={onDismiss}
        isOffline={isOffline}
        variant="fullpage"
      />
    );
  }

  // Empty state
  if (isEmpty) {
    return (
      <EmptyState
        icon={emptyIcon}
        title={emptyTitle}
        description={emptyDescription}
        action={emptyAction}
        variant={emptyVariant}
      />
    );
  }

  // Success state - render children
  return <>{children}</>;
}

export default StateHandler;
