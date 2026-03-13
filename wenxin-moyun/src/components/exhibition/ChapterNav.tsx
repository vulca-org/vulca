/**
 * ChapterNav Component
 *
 * Navigation tabs for exhibition chapters
 */

import { IOSSegmentedControl } from '../ios';
import type { Chapter } from '../../types/exhibition';

interface ChapterNavProps {
  chapters: Chapter[];
  selectedChapterId: number | null;
  onSelectChapter: (chapterId: number | null) => void;
  showAll?: boolean;
}

export function ChapterNav({
  chapters,
  selectedChapterId,
  onSelectChapter,
  showAll = true,
}: ChapterNavProps) {
  const segments = [
    ...(showAll ? [{ id: 'all', label: 'All Works', value: 'all' }] : []),
    ...chapters.map((chapter) => ({
      id: String(chapter.id),
      label: chapter.name,
      value: String(chapter.id),
    })),
  ];

  // Find the selected index
  const selectedIndex = selectedChapterId === null
    ? 0
    : segments.findIndex(s => s.value === String(selectedChapterId));

  return (
    <div className="w-full overflow-x-auto scrollbar-hide">
      <div className="min-w-max">
        <IOSSegmentedControl
          segments={segments}
          selectedIndex={selectedIndex >= 0 ? selectedIndex : 0}
          onChange={(index, segment) => {
            const value = typeof segment === 'string' ? segment : segment.value;
            onSelectChapter(value === 'all' ? null : parseInt(String(value), 10));
          }}
        />
      </div>
    </div>
  );
}

// Simplified chapter pills for mobile
export function ChapterPills({
  chapters,
  selectedChapterId,
  onSelectChapter,
}: ChapterNavProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
      <button
        onClick={() => onSelectChapter(null)}
        className={`
          px-4 py-2.5 min-h-[44px] rounded-full text-sm font-medium whitespace-nowrap transition-all
          focus:outline-none focus:ring-2 focus:ring-slate-600 focus:ring-offset-2
          ${
            selectedChapterId === null
              ? 'bg-slate-600 text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
          }
        `}
      >
        All
      </button>
      {chapters.map((chapter) => (
        <button
          key={chapter.id}
          onClick={() => onSelectChapter(chapter.id)}
          className={`
            px-4 py-2.5 min-h-[44px] rounded-full text-sm font-medium whitespace-nowrap transition-all
            focus:outline-none focus:ring-2 focus:ring-slate-600 focus:ring-offset-2
            ${
              selectedChapterId === chapter.id
                ? 'bg-slate-600 text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }
          `}
        >
          {chapter.name.length > 20 ? chapter.name.slice(0, 20) + '...' : chapter.name}
        </button>
      ))}
    </div>
  );
}

export default ChapterNav;
