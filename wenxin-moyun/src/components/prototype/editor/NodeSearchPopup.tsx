/**
 * NodeSearchPopup — ComfyUI-style floating search for adding nodes.
 *
 * Phase 5: Extended with Input, Processing, Flow Control, Output categories.
 * Opened by pressing Space in the pipeline editor.
 */

import { useState, useEffect, useRef, useMemo } from 'react';
import { ALL_AGENT_IDS, AGENT_META, type AgentNodeId } from './types';
import { INPUT_NODE_META } from './inputNodes';
import { OUTPUT_NODE_META } from './outputNodes';

interface SearchItem {
  id: string;
  label: string;
  icon: string;
  description: string;
  category: string;
}

// Nodes with actual backend support (ONE PIPELINE: vulca/ engine)
const BACKEND_SUPPORTED_AGENTS = new Set(['draft', 'critic', 'queen']);
const BACKEND_SUPPORTED_INPUTS = new Set(['textPrompt']);
const BACKEND_SUPPORTED_OUTPUTS = new Set(['save']);

/** Build the searchable items list — only nodes with backend support */
function buildSearchItems(): SearchItem[] {
  const items: SearchItem[] = [];

  // Agent nodes (only backend-connected)
  for (const id of ALL_AGENT_IDS) {
    if (!BACKEND_SUPPORTED_AGENTS.has(id)) continue;
    const meta = AGENT_META[id];
    items.push({ id, label: meta.label, icon: meta.icon, description: meta.description, category: 'Agents' });
  }

  // Input nodes (only textPrompt has backend support)
  for (const [id, meta] of Object.entries(INPUT_NODE_META)) {
    if (!BACKEND_SUPPORTED_INPUTS.has(id)) continue;
    items.push({ id, label: meta.label, icon: meta.icon, description: meta.description, category: 'Inputs' });
  }

  // Output nodes (only save)
  for (const [id, meta] of Object.entries(OUTPUT_NODE_META)) {
    if (!BACKEND_SUPPORTED_OUTPUTS.has(id)) continue;
    items.push({ id, label: meta.label, icon: meta.icon, description: meta.description, category: 'Output' });
  }

  // Utility nodes (pure UI, always available)
  items.push({ id: 'frame', label: 'Frame', icon: '🔲', description: 'Group container', category: 'Utility' });
  items.push({ id: 'reroute', label: 'Reroute', icon: '◆', description: 'Edge junction', category: 'Utility' });
  items.push({ id: 'sticky', label: 'Sticky Note', icon: '📝', description: 'Annotate your pipeline', category: 'Utility' });

  return items;
}

const ALL_ITEMS = buildSearchItems();

interface Props {
  visible: boolean;
  onClose: () => void;
  onAddNode: (nodeId: AgentNodeId | string) => void;
  /** Screen position to render at (near cursor or center) */
  position?: { x: number; y: number };
}

export default function NodeSearchPopup({ visible, onClose, onAddNode, position }: Props) {
  const [query, setQuery] = useState('');
  const [highlightIndex, setHighlightIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus input when opened
  useEffect(() => {
    if (visible) {
      setQuery('');
      setHighlightIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [visible]);

  // All hooks must be called before any early return (React rules)
  const { filtered, categories, flatIndexMap } = useMemo(() => {
    const f = ALL_ITEMS.filter(item => {
      if (!query.trim()) return true;
      const q = query.toLowerCase();
      return (
        item.id.toLowerCase().includes(q) ||
        item.label.toLowerCase().includes(q) ||
        item.description.toLowerCase().includes(q) ||
        item.category.toLowerCase().includes(q)
      );
    });

    const cats = new Map<string, SearchItem[]>();
    for (const item of f) {
      const cat = item.category;
      if (!cats.has(cat)) cats.set(cat, []);
      cats.get(cat)!.push(item);
    }

    const idxMap = new Map<string, number>();
    let idx = 0;
    for (const [, items] of cats.entries()) {
      for (const item of items) {
        idxMap.set(item.id, idx++);
      }
    }

    return { filtered: f, categories: cats, flatIndexMap: idxMap };
  }, [query]);

  if (!visible) return null;

  const handleSelect = (id: string) => {
    onAddNode(id as AgentNodeId);
    onClose();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightIndex(i => Math.min(i + 1, filtered.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightIndex(i => Math.max(i - 1, 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filtered[highlightIndex]) {
        handleSelect(filtered[highlightIndex].id);
      }
    }
  };

  const posStyle = position
    ? { left: Math.min(position.x, window.innerWidth - 280), top: Math.min(position.y, window.innerHeight - 400) }
    : { left: '50%', top: '30%', transform: 'translate(-50%, -50%)' };

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 z-40" onClick={onClose} />

      {/* Popup */}
      <div
        className="fixed z-50 w-64 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden"
        style={posStyle}
      >
        {/* Search input */}
        <div className="px-2 py-1.5 border-b border-gray-200 dark:border-gray-700">
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => {
              setQuery(e.target.value);
              setHighlightIndex(0);
            }}
            onKeyDown={handleKeyDown}
            placeholder="Search nodes..."
            className="w-full text-xs bg-transparent outline-none text-gray-800 dark:text-gray-200 placeholder-gray-400"
          />
        </div>

        {/* Results grouped by category */}
        <ul className="max-h-64 overflow-y-auto py-1">
          {filtered.length === 0 && (
            <li className="px-3 py-2 text-[11px] text-gray-400">No matching nodes</li>
          )}
          {Array.from(categories.entries()).map(([category, items]) => (
            <li key={category}>
              {/* Category header */}
              <div className="px-3 py-1 text-[9px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider bg-gray-50 dark:bg-gray-750">
                {category}
              </div>
              {items.map((item) => {
                const idx = flatIndexMap.get(item.id) ?? 0;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleSelect(item.id)}
                    onMouseEnter={() => setHighlightIndex(idx)}
                    className={[
                      'w-full flex items-center gap-2 px-3 py-1.5 text-left transition-colors',
                      idx === highlightIndex
                        ? 'bg-[#C87F4A]/10 dark:bg-[#C87F4A]/20'
                        : 'hover:bg-gray-50 dark:hover:bg-gray-700',
                    ].join(' ')}
                  >
                    <span className="text-sm">{item.icon}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-gray-800 dark:text-gray-200">
                        {item.label}
                      </p>
                      <p className="text-[9px] text-gray-400 dark:text-gray-500 truncate">
                        {item.description}
                      </p>
                    </div>
                  </button>
                );
              })}
            </li>
          ))}
        </ul>

        {/* Shortcut hints */}
        <div className="px-3 py-1 border-t border-gray-200 dark:border-gray-700 flex items-center gap-3 text-[9px] text-gray-400">
          <span><kbd className="px-1 py-0.5 rounded bg-gray-100 dark:bg-gray-700">↑↓</kbd> navigate</span>
          <span><kbd className="px-1 py-0.5 rounded bg-gray-100 dark:bg-gray-700">↵</kbd> add</span>
          <span><kbd className="px-1 py-0.5 rounded bg-gray-100 dark:bg-gray-700">esc</kbd> close</span>
        </div>
      </div>
    </>
  );
}
