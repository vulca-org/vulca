import { useState, useCallback } from 'react';
import { API_PREFIX, getProtoAuthHeaders } from '../config/api';

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
        const response = await fetch(`${API_PREFIX}/feedback`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...getProtoAuthHeaders(),
          },
          body: JSON.stringify({
            evaluation_id: evaluationId,
            rating,
            comment: comment || '',
            feedback_type: feedbackType || 'explicit',
          }),
        });

        if (!response.ok) {
          throw new Error(`Failed to submit feedback: ${response.statusText}`);
        }

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
