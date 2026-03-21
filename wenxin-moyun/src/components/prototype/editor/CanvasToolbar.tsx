/**
 * CanvasToolbar — compact toolbar strip above the React Flow canvas.
 *
 * Left:   Template button, Undo/Redo, Add Node/Note, Frame, Reroute, Skills
 * Right:  Auto-arrange, Validation badge, Save, Run Pipeline
 *
 * Phase 5: Added Frame, Reroute, Auto-arrange, Skills buttons.
 */

import { useState } from 'react';
import { ALL_AGENT_IDS, AGENT_META, type AgentNodeId } from './types';
import { INPUT_NODE_META } from './inputNodes';
import { OUTPUT_NODE_META } from './outputNodes';

const BACKEND_SUPPORTED_AGENTS = new Set(['draft', 'critic', 'queen']);
const BACKEND_SUPPORTED_INPUTS = new Set(['textPrompt']);
const BACKEND_SUPPORTED_OUTPUTS = new Set(['save']);

interface Props {
  onToggleGallery: () => void;
  onUndo: () => void;
  onRedo: () => void;
  canUndo: boolean;
  canRedo: boolean;
  onAddNode: (nodeId: AgentNodeId | string) => void;
  onAddStickyNote: () => void;
  onSave: () => void;
  onRun: () => void;
  disabled: boolean;
  validation: { valid: boolean; errors: string[]; warnings: string[] } | null;
  activeTemplate: string;
  /** Phase 5 */
  onAddFrame?: () => void;
  onAddReroute?: () => void;
  onAutoArrange?: () => void;
  onToggleSkills?: () => void;
}

function IconBtn({
  onClick,
  disabled,
  title,
  children,
  className = '',
}: {
  onClick: () => void;
  disabled?: boolean;
  title: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={[
        'p-1.5 rounded-md text-sm transition-colors',
        disabled
          ? 'text-gray-300 dark:text-gray-600 cursor-not-allowed'
          : 'text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700',
        className,
      ].join(' ')}
    >
      {children}
    </button>
  );
}

function Separator() {
  return <div className="w-px h-5 bg-gray-300 dark:bg-gray-600 mx-1" />;
}

export default function CanvasToolbar({
  onToggleGallery,
  onUndo,
  onRedo,
  canUndo,
  canRedo,
  onAddNode,
  onAddStickyNote,
  onSave,
  onRun,
  disabled,
  validation,
  activeTemplate,
  onAddFrame,
  onAddReroute,
  onAutoArrange,
  onToggleSkills,
}: Props) {
  const [showAddMenu, setShowAddMenu] = useState(false);

  return (
    <div className="flex items-center gap-1 px-3 py-1.5 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 flex-shrink-0 relative">
      {/* Template button */}
      <button
        onClick={onToggleGallery}
        disabled={disabled}
        className="px-2 py-1 text-xs font-medium border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
      >
        {activeTemplate.startsWith('custom-') ? 'Custom' : activeTemplate.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
        <span className="ml-1 text-gray-400">▾</span>
      </button>

      <Separator />

      {/* Undo / Redo */}
      <IconBtn onClick={onUndo} disabled={disabled || !canUndo} title="Undo (Ctrl+Z)">
        ↩
      </IconBtn>
      <IconBtn onClick={onRedo} disabled={disabled || !canRedo} title="Redo (Ctrl+Shift+Z)">
        ↪
      </IconBtn>

      <Separator />

      {/* Add Node dropdown — now with categories */}
      <div className="relative">
        <button
          onClick={() => setShowAddMenu(!showAddMenu)}
          disabled={disabled}
          className="px-2 py-1 text-xs font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-md transition-colors disabled:opacity-50"
        >
          + Node <span className="text-[9px] text-gray-400 ml-0.5">Space</span>
        </button>
        {showAddMenu && (
          <div className="absolute top-full left-0 mt-1 w-52 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-40 py-1 max-h-80 overflow-y-auto">
            {/* Agents — backend-supported only */}
            <div className="px-3 py-1 text-[9px] font-semibold text-gray-400 uppercase tracking-wider">Agents</div>
            {ALL_AGENT_IDS.filter((id) => BACKEND_SUPPORTED_AGENTS.has(id)).map((id) => (
              <button
                key={id}
                onClick={() => { onAddNode(id); setShowAddMenu(false); }}
                className="w-full px-3 py-1.5 text-left text-xs hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
              >
                <span>{AGENT_META[id].icon}</span>
                <span className="text-gray-800 dark:text-gray-200">{AGENT_META[id].label}</span>
              </button>
            ))}

            {/* Inputs — backend-supported only */}
            <div className="px-3 py-1 text-[9px] font-semibold text-gray-400 uppercase tracking-wider mt-1">Inputs</div>
            {Object.entries(INPUT_NODE_META).filter(([id]) => BACKEND_SUPPORTED_INPUTS.has(id)).map(([id, meta]) => (
              <button
                key={id}
                onClick={() => { onAddNode(id); setShowAddMenu(false); }}
                className="w-full px-3 py-1.5 text-left text-xs hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
              >
                <span>{meta.icon}</span>
                <span className="text-gray-800 dark:text-gray-200">{meta.label}</span>
              </button>
            ))}

            {/* Output — backend-supported only */}
            <div className="px-3 py-1 text-[9px] font-semibold text-gray-400 uppercase tracking-wider mt-1">Output</div>
            {Object.entries(OUTPUT_NODE_META).filter(([id]) => BACKEND_SUPPORTED_OUTPUTS.has(id)).map(([id, meta]) => (
              <button
                key={id}
                onClick={() => { onAddNode(id); setShowAddMenu(false); }}
                className="w-full px-3 py-1.5 text-left text-xs hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
              >
                <span>{meta.icon}</span>
                <span className="text-gray-800 dark:text-gray-200">{meta.label}</span>
              </button>
            ))}

            {/* Utility — pure UI nodes, always available */}
            <div className="px-3 py-1 text-[9px] font-semibold text-gray-400 uppercase tracking-wider mt-1">Utility</div>
            {[
              { id: 'frame', icon: '🔲', label: 'Frame' },
              { id: 'reroute', icon: '◆', label: 'Reroute' },
              { id: 'sticky', icon: '📝', label: 'Sticky Note' },
            ].map(({ id, icon, label }) => (
              <button
                key={id}
                onClick={() => {
                  if (id === 'sticky') onAddStickyNote();
                  else if (id === 'frame') onAddFrame?.();
                  else if (id === 'reroute') onAddReroute?.();
                  setShowAddMenu(false);
                }}
                className="w-full px-3 py-1.5 text-left text-xs hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
              >
                <span>{icon}</span>
                <span className="text-gray-800 dark:text-gray-200">{label}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Add Sticky Note */}
      <IconBtn onClick={onAddStickyNote} disabled={disabled} title="Add sticky note">
        📝
      </IconBtn>

      {/* Frame + Reroute */}
      {onAddFrame && (
        <IconBtn onClick={onAddFrame} disabled={disabled} title="Add Frame (Ctrl+J)">
          🔲
        </IconBtn>
      )}
      {onAddReroute && (
        <IconBtn onClick={onAddReroute} disabled={disabled} title="Add Reroute">
          ◆
        </IconBtn>
      )}

      <Separator />

      {/* Skills browser toggle */}
      {onToggleSkills && (
        <IconBtn onClick={onToggleSkills} disabled={disabled} title="Skills Marketplace">
          ⚡
        </IconBtn>
      )}

      {/* Auto-arrange */}
      {onAutoArrange && (
        <IconBtn onClick={onAutoArrange} disabled={disabled} title="Auto-arrange (Shift+A)">
          📊
        </IconBtn>
      )}

      {/* Spacer */}
      <div className="flex-1" />

      {/* Validation badge */}
      {validation && (
        <span
          className={[
            'text-xs px-2 py-0.5 rounded-full font-medium',
            validation.valid
              ? 'bg-[#5F8A50]/10 dark:bg-[#5F8A50]/15 text-[#5F8A50] dark:text-[#87A878]'
              : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
          ].join(' ')}
          title={[...validation.errors, ...validation.warnings].join('\n')}
        >
          {validation.valid ? 'Valid' : `${validation.errors.length} error(s)`}
        </span>
      )}

      {/* Save */}
      <IconBtn onClick={onSave} disabled={disabled} title="Save template (Ctrl+S)">
        💾
      </IconBtn>

      {/* Run */}
      <button
        onClick={onRun}
        disabled={disabled || !validation?.valid}
        className="px-3 py-1 text-xs font-semibold text-white bg-[#C87F4A] hover:bg-[#A85D3B] disabled:bg-gray-400 dark:disabled:bg-gray-600 rounded-lg transition-colors"
        title="Run Pipeline (Ctrl+Enter)"
      >
        ▶ Run
      </button>
    </div>
  );
}
