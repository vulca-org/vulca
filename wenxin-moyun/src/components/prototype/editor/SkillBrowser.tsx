/**
 * SkillBrowser — Left drawer panel (280px) for browsing marketplace skills.
 * Skills are draggable to the canvas.
 */

import { memo, useState } from 'react';
import { useSkillMarketplace, type SkillInfo } from '@/hooks/useSkillMarketplace';

interface SkillBrowserProps {
  visible: boolean;
  onClose: () => void;
}

function SkillBrowserComponent({ visible, onClose }: SkillBrowserProps) {
  const { skills, loading } = useSkillMarketplace();
  const [query, setQuery] = useState('');

  if (!visible) return null;

  const filtered = skills.filter(
    (s) =>
      !query.trim() ||
      s.name.toLowerCase().includes(query.toLowerCase()) ||
      s.display_name.toLowerCase().includes(query.toLowerCase()) ||
      s.tags.some((t) => t.toLowerCase().includes(query.toLowerCase())),
  );

  const handleDragStart = (e: React.DragEvent, skill: SkillInfo) => {
    e.dataTransfer.setData('application/vulca-skill', JSON.stringify(skill));
    e.dataTransfer.effectAllowed = 'move';
  };

  return (
    <div className="absolute left-0 top-0 bottom-0 w-[280px] bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 z-30 flex flex-col shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-xs font-semibold text-gray-800 dark:text-gray-200">
          ⚡ Skills Marketplace
        </h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-sm"
        >
          ✕
        </button>
      </div>

      {/* Search */}
      <div className="px-3 py-2 border-b border-gray-100 dark:border-gray-700">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search skills..."
          className="w-full text-xs bg-gray-50 dark:bg-gray-700 rounded-md px-2 py-1.5 outline-none text-gray-700 dark:text-gray-300 placeholder-gray-400"
        />
      </div>

      {/* Skills list */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-3 text-xs text-gray-400 text-center">Loading skills...</div>
        ) : filtered.length === 0 ? (
          <div className="p-3 text-xs text-gray-400 text-center">No skills found</div>
        ) : (
          filtered.map((skill) => (
            <div
              key={skill.name}
              draggable
              onDragStart={(e) => handleDragStart(e, skill)}
              className="px-3 py-2 border-b border-gray-100 dark:border-gray-700 cursor-grab hover:bg-[#B8923D]/5 dark:hover:bg-[#B8923D]/10 transition-colors"
            >
              <div className="flex items-center gap-1.5">
                <span className="text-sm">⚡</span>
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
                  {skill.display_name}
                </span>
              </div>
              <p className="text-[9px] text-gray-500 dark:text-gray-400 mt-0.5">
                {skill.description}
              </p>
              {skill.tags.length > 0 && (
                <div className="flex flex-wrap gap-0.5 mt-1">
                  {skill.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-[7px] px-1 py-0.5 rounded bg-[#B8923D]/10 text-[#B8923D] dark:text-[#DDA574]"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Footer hint */}
      <div className="px-3 py-1.5 border-t border-gray-200 dark:border-gray-700 text-[9px] text-gray-400">
        Drag skills to the canvas to add them
      </div>
    </div>
  );
}

export default memo(SkillBrowserComponent);
