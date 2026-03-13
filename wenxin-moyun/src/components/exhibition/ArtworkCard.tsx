/**
 * ArtworkCard Component
 *
 * Displays a single artwork in a card format
 */

import { Link } from 'react-router-dom';
import type { Artwork } from '../../types/exhibition';
import { IOSCard, IOSCardContent } from '../ios';

interface ArtworkCardProps {
  artwork: Artwork;
  exhibitionId: string;
}

const PLACEHOLDER_COLORS = [
  'from-slate-600 to-slate-800',
  'from-amber-700 to-amber-900',
  'from-emerald-700 to-emerald-900',
  'from-[#334155] to-slate-800',
  'from-rose-700 to-rose-900',
  'from-cyan-700 to-cyan-900',
];

export function ArtworkCard({ artwork, exhibitionId }: ArtworkCardProps) {
  // Handle both string and ArtworkImage types
  const firstImage = artwork.images?.[0];
  const thumbnail = typeof firstImage === 'string'
    ? firstImage
    : firstImage?.url || artwork.image_url || '';
  const hasImage = !!thumbnail;

  // Stable color based on artwork id
  const colorIndex = typeof artwork.id === 'number' ? artwork.id : String(artwork.id).length;
  const placeholderGradient = PLACEHOLDER_COLORS[colorIndex % PLACEHOLDER_COLORS.length];

  return (
    <Link to={`/exhibitions/${exhibitionId}/${artwork.id}`}>
      <IOSCard variant="elevated" interactive animate className="overflow-hidden group">
        {/* Thumbnail */}
        <div className="relative aspect-square overflow-hidden">
          {hasImage ? (
          <img
            src={thumbnail}
            alt={artwork.title}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            loading="lazy"
          />
          ) : (
          <div className={`w-full h-full bg-gradient-to-br ${placeholderGradient} flex flex-col items-center justify-center p-4 text-center transition-transform duration-500 group-hover:scale-105`}>
            <div className="text-white/30 text-5xl mb-3">
              <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
              </svg>
            </div>
            <p className="text-white/80 text-xs font-medium line-clamp-2">{artwork.title}</p>
            <p className="text-white/50 text-xs mt-1">{artwork.artist?.fullName}</p>
          </div>
          )}
          {/* Video indicator */}
          {artwork.video_url && (
            <div className="absolute bottom-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded-full flex items-center gap-1">
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
              </svg>
              Video
            </div>
          )}
        </div>

        <IOSCardContent className="p-3">
          {/* Title */}
          <h3 className="font-semibold text-gray-900 dark:text-white text-sm line-clamp-1">
            {artwork.title}
          </h3>

          {/* Artist */}
          <p className="text-gray-500 dark:text-gray-400 text-xs mt-1">
            {artwork.artist.fullName}
          </p>

          {/* Medium */}
          <p className="text-gray-500 dark:text-gray-400 text-xs mt-0.5 line-clamp-1">
            {artwork.medium}
          </p>
        </IOSCardContent>
      </IOSCard>
    </Link>
  );
}

export default ArtworkCard;
