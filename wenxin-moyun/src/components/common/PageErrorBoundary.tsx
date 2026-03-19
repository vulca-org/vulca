import React from 'react';
import { IOSCard, IOSCardContent, IOSButton } from '../ios';

interface PageErrorBoundaryProps {
  children: React.ReactNode;
  pageName: string;
}

interface PageErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

class PageErrorBoundary extends React.Component<PageErrorBoundaryProps, PageErrorBoundaryState> {
  constructor(props: PageErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): PageErrorBoundaryState {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error(`PageErrorBoundary (${this.props.pageName}) caught an error:`, {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      page: this.props.pageName,
      timestamp: new Date().toISOString(),
    });
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: undefined,
    });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      return (
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-lg mx-auto">
            <IOSCard variant="elevated" className="text-center">
              <IOSCardContent className="p-8">
                <div className="text-4xl mb-4">😵</div>
                
                <h2 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">
                  {this.props.pageName} Error
                </h2>
                
                <p className="text-gray-600 dark:text-gray-300 mb-6 text-sm leading-relaxed">
                  We encountered an issue loading this page. Please try refreshing or go back to continue browsing.
                </p>

                {/* Show error details in development */}
                {import.meta.env.DEV && (
                  <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-left">
                    <p className="text-xs text-red-700 dark:text-red-300 font-mono">
                      <strong>Error:</strong> {this.state.error.message}
                    </p>
                  </div>
                )}

                <div className="space-y-2">
                  <IOSButton
                    variant="primary"
                    size="md"
                    onClick={this.handleReset}
                    className="w-full"
                  >
                    🔄 Retry
                  </IOSButton>
                  
                  <IOSButton
                    variant="secondary"
                    size="sm"
                    onClick={() => window.history.back()}
                    className="w-full"
                  >
                    ← Go Back
                  </IOSButton>
                </div>
              </IOSCardContent>
            </IOSCard>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default PageErrorBoundary;