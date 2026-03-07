import { useState, useCallback } from 'react';
import { API_PREFIX } from '../config/api';

interface UseFeedbackReturn {
  submit: (
    evaluationId: string,
    rating: string,
    comment?: string,
    feedbackType?: string
  ) => Promise<void>;
  isSubmitting: boolean;
  isSubmitted: boolean;
  error: string | null;
  reset: () => void;
}

/**
 * Custom hook for submitting evaluation feedback.
 *
 * Currently uses a mock implementation (resolves after 500ms) since the
 * backend endpoint may not be deployed yet. Once `/api/v1/feedback` is
 * available, remove the mock and uncomment the fetch call below.
 */
export function useFeedback(): UseFeedbackReturn {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = useCallback(
    async (
      evaluationId: string,
      rating: string,
      comment?: string,
      feedbackType?: string
    ) => {
      setIsSubmitting(true);
      setError(null);

      try {
        // --- Mock implementation (remove when backend is ready) ---
        await new Promise((resolve) => setTimeout(resolve, 500));

        // Log for debugging during development
        if (import.meta.env.DEV) {
          // eslint-disable-next-line no-console
          console.log('[useFeedback] submitted', {
            url: `${API_PREFIX}/feedback`,
            evaluationId,
            rating,
            comment,
            feedbackType,
          });
        }

        // --- Real implementation (uncomment when backend is ready) ---
        // const response = await fetch(`${API_PREFIX}/feedback`, {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify({
        //     evaluation_id: evaluationId,
        //     rating,
        //     comment,
        //     feedback_type: feedbackType,
        //   }),
        // });
        //
        // if (!response.ok) {
        //   throw new Error(`Failed to submit feedback: ${response.statusText}`);
        // }

        setIsSubmitted(true);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to submit feedback';
        setError(message);
      } finally {
        setIsSubmitting(false);
      }
    },
    []
  );

  const reset = useCallback(() => {
    setIsSubmitting(false);
    setIsSubmitted(false);
    setError(null);
  }, []);

  return { submit, isSubmitting, isSubmitted, error, reset };
}
