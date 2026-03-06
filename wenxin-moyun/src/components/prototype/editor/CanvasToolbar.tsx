/**
 * CanvasToolbar — compact toolbar strip above the React Flow canvas.
 *
 * Left:   Template button, Undo/Redo, Add Node/Note
 * Right:  Validation badge, Save, Run Pipeline
 *
 * Tooltips show keyboard shortcuts. ComfyUI/n8n toolbar reference.
 */

import { useState } from 'react';
import { ALL_AGENT_IDS, AGENT_META, type AgentNodeId } from './types';

interface Props {
  onToggleGallery: () => void;
  onUndo: () => void;
  onRedo: () => void;
  canUndo: boolean;
  canRedo: boolean;
  onAddNode: (nodeId: AgentNodeId) => void;
  onAddStickyNote: () => void;
  onSave: () => void;
  onRun: () => void;
  disabled: boolean;
  validation: { valid: boolean; errors: string[]; warnings: string[] } | null;
  activeTemplate: string;
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
        {activeTemplate.startsWith('custom-') ? 'Custom' : activeTemplate.replace(/_/g, ' ')}
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

      {/* Add Node dropdown */}
      <div className="relative">
        <button
          onClick={() => setShowAddMenu(!showAddMenu)}
          disabled={disabled}
          className="px-2 py-1 text-xs font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-md transition-colors disabled:opacity-50"
        >
          + Node
        </button>
        {showAddMenu && (
          <div className="absolute top-full left-0 mt-1 w-44 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-40 py-1">
            {ALL_AGENT_IDS.map((id) => (
              <button
                key={id}
                onClick={() => {
                  onAddNode(id);
                  setShowAddMenu(false);
                }}
                className="w-full px-3 py-1.5 text-left text-xs hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
              >
                <span>{AGENT_META[id].icon}</span>
                <span className="text-gray-800 dark:text-gray-200">{AGENT_META[id].label}</span>
                <span className="text-[10px] text-gray-400 ml-auto">
                  {AGENT_META[id].description}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Add Sticky Note */}
      <IconBtn onClick={onAddStickyNote} disabled={disabled} title="Add sticky note">
        📝
      </IconBtn>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Validation badge */}
      {validation && (
        <span
          className={[
            'text-xs px-2 py-0.5 rounded-full font-medium',
            validation.valid
              ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
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
        className="px-3 py-1 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 dark:disabled:bg-gray-600 rounded-lg transition-colors"
        title="Run Pipeline (Ctrl+Enter)"
      >
        ▶ Run
      </button>
    </div>
  );
}
