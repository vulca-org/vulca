import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, MessageSquare, Globe, Search, Brain, ShieldCheck } from 'lucide-react';
import { IOSButton, IOSCard, IOSCardContent } from '../ios';

const PIPELINE_STEPS = [
  {
    id: 'intent',
    title: 'Intent Parsing',
    description: 'Analyzes your natural-language prompt to determine evaluation goals, target culture, and quality dimensions.',
    icon: MessageSquare,
  },
  {
    id: 'tradition',
    title: 'Tradition Detection',
    description: 'Identifies the most relevant cultural tradition (e.g., Chinese Ink, Japanese Ukiyo-e) based on intent and image content.',
    icon: Globe,
  },
  {
    id: 'scout',
    title: 'Scout Evidence',
    description: 'Gathers visual and contextual evidence from the image using multi-modal analysis agents.',
    icon: Search,
  },
  {
    id: 'scoring',
    title: 'VLM Scoring',
    description: 'Runs scoring across all relevant dimensions using vision-language models with calibrated rubrics.',
    icon: Brain,
  },
  {
    id: 'risk',
    title: 'Risk Analysis',
    description: 'Evaluates cultural sensitivity, factual accuracy, and potential risks with severity classification.',
    icon: ShieldCheck,
  },
];

export const FlowToggle: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
      className="w-full"
    >
      <IOSButton
        variant="secondary"
        size="md"
        onClick={() => setIsExpanded((v) => !v)}
        className="w-full justify-between"
      >
        <span>Show how it works</span>
        <motion.span
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.25 }}
          className="ml-2"
        >
          <ChevronDown className="w-4 h-4" />
        </motion.span>
      </IOSButton>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.35, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="pt-4 space-y-0">
              {PIPELINE_STEPS.map((step, index) => {
                const StepIcon = step.icon;
                const isLast = index === PIPELINE_STEPS.length - 1;

                return (
                  <div key={step.id} className="relative flex gap-4">
                    {/* Vertical connector line */}
                    {!isLast && (
                      <div className="absolute left-5 top-12 bottom-0 w-px bg-gray-200 dark:bg-gray-700" />
                    )}

                    {/* Step icon */}
                    <div className="relative z-10 flex-shrink-0 w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                      <StepIcon className="w-4.5 h-4.5 text-slate-600 dark:text-slate-300" />
                    </div>

                    {/* Step card */}
                    <div className="flex-1 pb-4">
                      <IOSCard variant="flat" padding="sm" animate={false}>
                        <IOSCardContent>
                          <p className="text-sm font-semibold text-gray-900 dark:text-white mb-0.5">
                            {step.title}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                            {step.description}
                          </p>
                        </IOSCardContent>
                      </IOSCard>
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default FlowToggle;
