/**
 * HITL overlay — wraps ScoutEvidenceEditor, DraftSelectionPanel,
 * CriticOverridePanel inside an IOSSheet bottom sheet.
 *
 * Automatically opens when hitlWaitInfo is non-null and stage != 'queen'.
 * Queen stage is handled inline in the right column.
 */

import { IOSSheet } from '../ios';
import ScoutEvidenceEditor from './ScoutEvidenceEditor';
import DraftSelectionPanel from './DraftSelectionPanel';
import CriticOverridePanel from './CriticOverridePanel';
import type { HitlWaitInfo, DraftCandidate, ScoredCandidate } from '../../hooks/usePrototypePipeline';

type SubmitActionFn = (
  action: string,
  options?: { locked_dimensions?: string[]; rerun_dimensions?: string[]; candidate_id?: string; reason?: string },
) => void;

interface Props {
  hitlWaitInfo: HitlWaitInfo | null;
  evidence: Record<string, unknown> | null;
  candidates: DraftCandidate[];
  scoredCandidates: ScoredCandidate[];
  bestCandidateId: string | null;
  onAction: SubmitActionFn;
  onClose: () => void;
}

export default function HitlOverlay({
  hitlWaitInfo,
  evidence,
  candidates,
  scoredCandidates,
  bestCandidateId,
  onAction,
  onClose,
}: Props) {
  // Only show bottom sheet for stages with dedicated panels (scout/draft/critic).
  // Queen/decide stage is handled inline in the right column — no overlay needed.
  const visible = hitlWaitInfo != null && ['scout', 'draft', 'critic'].includes(hitlWaitInfo.stage);
  const stage = hitlWaitInfo?.stage ?? '';

  return (
    <IOSSheet
      visible={visible}
      onClose={onClose}
      height="large"
      allowDismiss={false}
    >
      <div className="py-4">
        <div className="flex items-center gap-2 mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Human Input Required
          </h2>
          <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300">
            {stage}
          </span>
        </div>

        {stage === 'scout' && (
          <ScoutEvidenceEditor evidence={evidence} onAction={onAction} />
        )}
        {stage === 'draft' && (
          <DraftSelectionPanel candidates={candidates} onAction={onAction} />
        )}
        {stage === 'critic' && (
          <CriticOverridePanel
            scoredCandidates={scoredCandidates}
            bestCandidateId={bestCandidateId}
            onAction={onAction}
          />
        )}
      </div>
    </IOSSheet>
  );
}
