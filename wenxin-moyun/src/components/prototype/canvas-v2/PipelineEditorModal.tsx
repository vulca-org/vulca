/**
 * Pipeline Viewer Modal — Read-only visualization of the Scout→Draft→Critic→Queen pipeline.
 * Shows real-time stage status during execution.
 * Opens from ⚙️ button in AI Collective sidebar.
 */

import { X } from 'lucide-react';
import { PipelineEditor } from '../editor';
import type { StageStatus, ReportOutput } from '../editor';

interface Props {
  open: boolean;
  onClose: () => void;
  isRunning: boolean;
  stageStatuses?: Record<string, StageStatus>;
  reportOutput?: ReportOutput;
  onStartPipeline?: (params: { template: string; nodeParams?: Record<string, Record<string, unknown>> }) => void;
}

export default function PipelineEditorModal({ open, onClose, isRunning, stageStatuses, reportOutput, onStartPipeline }: Props) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm flex items-center justify-center">
      <div className="w-full h-full bg-surface-container-lowest flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-3 bg-white shadow-ambient-sm shrink-0">
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-primary-500">visibility</span>
            <h2 className="text-sm font-bold text-on-surface">Pipeline Viewer</h2>
            <span className="text-[10px] text-outline">Scout → Draft → Critic → Queen evaluation pipeline</span>
          </div>
          <button
            onClick={onClose}
            className="min-w-[44px] min-h-[44px] rounded-full hover:bg-surface-container-high flex items-center justify-center transition-colors"
          >
            <X className="w-5 h-5 text-on-surface-variant" />
          </button>
        </div>

        {/* Viewer (read-only pipeline) */}
        <div className="flex-1 relative overflow-hidden">
          <PipelineEditor
            onRun={(params) => {
              onStartPipeline?.({ template: params.template, nodeParams: params.nodeParams });
              onClose();
            }}
            disabled={isRunning}
            stageStatuses={stageStatuses}
            reportOutput={reportOutput}
          />
        </div>
      </div>
    </div>
  );
}
