/**
 * Node visual states — mute, bypass, collapse toggles.
 */

export interface NodeVisualState {
  muted: boolean;
  bypassed: boolean;
  collapsed: boolean;
}

export const DEFAULT_NODE_STATE: NodeVisualState = {
  muted: false,
  bypassed: false,
  collapsed: false,
};

/** CSS classes for muted nodes */
export function getMutedClasses(muted: boolean): string {
  return muted ? 'opacity-50 line-through' : '';
}

/** CSS classes for bypassed nodes */
export function getBypassedClasses(bypassed: boolean): string {
  return bypassed ? 'border-dashed !border-gray-400 dark:!border-gray-500' : '';
}
