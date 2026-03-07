import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { IOSButton } from '../ios';
import { iosAnimations } from '../ios/utils/animations';
import { useFeedback } from '../../hooks/useFeedback';
import FeedbackModal from './FeedbackModal';

interface FeedbackButtonsProps {
  evaluationId: string;
  onFeedbackSubmit?: (rating: string, comment?: string) => void;
}

const FeedbackButtons: React.FC<FeedbackButtonsProps> = ({
  evaluationId,
  onFeedbackSubmit,
}) => {
  const [selectedRating, setSelectedRating] = useState<'up' | 'down' | null>(
    null
  );
  const [showThankYou, setShowThankYou] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const { submit, isSubmitting } = useFeedback();

  const handleRatingClick = async (rating: 'up' | 'down') => {
    if (selectedRating === rating) return; // Already selected

    setSelectedRating(rating);
    setShowThankYou(true);

    // Submit the rating immediately
    await submit(evaluationId, rating);
    onFeedbackSubmit?.(rating);

    // Hide "thank you" after a short delay
    setTimeout(() => {
      setShowThankYou(false);
    }, 2000);
  };

  const handleOpenModal = () => {
    if (!selectedRating) return;
    setShowModal(true);
  };

  const handleModalSubmit = async (comment: string, feedbackType: string) => {
    if (!selectedRating) return;

    await submit(evaluationId, selectedRating, comment, feedbackType);
    onFeedbackSubmit?.(selectedRating, comment);
    setShowModal(false);
  };

  return (
    <>
      <div className="flex items-center gap-2">
        {/* Thumbs Up */}
        <motion.div
          whileTap={{ scale: 0.88 }}
          transition={iosAnimations.spring}
        >
          <IOSButton
            variant="glass"
            size="sm"
            disabled={isSubmitting}
            onClick={() => handleRatingClick('up')}
            aria-label="Thumbs up"
            aria-pressed={selectedRating === 'up'}
            className={
              selectedRating === 'up'
                ? 'ring-2 ring-green-500/40 bg-green-50/20 dark:bg-green-900/20'
                : ''
            }
          >
            <ThumbsUp
              className={`w-4 h-4 ${
                selectedRating === 'up'
                  ? 'text-green-600 dark:text-green-400'
                  : 'text-gray-600 dark:text-gray-400'
              }`}
            />
          </IOSButton>
        </motion.div>

        {/* Thumbs Down */}
        <motion.div
          whileTap={{ scale: 0.88 }}
          transition={iosAnimations.spring}
        >
          <IOSButton
            variant="glass"
            size="sm"
            disabled={isSubmitting}
            onClick={() => handleRatingClick('down')}
            aria-label="Thumbs down"
            aria-pressed={selectedRating === 'down'}
            className={
              selectedRating === 'down'
                ? 'ring-2 ring-red-500/40 bg-red-50/20 dark:bg-red-900/20'
                : ''
            }
          >
            <ThumbsDown
              className={`w-4 h-4 ${
                selectedRating === 'down'
                  ? 'text-red-600 dark:text-red-400'
                  : 'text-gray-600 dark:text-gray-400'
              }`}
            />
          </IOSButton>
        </motion.div>

        {/* Add Comment Button (visible after selecting a rating) */}
        <AnimatePresence>
          {selectedRating && !showThankYou && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8, width: 0 }}
              animate={{ opacity: 1, scale: 1, width: 'auto' }}
              exit={{ opacity: 0, scale: 0.8, width: 0 }}
              transition={iosAnimations.spring}
            >
              <IOSButton
                variant="text"
                size="sm"
                onClick={handleOpenModal}
                className="text-xs whitespace-nowrap"
              >
                Add Comment
              </IOSButton>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Thank You Message */}
        <AnimatePresence>
          {showThankYou && (
            <motion.span
              className="text-sm text-green-600 dark:text-green-400 font-medium whitespace-nowrap"
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 8 }}
              transition={{ duration: 0.3, ease: 'easeOut' }}
            >
              Thanks!
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      {/* Feedback Modal */}
      {selectedRating && (
        <FeedbackModal
          visible={showModal}
          onClose={() => setShowModal(false)}
          onSubmit={handleModalSubmit}
          rating={selectedRating}
        />
      )}
    </>
  );
};

export default FeedbackButtons;
