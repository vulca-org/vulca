import React, { useEffect, useRef, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { IOSButton } from '../ios';
import { IOSSegmentedControl } from '../ios';
import { iosAnimations } from '../ios/utils/animations';

interface FeedbackModalProps {
  visible: boolean;
  onClose: () => void;
  onSubmit: (comment: string, type: string) => void;
  rating: string;
}

const FEEDBACK_TYPES = ['General', 'Quality Issue', 'Suggestion'];

const FeedbackModal: React.FC<FeedbackModalProps> = ({
  visible,
  onClose,
  onSubmit,
  rating,
}) => {
  const [comment, setComment] = useState('');
  const [selectedTypeIndex, setSelectedTypeIndex] = useState(0);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const modalRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  // Auto-focus the textarea when modal opens
  useEffect(() => {
    if (visible) {
      previousActiveElement.current = document.activeElement as HTMLElement;
      const timer = setTimeout(() => {
        textareaRef.current?.focus();
      }, 100);
      return () => clearTimeout(timer);
    } else {
      previousActiveElement.current?.focus();
      // Reset state when closing
      setComment('');
      setSelectedTypeIndex(0);
    }
  }, [visible]);

  // Focus trap and keyboard handling
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
        return;
      }

      if (e.key !== 'Tab') return;

      const focusableElements = modalRef.current?.querySelectorAll(
        'button, textarea, [tabindex]:not([tabindex="-1"])'
      );

      if (!focusableElements || focusableElements.length === 0) return;

      const firstElement = focusableElements[0] as HTMLElement;
      const lastElement = focusableElements[
        focusableElements.length - 1
      ] as HTMLElement;

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
    },
    [onClose]
  );

  useEffect(() => {
    if (visible) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [visible, handleKeyDown]);

  const handleSubmit = () => {
    onSubmit(comment, FEEDBACK_TYPES[selectedTypeIndex]);
  };

  const ratingLabel = rating === 'up' ? 'Positive' : 'Negative';

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

          {/* Modal Container */}
          <div
            ref={modalRef}
            className="fixed inset-0 flex items-center justify-center z-50 p-4"
            role="dialog"
            aria-modal="true"
            aria-labelledby="feedback-modal-title"
          >
            <motion.div
              className="
                relative w-full max-w-md mx-auto
                bg-white/95 dark:bg-gray-800/95
                backdrop-blur-xl
                rounded-2xl
                shadow-2xl
                border border-white/20 dark:border-gray-700/50
                overflow-hidden
              "
              initial={{ opacity: 0, scale: 0.8, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: 20 }}
              transition={iosAnimations.spring}
            >
              {/* Glass morphism overlay */}
              <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent pointer-events-none" />

              {/* Content */}
              <div className="relative z-10 p-6">
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3
                      id="feedback-modal-title"
                      className="text-lg font-semibold text-gray-900 dark:text-gray-100"
                    >
                      Add Feedback
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                      Rating: {ratingLabel}
                    </p>
                  </div>
                  <motion.button
                    className="w-11 h-11 flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                    onClick={onClose}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    aria-label="Close"
                  >
                    <X className="w-5 h-5" />
                  </motion.button>
                </div>

                {/* Feedback Type Selector */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Feedback Type
                  </label>
                  <IOSSegmentedControl
                    segments={FEEDBACK_TYPES}
                    selectedIndex={selectedTypeIndex}
                    onChange={(index) => setSelectedTypeIndex(index)}
                    size="compact"
                    className="w-full"
                  />
                </div>

                {/* Comment Textarea */}
                <div className="mb-6">
                  <label
                    htmlFor="feedback-comment"
                    className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                  >
                    Comment (optional)
                  </label>
                  <textarea
                    ref={textareaRef}
                    id="feedback-comment"
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    placeholder="Share your thoughts on this evaluation..."
                    className="
                      w-full px-4 py-3
                      border border-gray-200 dark:border-gray-600
                      rounded-xl
                      bg-white/80 dark:bg-gray-900/50
                      text-gray-900 dark:text-gray-100
                      placeholder-gray-400 dark:placeholder-gray-500
                      focus:outline-none focus:ring-2 focus:ring-slate-500/30
                      resize-none
                      transition-shadow duration-200
                    "
                    rows={4}
                  />
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                  <IOSButton
                    variant="secondary"
                    size="md"
                    onClick={onClose}
                    className="flex-1"
                  >
                    Cancel
                  </IOSButton>
                  <IOSButton
                    variant="primary"
                    size="md"
                    onClick={handleSubmit}
                    className="flex-1"
                  >
                    Submit
                  </IOSButton>
                </div>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};

export default FeedbackModal;
