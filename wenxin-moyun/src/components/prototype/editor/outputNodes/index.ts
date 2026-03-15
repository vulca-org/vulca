export { default as SaveNode } from './SaveNode';
export { default as GalleryPublishNode } from './GalleryPublishNode';
export { default as ExportNode } from './ExportNode';
export { default as CompareNode } from './CompareNode';

export const OUTPUT_NODE_META = {
  save: { label: 'Save', icon: '💾', description: 'Save to session' },
  galleryPublish: { label: 'Gallery', icon: '🖼️', description: 'Publish to gallery' },
  export: { label: 'Export', icon: '📤', description: 'Export image (PNG/JPG/SVG)' },
  compare: { label: 'Compare', icon: '⚖️', description: 'A/B side-by-side' },
};
