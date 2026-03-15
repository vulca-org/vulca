export { default as ProcessingNodeBase } from './ProcessingNodeBase';
export { default as StyleTransferNode } from './StyleTransferNode';
export { default as ColorHarmonyNode } from './ColorHarmonyNode';
export { default as CompositionBalanceNode } from './CompositionBalanceNode';
export { default as UpscaleNode } from './UpscaleNode';
export { default as DepthMapNode } from './DepthMapNode';
export { default as EdgeDetectionNode } from './EdgeDetectionNode';
export { default as ElementExtractNode } from './ElementExtractNode';

export const PROCESSING_NODE_META = {
  styleTransfer: { label: 'Style Transfer', icon: '🎨', description: 'Apply artistic style' },
  colorHarmony: { label: 'Color Harmony', icon: '🌈', description: 'Optimize color balance' },
  compositionBalance: { label: 'Composition', icon: '📐', description: 'Balance composition' },
  upscale: { label: 'Upscale', icon: '🔍', description: 'AI upscale 2x/4x' },
  depthMap: { label: 'Depth Map', icon: '🗺️', description: 'Depth estimation' },
  edgeDetection: { label: 'Edge Detection', icon: '✂️', description: 'Detect edges' },
  elementExtract: { label: 'Element Extract', icon: '🧩', description: 'Extract elements' },
};
