/**
 * useKeyboardShortcuts — canvas keyboard shortcut handler.
 *
 * Core shortcuts: Ctrl+Z, Ctrl+Shift+Z, Ctrl+S, Ctrl+Enter, Ctrl+A, Escape
 * ComfyUI-style: Space → node search, Delete → remove, D → duplicate, F → fit view
 * Phase 5: M → mute, B → bypass, H → collapse, Ctrl+J → frame, Shift+A → auto-arrange
 */

import { useEffect } from 'react';

interface ShortcutHandlers {
  onUndo: () => void;
  onRedo: () => void;
  onSave: () => void;
  onRun: () => void;
  onSelectAll: () => void;
  onDeselectAll: () => void;
  /** Space/Tab opens node search popup */
  onOpenNodeSearch?: () => void;
  /** Delete removes selected nodes */
  onDeleteSelected?: () => void;
  /** D duplicates selected nodes */
  onDuplicateSelected?: () => void;
  /** F fits view */
  onFitView?: () => void;
  /** M toggles mute on selected nodes */
  onMuteSelected?: () => void;
  /** B toggles bypass on selected nodes */
  onBypassSelected?: () => void;
  /** H toggles collapse on selected nodes */
  onCollapseSelected?: () => void;
  /** Ctrl+J adds frame around selection */
  onAddFrame?: () => void;
  /** Shift+A auto-arranges all nodes */
  onAutoArrange?: () => void;
  disabled?: boolean;
}

export function useKeyboardShortcuts({
  onUndo,
  onRedo,
  onSave,
  onRun,
  onSelectAll,
  onDeselectAll,
  onOpenNodeSearch,
  onDeleteSelected,
  onDuplicateSelected,
  onFitView,
  onMuteSelected,
  onBypassSelected,
  onCollapseSelected,
  onAddFrame,
  onAutoArrange,
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
      } else if (mod && e.key === 'j' && onAddFrame) {
        // Ctrl+J → add frame
        e.preventDefault();
        onAddFrame();
      } else if (e.key === 'Escape') {
        onDeselectAll();
      } else if (e.key === ' ' && !mod && onOpenNodeSearch) {
        // Space → open node search (ComfyUI-style)
        e.preventDefault();
        onOpenNodeSearch();
      } else if ((e.key === 'Delete' || e.key === 'Backspace') && !mod && onDeleteSelected) {
        onDeleteSelected();
      } else if (e.key === 'd' && !mod && onDuplicateSelected) {
        e.preventDefault();
        onDuplicateSelected();
      } else if (e.key === 'f' && !mod && onFitView) {
        e.preventDefault();
        onFitView();
      } else if (e.key === 'm' && !mod && onMuteSelected) {
        e.preventDefault();
        onMuteSelected();
      } else if (e.key === 'b' && !mod && onBypassSelected) {
        e.preventDefault();
        onBypassSelected();
      } else if (e.key === 'h' && !mod && onCollapseSelected) {
        e.preventDefault();
        onCollapseSelected();
      } else if (e.key === 'A' && e.shiftKey && !mod && onAutoArrange) {
        // Shift+A → auto-arrange
        e.preventDefault();
        onAutoArrange();
      }
    };

    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onUndo, onRedo, onSave, onRun, onSelectAll, onDeselectAll, onOpenNodeSearch, onDeleteSelected, onDuplicateSelected, onFitView, onMuteSelected, onBypassSelected, onCollapseSelected, onAddFrame, onAutoArrange, disabled]);
}
