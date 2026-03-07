import { X, User, Clock, Tag, Play } from 'lucide-react';
import {
  IOSButton,
  IOSCard,
  IOSCardContent,
} from '../ios';
import type { SkillItem } from './SkillCard';
import SkillDiscussion from './SkillDiscussion';

// ---------------------------------------------------------------------------
// Version history mock
// ---------------------------------------------------------------------------

interface VersionEntry {
  version: string;
  date: string;
  changes: string;
}

const VERSION_HISTORY: Record<string, VersionEntry[]> = {
  '1': [
    { version: '1.0.0', date: '2026-02-15', changes: 'Initial release with logo and typography consistency checks.' },
    { version: '0.9.0', date: '2026-01-20', changes: 'Beta with basic color palette matching.' },
  ],
  '2': [
    { version: '1.0.0', date: '2026-02-28', changes: 'Initial release supporting 12 demographic segments.' },
    { version: '0.8.0', date: '2026-02-01', changes: 'Alpha with Gen-Z and Millennial targeting.' },
  ],
  '3': [
    { version: '1.0.0', date: '2026-03-01', changes: 'Initial release with weekly trend sync.' },
  ],
  '4': [
    { version: '1.0.0', date: '2026-03-02', changes: 'Initial release with WCAG 2.1 AA checks.' },
  ],
  '5': [
    { version: '1.0.0', date: '2026-03-03', changes: 'Initial release with 8 emotion dimensions.' },
  ],
  '6': [
    { version: '1.2.0', date: '2026-03-05', changes: 'Added GPU memory profiling and batch latency reporting.' },
    { version: '1.1.0', date: '2026-02-20', changes: 'Added TTFB (Time to First Byte) metric.' },
    { version: '1.0.0', date: '2026-02-10', changes: 'Initial release with inference latency benchmarking.' },
  ],
};

// ---------------------------------------------------------------------------
// Tag color (shared with SkillCard)
// ---------------------------------------------------------------------------

const TAG_COLORS: Record<string, string> = {
  brand: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
  design: 'bg-violet-100 text-violet-700 dark:bg-violet-900/40 dark:text-violet-300',
  audience: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300',
  marketing: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
  trends: 'bg-pink-100 text-pink-700 dark:bg-pink-900/40 dark:text-pink-300',
  culture: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300',
  quality: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/40 dark:text-cyan-300',
  accessibility: 'bg-teal-100 text-teal-700 dark:bg-teal-900/40 dark:text-teal-300',
  emotion: 'bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300',
  performance: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300',
};

function getTagColor(tag: string): string {
  return TAG_COLORS[tag] ?? 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300';
}

// ---------------------------------------------------------------------------
// SkillDetail Component
// ---------------------------------------------------------------------------

interface SkillDetailProps {
  skill: SkillItem;
  onClose?: () => void;
}

export default function SkillDetail({ skill, onClose }: SkillDetailProps) {
  const versions = VERSION_HISTORY[skill.id] ?? [
    { version: skill.version, date: '2026-03-01', changes: 'Initial release.' },
  ];

  return (
    <div className="space-y-6 py-2">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-1">
            {skill.name}
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
            {skill.description}
          </p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-4 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex-shrink-0"
            type="button"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        )}
      </div>

      {/* Meta info */}
      <div className="flex flex-wrap gap-4 text-sm text-gray-500 dark:text-gray-400">
        <div className="flex items-center gap-1.5">
          <User className="w-4 h-4" />
          <span>{skill.author}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Tag className="w-4 h-4" />
          <span>v{skill.version}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Clock className="w-4 h-4" />
          <span>{versions[0]?.date ?? 'N/A'}</span>
        </div>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-1.5">
        {skill.tags.map((tag) => (
          <span
            key={tag}
            className={`text-xs font-medium px-2.5 py-1 rounded-full ${getTagColor(tag)}`}
          >
            {tag}
          </span>
        ))}
      </div>

      {/* Use this skill */}
      <IOSButton variant="primary" size="md" onClick={() => {}}>
        <Play className="w-4 h-4 mr-1.5" />
        Use this Skill
      </IOSButton>

      {/* Version History */}
      <IOSCard variant="flat" padding="md">
        <IOSCardContent>
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-1.5">
            <Clock className="w-4 h-4" />
            Version History
          </h3>
          <div className="space-y-3">
            {versions.map((v) => (
              <div key={v.version} className="flex gap-3">
                <span className="text-xs font-mono text-gray-500 dark:text-gray-400 flex-shrink-0 w-14 pt-0.5">
                  v{v.version}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                    {v.changes}
                  </p>
                  <p className="text-[11px] text-gray-400 dark:text-gray-500 mt-0.5">
                    {v.date}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </IOSCardContent>
      </IOSCard>

      {/* Discussion */}
      <IOSCard variant="flat" padding="md">
        <IOSCardContent>
          <SkillDiscussion skillId={skill.id} />
        </IOSCardContent>
      </IOSCard>
    </div>
  );
}
