import React from 'react';
import { IOSCard, IOSCardContent, IOSButton } from '../ios';
import { captureError, addBreadcrumb } from '../../config/sentry';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{
    error: Error;
    resetError: () => void;
  }>;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    this.setState({
      error,
      errorInfo,
    });

    // Report to Sentry
    captureError(error, {
      componentStack: errorInfo.componentStack,
      type: 'react-error-boundary',
    });

    // Add breadcrumb for debugging
    addBreadcrumb('error-boundary', `Caught error: ${error.message}`, 'error');

    // Call optional error reporting callback
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: undefined,
      errorInfo: undefined,
    });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      // If a custom fallback component is provided, use it
      if (this.props.fallback) {
        const FallbackComponent = this.props.fallback;
        return <FallbackComponent error={this.state.error} resetError={this.handleReset} />;
      }

      // Default fallback UI
      return (
        <div className="min-h-screen bg-gradient-to-b from-white via-gray-50 to-white 
                       dark:from-black dark:via-gray-900 dark:to-black 
                       flex items-center justify-center p-4">
          <div className="max-w-md w-full">
            <IOSCard variant="elevated" className="text-center">
              <IOSCardContent className="p-8">
                <div className="text-6xl mb-6">⚠️</div>
                
                <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
                  Oops! Something went wrong
                </h2>
                
                <p className="text-gray-600 dark:text-gray-300 mb-6 leading-relaxed">
                  We encountered an unexpected error. This has been logged and we'll work on fixing it.
                </p>

                {/* Error details in development */}
                {import.meta.env.DEV && (
                  <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-left">
                    <h3 className="text-sm font-semibold text-red-800 dark:text-red-200 mb-2">
                      Error Details (Development):
                    </h3>
                    <div className="text-xs text-red-700 dark:text-red-300 font-mono">
                      <p className="mb-1"><strong>Error:</strong> {this.state.error.message}</p>
                      {this.state.error.stack && (
                        <pre className="whitespace-pre-wrap break-all text-xs">
                          {this.state.error.stack.split('\n').slice(0, 3).join('\n')}
                        </pre>
                      )}
                    </div>
                  </div>
                )}

                <div className="space-y-3">
                  <IOSButton
                    variant="primary"
                    size="lg"
                    onClick={this.handleReset}
                    className="w-full"
                  >
                    🔄 Try Again
                  </IOSButton>
                  
                  <IOSButton
                    variant="secondary"
                    size="md"
                    onClick={() => window.location.href = '/'}
                    className="w-full"
                  >
                    🏠 Go to Homepage
                  </IOSButton>
                  
                  <IOSButton
                    variant="text"
                    size="sm"
                    onClick={() => window.location.reload()}
                    className="w-full text-gray-600 dark:text-gray-400"
                  >
                    🔄 Refresh Page
                  </IOSButton>
                </div>
              </IOSCardContent>
            </IOSCard>
            
            <p className="text-center text-xs text-gray-500 dark:text-gray-400 mt-4">
              If this problem persists, please contact support or try refreshing the page.
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;