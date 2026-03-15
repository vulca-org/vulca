export { default as SketchUploadNode } from './SketchUploadNode';
export { default as ReferenceImageNode } from './ReferenceImageNode';
export { default as MaskRegionNode } from './MaskRegionNode';
export { default as TextPromptNode } from './TextPromptNode';
export { default as ScriptNode } from './ScriptNode';
export { default as ModelImportNode } from './ModelImportNode';
export { default as AudioImportNode } from './AudioImportNode';

export const INPUT_NODE_META = {
  sketch: { label: 'Sketch', icon: '✏️', description: 'Upload sketch/line art' },
  reference: { label: 'Reference Image', icon: '🖼️', description: 'Reference image input' },
  mask: { label: 'Mask Region', icon: '🎭', description: 'Draw mask/region' },
  textPrompt: { label: 'Text Prompt', icon: '📝', description: 'Text/prompt input' },
  script: { label: 'Storyboard', icon: '📜', description: 'Storyboard text' },
  modelImport: { label: '3D Model', icon: '🧊', description: '3D model input (Coming Soon)' },
  audioImport: { label: 'Audio', icon: '🎵', description: 'Audio input (Coming Soon)' },
};
