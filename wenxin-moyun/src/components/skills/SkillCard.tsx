import { motion } from 'framer-motion';
import { ThumbsUp, ThumbsDown, User } from 'lucide-react';
import {
  IOSCard,
  IOSCardContent,
  IOSCardFooter,
} from '../ios';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface SkillItem {
  id: string;
  name: string;
  description: string;
  tags: string[];
  author: string;
  version: string;
  upvotes: number;
  downvotes: number;
}

// ---------------------------------------------------------------------------
// Tag color helper
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
// SkillCard Component
// ---------------------------------------------------------------------------

interface SkillCardProps {
  skill: SkillItem;
  onClick: () => void;
}

export default function SkillCard({ skill, onClick }: SkillCardProps) {
  return (
    <IOSCard variant="elevated" padding="none" interactive onClick={onClick}>
      <IOSCardContent className="px-5 pt-5 pb-3">
        {/* Header: name + version */}
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-base font-semibold text-gray-900 dark:text-white leading-tight">
            {skill.name}
          </h3>
          <span className="ml-2 flex-shrink-0 text-[11px] font-mono px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400">
            v{skill.version}
          </span>
        </div>

        {/* Description */}
        <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed mb-3 line-clamp-2">
          {skill.description}
        </p>

        {/* Tags */}
        <div className="flex flex-wrap gap-1.5 mb-3">
          {skill.tags.map((tag) => (
            <span
              key={tag}
              className={`text-xs font-medium px-2 py-0.5 rounded-full ${getTagColor(tag)}`}
            >
              {tag}
            </span>
          ))}
        </div>
      </IOSCardContent>

      <IOSCardFooter className="px-5 pb-4 flex items-center justify-between">
        {/* Author */}
        <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
          <User className="w-3.5 h-3.5" />
          <span>{skill.author}</span>
        </div>

        {/* Votes */}
        <div className="flex items-center gap-3">
          <motion.button
            className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 hover:text-green-600 dark:hover:text-green-400 transition-colors"
            whileTap={{ scale: 0.9 }}
            onClick={(e) => e.stopPropagation()}
            type="button"
          >
            <ThumbsUp className="w-3.5 h-3.5" />
            <span>{skill.upvotes}</span>
          </motion.button>

          <motion.button
            className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors"
            whileTap={{ scale: 0.9 }}
            onClick={(e) => e.stopPropagation()}
            type="button"
          >
            <ThumbsDown className="w-3.5 h-3.5" />
            <span>{skill.downvotes}</span>
          </motion.button>
        </div>
      </IOSCardFooter>
    </IOSCard>
  );
}
