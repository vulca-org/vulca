/**
 * FeedbackCollector — collects user feedback after pipeline evaluation.
 *
 * Features:
 * - 5-star clickable rating with hover preview
 * - Text comment textarea
 * - Submit to POST /api/v1/feedback (no auth required for feedback)
 * - Success/failure state feedback via inline banners
 *
 * Backend maps: rating >= 3 stars → "thumbs_up", < 3 → "thumbs_down".
 * The exact star count is appended to the comment for richer data.
 */

import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { IOSCard, IOSCardHeader, IOSCardContent, IOSButton } from '../ios';
import { API_PREFIX, getProtoAuthHeaders } from '../../config/api';

interface FeedbackCollectorProps {
  sessionId: string;
  evaluationId: string;
  candidateId?: string;
  tradition?: string;
  scoresSnapshot?: Record<string, number>;
  onSubmit?: () => void;
  onCreateAnother?: () => void;
}

type SubmitStatus = 'idle' | 'submitting' | 'success' | 'error';

export default function FeedbackCollector({ sessionId, evaluationId, candidateId, tradition, scoresSnapshot, onSubmit, onCreateAnother }: FeedbackCollectorProps) {
  const [rating, setRating] = useState(0);
  const [hoveredStar, setHoveredStar] = useState(0);
  const [comment, setComment] = useState('');
  const [status, setStatus] = useState<SubmitStatus>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  // Suppress unused-var lint for sessionId (included in comment payload)
  void sessionId;

  const displayRating = hoveredStar || rating;

  const handleSubmit = useCallback(async () => {
    if (rating === 0) return;

    setStatus('submitting');
    setErrorMessage('');

    const ratingLabel = rating >= 3 ? 'thumbs_up' : 'thumbs_down';
    const enrichedComment = comment
      ? `[${rating}/5 stars] ${comment}`
      : `[${rating}/5 stars]`;

    try {
      const res = await fetch(`${API_PREFIX}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getProtoAuthHeaders(),
        },
        body: JSON.stringify({
          evaluation_id: evaluationId,
          rating: ratingLabel,
          comment: enrichedComment,
          feedback_type: 'explicit',
          candidate_id: candidateId || '',
          tradition: tradition || '',
          scores_snapshot: scoresSnapshot || null,
        }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }

      setStatus('success');
      onSubmit?.();
    } catch (err) {
      setStatus('error');
      setErrorMessage(err instanceof Error ? err.message : 'Failed to submit feedback');
    }
  }, [rating, comment, evaluationId, candidateId, tradition, scoresSnapshot, onSubmit]);

  if (status === 'success') {
    return (
      <IOSCard variant="elevated" padding="md" animate={false}>
        <IOSCardContent>
          <div className="text-center py-3">
            <div className="text-2xl mb-2">&#x2705;</div>
            <p className="text-sm font-semibold text-[#5F8A50] dark:text-[#87A878]">
              Feedback submitted
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Thank you for your feedback!
            </p>
            {onCreateAnother && (
              <div className="mt-3">
                <IOSButton variant="primary" size="sm" onClick={onCreateAnother}>
                  Create Another
                </IOSButton>
              </div>
            )}
          </div>
        </IOSCardContent>
      </IOSCard>
    );
  }

  return (
    <IOSCard variant="elevated" padding="md" animate={false}>
      <IOSCardHeader title="Feedback" subtitle="Rate this evaluation" />
      <IOSCardContent>
        <div className="space-y-4">
          {/* 5-star rating */}
          <div>
            <div className="flex items-center gap-1" role="radiogroup" aria-label="Rating">
              {[1, 2, 3, 4, 5].map((star) => (
                <motion.button
                  key={star}
                  type="button"
                  onClick={() => setRating(star)}
                  onMouseEnter={() => setHoveredStar(star)}
                  onMouseLeave={() => setHoveredStar(0)}
                  whileTap={{ scale: 0.85 }}
                  whileHover={{ scale: 1.15 }}
                  className="p-1 focus:outline-none focus:ring-2 focus:ring-[#C87F4A]/30 rounded-lg min-w-[44px] min-h-[44px] flex items-center justify-center"
                  aria-label={`${star} star${star > 1 ? 's' : ''}`}
                  role="radio"
                  aria-checked={rating === star}
                >
                  <span
                    className={`text-2xl transition-colors duration-150 ${
                      star <= displayRating
                        ? 'text-amber-400'
                        : 'text-gray-300 dark:text-gray-600'
                    }`}
                  >
                    &#9733;
                  </span>
                </motion.button>
              ))}
              {rating > 0 && (
                <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
                  {rating}/5
                </span>
              )}
            </div>
          </div>

          {/* Comment textarea */}
          <div>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Add a comment (optional)..."
              rows={3}
              className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 resize-none focus:outline-none focus:ring-2 focus:ring-[#C87F4A]/30 dark:focus:ring-[#C87F4A] focus:border-transparent transition-all"
            />
          </div>

          {/* Error banner */}
          {status === 'error' && (
            <div className="rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 p-2 text-xs text-red-700 dark:text-red-300">
              {errorMessage || 'Something went wrong. Please try again.'}
            </div>
          )}

          {/* Submit button */}
          <IOSButton
            variant="primary"
            size="sm"
            disabled={rating === 0 || status === 'submitting'}
            onClick={handleSubmit}
          >
            {status === 'submitting' ? 'Submitting...' : 'Submit Feedback'}
          </IOSButton>
        </div>
      </IOSCardContent>
    </IOSCard>
  );
}
