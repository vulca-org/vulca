import React, { useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { IOSButton } from './IOSButton';
import { StatusEmoji } from './EmojiIcon';
import { iosAnimations } from '../utils/animations';

export interface IOSAlertAction {
  label: string;
  onPress: () => void;
  style?: 'default' | 'cancel' | 'destructive';
  disabled?: boolean;
}

export interface IOSAlertProps {
  visible: boolean;
  onClose: () => void;
  title?: string;
  message?: string;
  type?: 'info' | 'success' | 'warning' | 'error';
  actions?: IOSAlertAction[];
  showCloseButton?: boolean;
  customIcon?: React.ReactNode;
  className?: string;
}

export const IOSAlert: React.FC<IOSAlertProps> = ({
  visible,
  onClose,
  title,
  message,
  type = 'info',
  actions = [{ label: '确定', onPress: onClose, style: 'default' }],
  showCloseButton = false,
  customIcon,
  className = '',
}) => {
  type AlertStatus = React.ComponentProps<typeof StatusEmoji>['status'];

  // Type-based configurations
  const typeConfig: Record<NonNullable<IOSAlertProps['type']>, {
    emoji: AlertStatus;
    titleColor: string;
    borderColor: string;
    bgColor: string;
  }> = {
    info: {
      emoji: 'pending',
      titleColor: 'text-slate-900 dark:text-slate-100',
      borderColor: 'border-slate-200 dark:border-slate-800',
      bgColor: 'bg-slate-50/80 dark:bg-slate-900/20',
    },
    success: {
      emoji: 'completed',
      titleColor: 'text-[#3D5E35] dark:text-[#87A878]',
      borderColor: 'border-[#5F8A50]/20 dark:border-[#5F8A50]/30',
      bgColor: 'bg-[#5F8A50]/5 dark:bg-[#5F8A50]/10',
    },
    warning: {
      emoji: 'pending',
      titleColor: 'text-[#8F7030] dark:text-[#D4A94E]',
      borderColor: 'border-[#B8923D]/20 dark:border-[#B8923D]/30',
      bgColor: 'bg-[#B8923D]/5 dark:bg-[#B8923D]/10',
    },
    error: {
      emoji: 'failed',
      titleColor: 'text-red-900 dark:text-red-100',
      borderColor: 'border-red-200 dark:border-red-800',
      bgColor: 'bg-red-50/80 dark:bg-red-900/20',
    },
  };

  const config = typeConfig[type];
  const alertRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  // Focus trap: keep focus within the alert
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
      return;
    }

    if (e.key !== 'Tab') return;

    const focusableElements = alertRef.current?.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    if (!focusableElements || focusableElements.length === 0) return;

    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    if (e.shiftKey) {
      if (document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
      }
    } else {
      if (document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
      }
    }
  }, [onClose]);

  // Manage focus when alert opens/closes
  useEffect(() => {
    if (visible) {
      previousActiveElement.current = document.activeElement as HTMLElement;

      // Focus first button after animation
      const timer = setTimeout(() => {
        const firstButton = alertRef.current?.querySelector('button');
        firstButton?.focus();
      }, 100);

      document.addEventListener('keydown', handleKeyDown);

      return () => {
        clearTimeout(timer);
        document.removeEventListener('keydown', handleKeyDown);
      };
    } else {
      // Restore focus when closing
      previousActiveElement.current?.focus();
    }
  }, [visible, handleKeyDown]);

  // Action button variant mapping
  const getActionVariant = (style: IOSAlertAction['style']) => {
    switch (style) {
      case 'cancel':
        return 'secondary';
      case 'destructive':
        return 'destructive';
      default:
        return 'primary';
    }
  };

  return (
    <AnimatePresence>
      {visible && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          
          {/* Alert Container */}
          <div
            ref={alertRef}
            className="fixed inset-0 flex items-center justify-center z-50 p-4"
            role="dialog"
            aria-modal="true"
            aria-labelledby="ios-alert-title"
          >
            <motion.div
              className={`
                relative w-full max-w-sm mx-auto
                bg-white/95 dark:bg-gray-800/95
                backdrop-blur-xl
                rounded-2xl
                shadow-2xl
                border border-white/20 dark:border-gray-700/50
                overflow-hidden
                ${className}
              `}
              initial={{ opacity: 0, scale: 0.8, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: 20 }}
              transition={iosAnimations.spring}
            >
              {/* Glass morphism overlay */}
              <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent pointer-events-none" />
              
              {/* Content */}
              <div className="relative z-10 p-6">
                {/* Icon */}
                <div className="flex justify-center mb-4">
                  {customIcon || (
                    <StatusEmoji 
                      status={config.emoji}
                      size="lg" 
                      animated 
                    />
                  )}
                </div>
                
                {/* Title */}
                {title && (
                  <h3
                    id="ios-alert-title"
                    className={`
                    text-lg font-semibold text-center mb-2
                    ${config.titleColor}
                  `}>
                    {title}
                  </h3>
                )}
                
                {/* Message */}
                {message && (
                  <p className="text-gray-600 dark:text-gray-300 text-center leading-relaxed mb-6">
                    {message}
                  </p>
                )}
                
                {/* Actions */}
                <div className={`
                  flex gap-3
                  ${actions.length > 2 ? 'flex-col' : 'flex-row'}
                `}>
                  {actions.map((action, index) => (
                    <IOSButton
                      key={index}
                      variant={getActionVariant(action.style)}
                      size="md"
                      disabled={action.disabled}
                      onClick={action.onPress}
                      className={`
                        ${actions.length <= 2 ? 'flex-1' : ''}
                        ${action.style === 'cancel' ? 'order-last' : ''}
                      `}
                    >
                      {action.label}
                    </IOSButton>
                  ))}
                </div>
              </div>
              
              {/* Close Button */}
              {showCloseButton && (
                <motion.button
                  className="absolute top-2 right-2 w-11 h-11 flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                  onClick={onClose}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  aria-label="Close"
                >
                  ✕
                </motion.button>
              )}
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};
