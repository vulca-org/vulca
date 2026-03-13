/**
 * ExhibitionCard Component
 *
 * Displays a single exhibition in a card format using iOS design system
 */

import { Link } from 'react-router-dom';
import type { Exhibition } from '../../types/exhibition';
import { IOSCard, IOSCardHeader, IOSCardContent, IOSCardFooter, IOSButton, EmojiIcon } from '../ios';

interface ExhibitionCardProps {
  exhibition: Exhibition;
}

export function ExhibitionCard({ exhibition }: ExhibitionCardProps) {
  const statusColors = {
    live: 'bg-green-500',
    upcoming: 'bg-orange-500',
    archived: 'bg-gray-400',
  };

  const statusLabels = {
    live: 'Now Showing',
    upcoming: 'Coming Soon',
    archived: 'Past Exhibition',
  };

  return (
    <IOSCard variant="elevated" interactive animate className="overflow-hidden">
      {/* Cover Image */}
      <div className="relative aspect-[16/9] overflow-hidden">
        <img
          src={exhibition.cover_image}
          alt={exhibition.name}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        {/* Status Badge */}
        <div className="absolute top-3 right-3">
          <span
            className={`${statusColors[exhibition.status]} text-white text-xs font-medium px-2.5 py-1 rounded-full backdrop-blur-sm`}
          >
            {statusLabels[exhibition.status]}
          </span>
        </div>
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent" />
      </div>

      <IOSCardHeader
        title={exhibition.name}
        subtitle={exhibition.name_zh}
        emoji={<EmojiIcon category="content" name="frame" size="lg" />}
      />

      <IOSCardContent>
        <p className="text-gray-600 dark:text-gray-400 text-sm line-clamp-2">
          {exhibition.description}
        </p>

        {/* Stats */}
        <div className="flex items-center gap-4 mt-3 text-sm text-gray-500 dark:text-gray-400">
          <span className="flex items-center gap-1">
            <EmojiIcon category="content" name="artwork" size="sm" />
            {exhibition.artworks_count} Artworks
          </span>
          {exhibition.chapters && exhibition.chapters.length > 0 && (
            <span className="flex items-center gap-1">
              <EmojiIcon category="content" name="folder" size="sm" />
              {exhibition.chapters.length} Chapters
            </span>
          )}
        </div>
      </IOSCardContent>

      <IOSCardFooter>
        <Link to={`/exhibitions/${exhibition.id}`} className="w-full">
          <IOSButton variant="primary" className="w-full" glassMorphism>
            View Exhibition
          </IOSButton>
        </Link>
      </IOSCardFooter>
    </IOSCard>
  );
}

export default ExhibitionCard;
