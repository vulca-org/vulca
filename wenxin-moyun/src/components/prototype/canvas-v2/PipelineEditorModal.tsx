/**
 * Pipeline Editor Modal — Full-screen ReactFlow editor.
 * Opens from ⚙️ button in AI Collective sidebar.
 */

import { X } from 'lucide-react';
import { PipelineEditor, NodeParamPanel } from '../editor';
import type { StageStatus, ReportOutput, AgentNodeId } from '../editor';
import { useState } from 'react';

interface Props {
  open: boolean;
  onClose: () => void;
  isRunning: boolean;
  stageStatuses?: Record<string, StageStatus>;
  reportOutput?: ReportOutput;
  onStartPipeline?: (params: { template: string; customNodes?: string[]; customEdges?: [string, string][]; nodeParams?: Record<string, Record<string, unknown>> }) => void;
}

export default function PipelineEditorModal({ open, onClose, isRunning, stageStatuses, reportOutput, onStartPipeline }: Props) {
  const [selectedNode, setSelectedNode] = useState<AgentNodeId | null>(null);
  const [nodeParams, setNodeParams] = useState<Record<string, Record<string, unknown>>>({});

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm flex items-center justify-center">
      <div className="w-full h-full bg-surface-container-lowest flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-3 bg-white shadow-ambient-sm shrink-0">
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-primary-500">tune</span>
            <h2 className="text-sm font-bold text-on-surface">Pipeline Editor</h2>
            <span className="text-[10px] text-outline">Drag nodes to customize the pipeline topology</span>
          </div>
          <button
            onClick={onClose}
            className="w-10 h-10 rounded-full hover:bg-surface-container-high flex items-center justify-center transition-colors"
          >
            <X className="w-5 h-5 text-on-surface-variant" />
          </button>
        </div>

        {/* Editor */}
        <div className="flex-1 relative overflow-hidden">
          <PipelineEditor
            onRun={(params) => {
              const merged = { ...params, nodeParams: { ...nodeParams, ...params.nodeParams } };
              onStartPipeline?.(merged);
              onClose();
            }}
            disabled={isRunning}
            onNodeSelect={setSelectedNode}
            nodeParams={nodeParams}
            stageStatuses={stageStatuses}
            reportOutput={reportOutput}
          />
          <NodeParamPanel
            nodeId={selectedNode}
            params={nodeParams}
            onChange={(nodeId, key, value) => {
              setNodeParams(prev => ({
                ...prev,
                [nodeId]: { ...prev[nodeId], [key]: value },
              }));
            }}
            onClose={() => setSelectedNode(null)}
          />
        </div>
      </div>
    </div>
  );
}
