/**
 * useOnboardingTour — manages first-time onboarding tour state for Canvas.
 *
 * Persists "seen" status in localStorage so the tour only shows once.
 * Exposes start/dismiss/advance controls consumed by OnboardingTour component.
 */

import { useState, useCallback, useEffect } from 'react';

const STORAGE_KEY = 'vulca_tour_seen';

export interface TourStep {
  /** CSS selector for the target element (expects data-tour-* attributes). */
  target: string;
  title: string;
  description: string;
}

export const TOUR_STEPS: TourStep[] = [
  {
    target: '[data-tour-intent]',
    title: 'Describe Your Vision',
    description: 'Type a creative prompt or upload an image. The AI Scout will analyze cultural context and gather references automatically.',
  },
  {
    target: '[data-tour-tradition]',
    title: 'Tradition Auto-Detect',
    description: 'VULCA detects the cultural tradition from your prompt — Chinese ink wash, Japanese wabi-sabi, Persian miniature, and more. You can also pick one manually.',
  },
  {
    target: '[data-tour-modes]',
    title: 'Workspace Modes',
    description: 'Edit mode designs the agent pipeline visually. Run mode shows live creation results. Traditions mode lets you explore and customize cultural styles.',
  },
  {
    target: '[data-tour-hitl]',
    title: 'Creation Mode',
    description: 'Preview for instant free mockups. Guided pauses at each stage for your review. Generate runs the full pipeline automatically with real AI images.',
  },
  {
    target: '[data-tour-canvas]',
    title: 'Your Canvas',
    description: 'This is where the magic happens. Candidates appear here as the Scout, Draft, Critic, and Queen agents collaborate in real time.',
  },
];

export function useOnboardingTour() {
  const [isOpen, setIsOpen] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  // Show tour on first visit (skip in CI/test/Playwright environments)
  useEffect(() => {
    const isTest = navigator.webdriver || window.location.search.includes('skip_tour');
    const seen = localStorage.getItem(STORAGE_KEY);
    if (!seen && !isTest) {
      const timer = setTimeout(() => setIsOpen(true), 800);
      return () => clearTimeout(timer);
    }
    if (isTest && !seen) {
      localStorage.setItem(STORAGE_KEY, 'true');
    }
  }, []);

  const dismiss = useCallback(() => {
    setIsOpen(false);
    setCurrentStep(0);
    localStorage.setItem(STORAGE_KEY, 'true');
  }, []);

  const next = useCallback(() => {
    if (currentStep < TOUR_STEPS.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      dismiss();
    }
  }, [currentStep, dismiss]);

  const prev = useCallback(() => {
    setCurrentStep(prev => Math.max(0, prev - 1));
  }, []);

  const restart = useCallback(() => {
    setCurrentStep(0);
    setIsOpen(true);
  }, []);

  return { isOpen, currentStep, steps: TOUR_STEPS, next, prev, dismiss, restart };
}
