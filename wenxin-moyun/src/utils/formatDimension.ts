/**
 * Shared dimension-name formatting utilities.
 *
 * - `formatDimension`  uses PROTOTYPE_DIM_LABELS for a short label with
 *   fallback to underscores-to-spaces.
 * - `formatDimensionTitleCase` converts snake_case to Title Case
 *   (no label lookup — used by AgentInsightsPanel and similar views).
 */

import { PROTOTYPE_DIM_LABELS } from '@/utils/vulca-dimensions';
import type { PrototypeDimension } from '@/utils/vulca-dimensions';

/** Return the short label from PROTOTYPE_DIM_LABELS, falling back to a
 *  space-separated version of the raw key. */
export function formatDimension(dim: string): string {
  return PROTOTYPE_DIM_LABELS[dim as PrototypeDimension]?.short || dim.replace(/_/g, ' ');
}

/** Convert a snake_case dimension key to Title Case (no label lookup). */
export function formatDimensionTitleCase(dim: string): string {
  return dim
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
}
