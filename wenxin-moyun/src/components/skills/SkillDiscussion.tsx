import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ThumbsUp, MessageSquare, Send } from 'lucide-react';
import { IOSButton } from '../ios';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface DiscussionComment {
  id: string;
  author: string;
  content: string;
  type: 'comment' | 'review' | 'upgrade_proposal';
  timestamp: string;
  votes: number;
}

type CommentType = DiscussionComment['type'];

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

const MOCK_COMMENTS: Record<string, DiscussionComment[]> = {
  '1': [
    { id: 'c1', author: 'alice', content: 'Works great for logo consistency checks. Would love to see support for color palette matching.', type: 'comment', timestamp: '2026-03-05T10:30:00Z', votes: 8 },
    { id: 'c2', author: 'bob', content: 'Tested on 200 images. Precision is solid but recall could improve on subtle brand deviations.', type: 'review', timestamp: '2026-03-04T14:20:00Z', votes: 12 },
    { id: 'c3', author: 'carol', content: 'Proposal: add a configurable threshold parameter for strictness levels (loose/moderate/strict).', type: 'upgrade_proposal', timestamp: '2026-03-03T09:15:00Z', votes: 15 },
  ],
  '2': [
    { id: 'c4', author: 'dave', content: 'The demographic segmentation is surprisingly accurate for Gen-Z content.', type: 'comment', timestamp: '2026-03-06T08:00:00Z', votes: 6 },
    { id: 'c5', author: 'eve', content: 'Comprehensive review: handles Western markets well but needs more training data for Asian demographics.', type: 'review', timestamp: '2026-03-05T16:45:00Z', votes: 9 },
  ],
  '3': [
    { id: 'c6', author: 'frank', content: 'Trends update weekly? Or is it static?', type: 'comment', timestamp: '2026-03-06T11:00:00Z', votes: 3 },
  ],
};

// ---------------------------------------------------------------------------
// Type badge
// ---------------------------------------------------------------------------

function TypeBadge({ type }: { type: CommentType }) {
  const config: Record<CommentType, { label: string; cls: string }> = {
    comment: { label: 'Comment', cls: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400' },
    review: { label: 'Review', cls: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300' },
    upgrade_proposal: { label: 'Upgrade Proposal', cls: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300' },
  };
  const c = config[type];
  return (
    <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full ${c.cls}`}>
      {c.label}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Relative time helper
// ---------------------------------------------------------------------------

function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

// ---------------------------------------------------------------------------
// SkillDiscussion Component
// ---------------------------------------------------------------------------

interface SkillDiscussionProps {
  skillId: string;
}

export default function SkillDiscussion({ skillId }: SkillDiscussionProps) {
  const [comments, setComments] = useState<DiscussionComment[]>(
    MOCK_COMMENTS[skillId] ?? []
  );
  const [newContent, setNewContent] = useState('');
  const [newType, setNewType] = useState<CommentType>('comment');

  const handleSubmit = () => {
    if (!newContent.trim()) return;
    const comment: DiscussionComment = {
      id: `c-${Date.now()}`,
      author: 'you',
      content: newContent.trim(),
      type: newType,
      timestamp: new Date().toISOString(),
      votes: 0,
    };
    setComments((prev) => [...prev, comment]);
    setNewContent('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
        <MessageSquare className="w-4 h-4" />
        <span>Discussion ({comments.length})</span>
      </div>

      {/* Comments list */}
      <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
        <AnimatePresence initial={false}>
          {comments.map((c) => (
            <motion.div
              key={c.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-gray-50 dark:bg-gray-800/50 rounded-xl px-4 py-3"
            >
              {/* Meta row */}
              <div className="flex flex-wrap items-center gap-2 mb-1.5">
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {c.author}
                </span>
                <TypeBadge type={c.type} />
                <span className="text-[11px] text-gray-400 dark:text-gray-500 ml-auto">
                  {relativeTime(c.timestamp)}
                </span>
              </div>

              {/* Content */}
              <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed mb-2">
                {c.content}
              </p>

              {/* Vote */}
              <button
                className="flex items-center gap-1 text-xs text-gray-400 hover:text-green-600 dark:hover:text-green-400 transition-colors"
                type="button"
              >
                <ThumbsUp className="w-3 h-3" />
                <span>{c.votes}</span>
              </button>
            </motion.div>
          ))}
        </AnimatePresence>

        {comments.length === 0 && (
          <p className="text-sm text-gray-400 dark:text-gray-500 text-center py-6">
            No comments yet. Be the first to share your thoughts.
          </p>
        )}
      </div>

      {/* Add comment form */}
      <div className="border-t border-gray-200 dark:border-gray-700 pt-4 space-y-3">
        <textarea
          rows={3}
          placeholder="Share your feedback..."
          value={newContent}
          onChange={(e) => setNewContent(e.target.value)}
          onKeyDown={handleKeyDown}
          className="w-full px-4 py-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-slate-500/40 resize-none transition"
        />

        <div className="flex items-center justify-between">
          {/* Type selector */}
          <div className="flex gap-1.5">
            {(['comment', 'review', 'upgrade_proposal'] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setNewType(t)}
                className={`text-xs px-2.5 py-1 rounded-full border transition-colors ${
                  newType === t
                    ? 'border-slate-600 bg-slate-600 text-white'
                    : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'
                }`}
              >
                {t === 'upgrade_proposal' ? 'Proposal' : t.charAt(0).toUpperCase() + t.slice(1)}
              </button>
            ))}
          </div>

          <IOSButton
            variant="primary"
            size="sm"
            onClick={handleSubmit}
            disabled={!newContent.trim()}
          >
            <Send className="w-3.5 h-3.5 mr-1.5" />
            Post
          </IOSButton>
        </div>
      </div>
    </div>
  );
}
