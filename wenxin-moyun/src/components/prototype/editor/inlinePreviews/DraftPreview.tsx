/**
 * DraftPreview — 2x2 thumbnail grid for draft candidate images.
 * Shows up to 4 candidate thumbnails (48x48px each).
 */

import { memo } from 'react';

interface DraftPreviewProps {
  candidates: { image_url?: string; candidate_id?: string }[];
}

function DraftPreviewComponent({ candidates }: DraftPreviewProps) {
  const shown = candidates.slice(0, 4);
  if (shown.length === 0) return null;

  return (
    <div className="grid grid-cols-2 gap-1 mt-1.5">
      {shown.map((c, i) => (
        <div
          key={c.candidate_id || i}
          className="w-12 h-12 rounded-md overflow-hidden bg-gray-100 dark:bg-gray-700"
        >
          {c.image_url ? (
            <img
              src={c.image_url}
              alt={`Candidate ${i + 1}`}
              className="w-full h-full object-cover"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-[10px] text-gray-400">
              {i + 1}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default memo(DraftPreviewComponent);
