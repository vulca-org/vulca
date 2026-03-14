import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, User, Shield, Clock, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export interface LoginPromptProps {
  isOpen: boolean;
  onClose: () => void;
  trigger: 'limit_reached' | 'save_progress' | 'share_result' | 'advanced_features';
  remainingUsage?: number;
}

const LoginPrompt: React.FC<LoginPromptProps> = ({ 
  isOpen, 
  onClose, 
  trigger
}) => {
  const navigate = useNavigate();

  const handleLogin = () => {
    const returnUrl = encodeURIComponent(window.location.pathname + window.location.search);
    navigate(`/login?from=${returnUrl}`);
  };

  const getTriggerConfig = () => {
    switch (trigger) {
      case 'limit_reached':
        return {
          icon: Clock,
          title: 'Daily Trial Limit Reached',
          subtitle: `You've used all 10 free evaluations today`,
          description: 'Register to enjoy unlimited use and save your evaluation history.',
          buttonText: 'Sign Up Now',
          urgency: 'high' as const
        };
      case 'save_progress':
        return {
          icon: Shield,
          title: 'Save Your Evaluation Progress',
          subtitle: 'Prevent data loss and build your evaluation portfolio',
          description: 'Sign in to save all evaluation records and view historical data and trend analysis.',
          buttonText: 'Save Progress',
          urgency: 'medium' as const
        };
      case 'share_result':
        return {
          icon: TrendingUp,
          title: 'Share Your Amazing Work',
          subtitle: 'Let others see your creative achievements',
          description: 'Sign in to share evaluation results, join community discussions, and discover more excellent works.',
          buttonText: 'Start Sharing',
          urgency: 'low' as const
        };
      case 'advanced_features':
        return {
          icon: User,
          title: 'Unlock Advanced Features',
          subtitle: 'Professional evaluation tools await',
          description: 'Logged-in users can access batch evaluation, detailed reports, custom templates and more.',
          buttonText: 'Unlock Now',
          urgency: 'medium' as const
        };
    }
  };

  const config = getTriggerConfig();
  const IconComponent = config.icon;

  const getUrgencyStyles = () => {
    switch (config.urgency) {
      case 'high':
        return {
          iconColor: 'text-red-500',
          gradient: 'from-red-500 to-pink-500',
          buttonClass: 'bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700'
        };
      case 'medium':
        return {
          iconColor: 'text-orange-500',
          gradient: 'from-orange-500 to-amber-500',
          buttonClass: 'bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700'
        };
      case 'low':
        return {
          iconColor: 'text-slate-600',
          gradient: 'from-slate-600 to-amber-600',
          buttonClass: 'bg-gradient-to-r from-slate-700 to-amber-700 hover:from-slate-700 hover:to-amber-700'
        };
    }
  };

  const styles = getUrgencyStyles();

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
            onClick={onClose}
          >
            {/* Modal */}
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className="bg-white dark:bg-[#1A1614] rounded-xl shadow-2xl max-w-md w-full mx-4 overflow-hidden relative"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Close button */}
              <button
                onClick={onClose}
                className="absolute top-3 right-3 w-11 h-11 flex items-center justify-center rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors z-10"
                aria-label="Close"
              >
                <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
              </button>

              {/* Header with gradient background */}
              <div className={`bg-gradient-to-r ${styles.gradient} p-6 text-white relative`}>
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-neutral-50 bg-opacity-20 rounded-lg">
                    <IconComponent className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold">{config.title}</h3>
                    <p className="text-sm opacity-90">{config.subtitle}</p>
                  </div>
                </div>
                
                {/* Usage indicator for limit_reached */}
                {trigger === 'limit_reached' && (
                  <div className="mt-4 flex items-center space-x-2">
                    <div className="flex-1 bg-neutral-50 bg-opacity-20 rounded-full h-2">
                      <div className="h-full bg-neutral-50 rounded-full" style={{ width: '100%' }} />
                    </div>
                    <span className="text-sm font-medium">10/10</span>
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="p-6">
                <p className="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
                  {config.description}
                </p>

                {/* Benefits list */}
                <div className="space-y-3 mb-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">Unlimited evaluations</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">Save evaluation history</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">Advanced analytics features</span>
                  </div>
                </div>

                {/* Action buttons */}
                <div className="flex space-x-3">
                  <button
                    onClick={handleLogin}
                    className={`flex-1 ${styles.buttonClass} text-white px-4 py-3 rounded-lg font-medium transition-all hover:shadow-lg`}
                  >
                    {config.buttonText}
                  </button>
                  <button
                    onClick={onClose}
                    className="px-4 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                  >
                    Later
                  </button>
                </div>

                {/* Guest continue option for non-critical prompts */}
                {trigger !== 'limit_reached' && (
                  <div className="mt-3 text-center">
                    <button
                      onClick={onClose}
                      className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
                    >
                      Continue as Guest
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default LoginPrompt;
