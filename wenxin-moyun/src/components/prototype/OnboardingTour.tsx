/**
 * OnboardingTour — 5-step spotlight tour for first-time Canvas visitors.
 *
 * Uses a full-screen overlay with a spotlight cutout around the target element.
 * Tooltip card follows the target with framer-motion animations.
 * Art Professional palette — no blue/purple/indigo/violet.
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { IOSButton } from '../ios';
import { useOnboardingTour } from '../../hooks/useOnboardingTour';
import type { TourStep } from '../../hooks/useOnboardingTour';

/** Bounding rect for a target element (or null if not found). */
interface TargetRect {
  top: number;
  left: number;
  width: number;
  height: number;
}

/** Compute the position for the tooltip so it stays within the viewport. */
function computeTooltipPosition(rect: TargetRect, tooltipWidth: number, tooltipHeight: number) {
  const pad = 16;
  const arrowGap = 12;
  const vw = window.innerWidth;
  const vh = window.innerHeight;

  // Default: place below the target, centered horizontally
  let top = rect.top + rect.height + arrowGap;
  let left = rect.left + rect.width / 2 - tooltipWidth / 2;

  // If tooltip overflows bottom, place above
  if (top + tooltipHeight + pad > vh) {
    top = rect.top - tooltipHeight - arrowGap;
  }

  // Clamp horizontal
  left = Math.max(pad, Math.min(left, vw - tooltipWidth - pad));

  // If tooltip overflows top, center vertically
  if (top < pad) {
    top = Math.max(pad, rect.top + rect.height / 2 - tooltipHeight / 2);
  }

  return { top, left };
}

function StepDots({ total, current }: { total: number; current: number }) {
  return (
    <div className="flex items-center gap-1.5">
      {Array.from({ length: total }, (_, i) => (
        <div
          key={i}
          className={[
            'w-1.5 h-1.5 rounded-full transition-all duration-300',
            i === current
              ? 'w-4 bg-[#C87F4A]'
              : i < current
                ? 'bg-[#C87F4A]/40'
                : 'bg-gray-300 dark:bg-gray-600',
          ].join(' ')}
        />
      ))}
    </div>
  );
}

function TourTooltip({
  step,
  stepIndex,
  totalSteps,
  targetRect,
  onNext,
  onSkip,
}: {
  step: TourStep;
  stepIndex: number;
  totalSteps: number;
  targetRect: TargetRect | null;
  onNext: () => void;
  onSkip: () => void;
}) {
  const tooltipRef = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState<{ top: number; left: number }>({ top: 0, left: 0 });

  const isLast = stepIndex === totalSteps - 1;

  useEffect(() => {
    if (!targetRect) return;
    const tw = 340;
    const th = 200; // estimated height
    const computed = computeTooltipPosition(targetRect, tw, th);
    setPos(computed);
  }, [targetRect]);

  if (!targetRect) return null;

  return (
    <motion.div
      ref={tooltipRef}
      initial={{ opacity: 0, scale: 0.92, y: 8 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.92, y: 8 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className="fixed z-[10002] w-[340px]"
      style={{ top: pos.top, left: pos.left }}
    >
      <div className="rounded-2xl bg-white dark:bg-[#1A1614] border border-gray-200 dark:border-[#342E28] shadow-xl p-5">
        {/* Step counter */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-[11px] font-medium text-gray-400 dark:text-gray-500 uppercase tracking-wider">
            Step {stepIndex + 1} of {totalSteps}
          </span>
          <StepDots total={totalSteps} current={stepIndex} />
        </div>

        {/* Title */}
        <h3 className="text-base font-semibold text-[#334155] dark:text-white mb-1.5">
          {step.title}
        </h3>

        {/* Description */}
        <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed mb-5">
          {step.description}
        </p>

        {/* Actions */}
        <div className="flex items-center justify-between">
          <button
            onClick={onSkip}
            className="text-xs text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            Skip tour
          </button>
          <IOSButton
            variant="primary"
            size="sm"
            onClick={onNext}
          >
            {isLast ? 'Start Creating' : 'Next'}
          </IOSButton>
        </div>
      </div>
    </motion.div>
  );
}

export default function OnboardingTour() {
  const { isOpen, currentStep, steps, next, dismiss } = useOnboardingTour();
  const [targetRect, setTargetRect] = useState<TargetRect | null>(null);

  // Find and measure the target element for the current step
  const measureTarget = useCallback(() => {
    if (!isOpen || !steps[currentStep]) {
      setTargetRect(null);
      return;
    }

    const el = document.querySelector(steps[currentStep].target);
    if (!el) {
      // Target not found — fallback to centered position
      setTargetRect({
        top: window.innerHeight / 2 - 40,
        left: window.innerWidth / 2 - 100,
        width: 200,
        height: 80,
      });
      return;
    }

    const rect = el.getBoundingClientRect();
    const pad = 8;
    setTargetRect({
      top: rect.top - pad,
      left: rect.left - pad,
      width: rect.width + pad * 2,
      height: rect.height + pad * 2,
    });
  }, [isOpen, currentStep, steps]);

  useEffect(() => {
    measureTarget();
  }, [measureTarget]);

  // Re-measure on scroll/resize
  useEffect(() => {
    if (!isOpen) return;

    const handleResize = () => measureTarget();
    window.addEventListener('resize', handleResize);
    window.addEventListener('scroll', handleResize, true);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('scroll', handleResize, true);
    };
  }, [isOpen, measureTarget]);

  // Scroll target into view when step changes
  useEffect(() => {
    if (!isOpen || !steps[currentStep]) return;
    const el = document.querySelector(steps[currentStep].target);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      // Re-measure after scroll
      const timer = setTimeout(measureTarget, 350);
      return () => clearTimeout(timer);
    }
  }, [isOpen, currentStep, steps, measureTarget]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop overlay with spotlight cutout via box-shadow */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 z-[10000]"
            onClick={dismiss}
            aria-hidden="true"
          >
            {targetRect && (
              <div
                className="absolute rounded-xl transition-all duration-300 ease-out"
                style={{
                  top: targetRect.top,
                  left: targetRect.left,
                  width: targetRect.width,
                  height: targetRect.height,
                  boxShadow: '0 0 0 9999px rgba(0,0,0,0.6)',
                }}
              />
            )}
          </motion.div>

          {/* Highlight area — pointer-events-none so users can interact with the target */}
          {targetRect && (
            <div
              className="fixed z-[10001] rounded-xl pointer-events-none"
              style={{
                top: targetRect.top,
                left: targetRect.left,
                width: targetRect.width,
                height: targetRect.height,
              }}
            />
          )}

          {/* Tooltip */}
          <TourTooltip
            key={currentStep}
            step={steps[currentStep]}
            stepIndex={currentStep}
            totalSteps={steps.length}
            targetRect={targetRect}
            onNext={next}
            onSkip={dismiss}
          />
        </>
      )}
    </AnimatePresence>
  );
}
