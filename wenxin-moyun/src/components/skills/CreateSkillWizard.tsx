import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, Check, Plus, X } from 'lucide-react';
import {
  IOSButton,
  IOSCard,
  IOSCardContent,
} from '../ios';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface SkillDraft {
  name: string;
  description: string;
  tags: string[];
  config: ConfigEntry[];
}

interface ConfigEntry {
  key: string;
  value: string;
}

// ---------------------------------------------------------------------------
// Available tags
// ---------------------------------------------------------------------------

const AVAILABLE_TAGS = [
  'brand', 'design', 'audience', 'marketing', 'trends',
  'culture', 'quality', 'accessibility', 'emotion', 'performance',
];

const TAG_COLORS: Record<string, string> = {
  brand: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300 border-blue-200 dark:border-blue-800',
  design: 'bg-violet-100 text-violet-700 dark:bg-violet-900/40 dark:text-violet-300 border-violet-200 dark:border-violet-800',
  audience: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300 border-green-200 dark:border-green-800',
  marketing: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300 border-orange-200 dark:border-orange-800',
  trends: 'bg-pink-100 text-pink-700 dark:bg-pink-900/40 dark:text-pink-300 border-pink-200 dark:border-pink-800',
  culture: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300 border-amber-200 dark:border-amber-800',
  quality: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/40 dark:text-cyan-300 border-cyan-200 dark:border-cyan-800',
  accessibility: 'bg-teal-100 text-teal-700 dark:bg-teal-900/40 dark:text-teal-300 border-teal-200 dark:border-teal-800',
  emotion: 'bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300 border-rose-200 dark:border-rose-800',
  performance: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800',
};

function getTagColor(tag: string): string {
  return TAG_COLORS[tag] ?? 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-700';
}

// ---------------------------------------------------------------------------
// Steps
// ---------------------------------------------------------------------------

const STEPS = [
  { label: 'Basics', description: 'Name & Description' },
  { label: 'Tags', description: 'Categorization' },
  { label: 'Config', description: 'Parameters' },
  { label: 'Review', description: 'Confirm & Submit' },
];

// ---------------------------------------------------------------------------
// CreateSkillWizard Component
// ---------------------------------------------------------------------------

interface CreateSkillWizardProps {
  onClose: () => void;
}

export default function CreateSkillWizard({ onClose }: CreateSkillWizardProps) {
  const [step, setStep] = useState(0);
  const [draft, setDraft] = useState<SkillDraft>({
    name: '',
    description: '',
    tags: [],
    config: [{ key: '', value: '' }],
  });
  const [submitted, setSubmitted] = useState(false);

  // Navigation
  const canNext = () => {
    if (step === 0) return draft.name.trim().length > 0 && draft.description.trim().length > 0;
    if (step === 1) return draft.tags.length > 0;
    return true;
  };

  const handleNext = () => {
    if (step < STEPS.length - 1) setStep(step + 1);
  };

  const handleBack = () => {
    if (step > 0) setStep(step - 1);
  };

  const handleSubmit = () => {
    setSubmitted(true);
    // In a real app, this would POST to the API
  };

  // Tag toggle
  const toggleTag = (tag: string) => {
    setDraft((prev) => ({
      ...prev,
      tags: prev.tags.includes(tag)
        ? prev.tags.filter((t) => t !== tag)
        : [...prev.tags, tag],
    }));
  };

  // Config entry management
  const updateConfig = (index: number, field: 'key' | 'value', val: string) => {
    setDraft((prev) => {
      const config = [...prev.config];
      config[index] = { ...config[index], [field]: val };
      return { ...prev, config };
    });
  };

  const addConfigEntry = () => {
    setDraft((prev) => ({
      ...prev,
      config: [...prev.config, { key: '', value: '' }],
    }));
  };

  const removeConfigEntry = (index: number) => {
    setDraft((prev) => ({
      ...prev,
      config: prev.config.filter((_, i) => i !== index),
    }));
  };

  // Success state
  if (submitted) {
    return (
      <div className="text-center py-12 space-y-4">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 300, damping: 20 }}
          className="w-16 h-16 mx-auto rounded-full bg-green-100 dark:bg-green-900/40 flex items-center justify-center"
        >
          <Check className="w-8 h-8 text-green-600 dark:text-green-400" />
        </motion.div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Skill Created
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 max-w-sm mx-auto">
          "{draft.name}" has been submitted for review and will appear in the marketplace once approved.
        </p>
        <IOSButton variant="primary" size="md" onClick={onClose}>
          Done
        </IOSButton>
      </div>
    );
  }

  return (
    <div className="space-y-6 py-2">
      {/* Progress indicator */}
      <div className="flex items-center gap-1">
        {STEPS.map((s, i) => (
          <div key={s.label} className="flex-1 flex items-center">
            <div className="flex-1">
              <div
                className={`h-1.5 rounded-full transition-colors duration-300 ${
                  i <= step
                    ? 'bg-slate-700 dark:bg-slate-400'
                    : 'bg-gray-200 dark:bg-gray-700'
                }`}
              />
              <p className={`text-[11px] mt-1.5 ${
                i === step
                  ? 'text-gray-900 dark:text-white font-medium'
                  : 'text-gray-400 dark:text-gray-500'
              }`}>
                {s.label}
              </p>
            </div>
            {i < STEPS.length - 1 && <div className="w-1" />}
          </div>
        ))}
      </div>

      {/* Step content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={step}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.2 }}
        >
          {/* Step 0: Basics */}
          {step === 0 && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                  Skill Name
                </label>
                <input
                  type="text"
                  placeholder="e.g., Brand Consistency"
                  value={draft.name}
                  onChange={(e) => setDraft((prev) => ({ ...prev, name: e.target.value }))}
                  className="w-full px-4 py-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-slate-500/40 transition"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                  Description
                </label>
                <textarea
                  rows={4}
                  placeholder="Describe what this skill evaluates and how it works..."
                  value={draft.description}
                  onChange={(e) => setDraft((prev) => ({ ...prev, description: e.target.value }))}
                  className="w-full px-4 py-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-slate-500/40 resize-none transition"
                />
              </div>
            </div>
          )}

          {/* Step 1: Tags */}
          {step === 1 && (
            <div className="space-y-4">
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Select one or more tags to categorize your skill.
              </p>
              <div className="flex flex-wrap gap-2">
                {AVAILABLE_TAGS.map((tag) => {
                  const selected = draft.tags.includes(tag);
                  return (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => toggleTag(tag)}
                      className={`text-sm px-3.5 py-1.5 rounded-full border transition-all ${
                        selected
                          ? getTagColor(tag)
                          : 'border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'
                      }`}
                    >
                      {selected && <Check className="w-3 h-3 inline mr-1 -mt-0.5" />}
                      {tag}
                    </button>
                  );
                })}
              </div>
              {draft.tags.length > 0 && (
                <p className="text-xs text-gray-400 dark:text-gray-500">
                  {draft.tags.length} tag{draft.tags.length !== 1 ? 's' : ''} selected
                </p>
              )}
            </div>
          )}

          {/* Step 2: Config */}
          {step === 2 && (
            <div className="space-y-4">
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Define configuration parameters as key-value pairs.
              </p>
              <div className="space-y-2">
                {draft.config.map((entry, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <input
                      type="text"
                      placeholder="Key"
                      value={entry.key}
                      onChange={(e) => updateConfig(i, 'key', e.target.value)}
                      className="flex-1 px-3 py-2.5 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-slate-500/40 transition"
                    />
                    <input
                      type="text"
                      placeholder="Value"
                      value={entry.value}
                      onChange={(e) => updateConfig(i, 'value', e.target.value)}
                      className="flex-1 px-3 py-2.5 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-slate-500/40 transition"
                    />
                    {draft.config.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeConfigEntry(i)}
                        className="p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-400 hover:text-red-500 transition-colors flex-shrink-0"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
              <button
                type="button"
                onClick={addConfigEntry}
                className="flex items-center gap-1.5 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Add Parameter
              </button>
            </div>
          )}

          {/* Step 3: Review */}
          {step === 3 && (
            <div className="space-y-4">
              <IOSCard variant="bordered" padding="md">
                <IOSCardContent className="space-y-3">
                  <div>
                    <span className="text-xs text-gray-500 dark:text-gray-400">Name</span>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">{draft.name}</p>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500 dark:text-gray-400">Description</span>
                    <p className="text-sm text-gray-700 dark:text-gray-300">{draft.description}</p>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500 dark:text-gray-400">Tags</span>
                    <div className="flex flex-wrap gap-1.5 mt-1">
                      {draft.tags.map((tag) => (
                        <span
                          key={tag}
                          className={`text-xs font-medium px-2 py-0.5 rounded-full ${getTagColor(tag)}`}
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  {draft.config.some((e) => e.key.trim()) && (
                    <div>
                      <span className="text-xs text-gray-500 dark:text-gray-400">Configuration</span>
                      <div className="mt-1 bg-gray-50 dark:bg-gray-800/50 rounded-lg px-3 py-2 font-mono text-xs text-gray-700 dark:text-gray-300">
                        {draft.config
                          .filter((e) => e.key.trim())
                          .map((e) => `${e.key}: ${e.value}`)
                          .join('\n')}
                      </div>
                    </div>
                  )}
                </IOSCardContent>
              </IOSCard>
            </div>
          )}
        </motion.div>
      </AnimatePresence>

      {/* Navigation */}
      <div className="flex items-center justify-between pt-2 border-t border-gray-200 dark:border-gray-700">
        <IOSButton
          variant="text"
          size="sm"
          onClick={step === 0 ? onClose : handleBack}
        >
          <ChevronLeft className="w-4 h-4 mr-1" />
          {step === 0 ? 'Cancel' : 'Back'}
        </IOSButton>

        {step < STEPS.length - 1 ? (
          <IOSButton
            variant="primary"
            size="sm"
            onClick={handleNext}
            disabled={!canNext()}
          >
            Next
            <ChevronRight className="w-4 h-4 ml-1" />
          </IOSButton>
        ) : (
          <IOSButton
            variant="primary"
            size="sm"
            onClick={handleSubmit}
          >
            <Check className="w-4 h-4 mr-1" />
            Submit
          </IOSButton>
        )}
      </div>
    </div>
  );
}
