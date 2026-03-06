/**
 * useKeyboardShortcuts — canvas keyboard shortcut handler.
 * Registers Ctrl/Cmd shortcuts for undo, redo, save, run, select-all, deselect.
 */

import { useEffect } from 'react';

interface ShortcutHandlers {
  onUndo: () => void;
  onRedo: () => void;
  onSave: () => void;
  onRun: () => void;
  onSelectAll: () => void;
  onDeselectAll: () => void;
  disabled?: boolean;
}

export function useKeyboardShortcuts({
  onUndo,
  onRedo,
  onSave,
  onRun,
  onSelectAll,
  onDeselectAll,
  disabled,
}: ShortcutHandlers) {
  useEffect(() => {
    if (disabled) return;

    const handler = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
      if ((e.target as HTMLElement)?.isContentEditable) return;

      const mod = e.metaKey || e.ctrlKey;

      if (mod && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        onUndo();
      } else if (mod && (e.key === 'Z' || (e.key === 'z' && e.shiftKey))) {
        e.preventDefault();
        onRedo();
      } else if (mod && e.key === 's') {
        e.preventDefault();
        onSave();
      } else if (mod && e.key === 'Enter') {
        e.preventDefault();
        onRun();
      } else if (mod && e.key === 'a') {
        e.preventDefault();
        onSelectAll();
      } else if (e.key === 'Escape') {
        onDeselectAll();
      }
    };

    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onUndo, onRedo, onSave, onRun, onSelectAll, onDeselectAll, disabled]);
}
