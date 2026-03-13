/**
 * ArtworkPage
 *
 * Displays single artwork details with image gallery and AI dialogue
 */

import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useExhibitions } from '../../hooks/exhibitions';
import { ArtworkDetail, DialogueViewer, ArtworkCard, CritiqueViewer } from '../../components/exhibition';
import { IOSButton, EmojiIcon } from '../../components/ios';

export function ArtworkPage() {
  const { id: exhibitionId, artworkId } = useParams<{ id: string; artworkId: string }>();
  const {
    artworks,
    getArtworkById,
    getDialogueByArtworkId,
    loading: artworkLoading,
    error: artworkError,
    exhibition
  } = useExhibitions(exhibitionId);

  // Get artwork and dialogue from the exhibition
  const artwork = getArtworkById(artworkId || '');
  const dialogue = getDialogueByArtworkId(artworkId || '');

  // Get dialogues - prefer from artwork, fallback to direct hook result
  const dialogues = artwork?.dialogues?.length ? artwork.dialogues : (dialogue ? [dialogue] : []);

  // Get critiques and personas for RPAIT display (Negative Space exhibition)
  const critiques = artwork?.critiques || [];
  const personas = exhibition?.personas || [];

  // Get related artworks (same chapter, excluding current, or random for flat exhibitions)
  const relatedArtworks = artwork?.chapter
    ? artworks
        .filter(
          (a) =>
            a.chapter?.id === artwork.chapter?.id && a.id !== artwork.id
        )
        .slice(0, 4)
    : artworks.filter((a) => a.id !== artwork?.id).slice(0, 4);

  // Navigate to next/prev artwork
  const currentIndex = artworks.findIndex((a) => a.id === artwork?.id);
  const prevArtwork = currentIndex > 0 ? artworks[currentIndex - 1] : null;
  const nextArtwork = currentIndex < artworks.length - 1 ? artworks[currentIndex + 1] : null;

  if (artworkLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-slate-600 border-t-transparent rounded-full mx-auto" />
          <p className="mt-4 text-gray-500 dark:text-gray-400">Loading artwork...</p>
        </div>
      </div>
    );
  }

  if (artworkError || !artwork) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <EmojiIcon category="status" name="warning" size="xl" className="mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Artwork Not Found
          </h2>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            {artworkError || 'The artwork you are looking for does not exist.'}
          </p>
          <Link to={`/exhibitions/${exhibitionId}`}>
            <IOSButton variant="primary">Back to Exhibition</IOSButton>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
    >
      {/* Back Button */}
      <Link
        to={`/exhibitions/${exhibitionId}`}
        className="inline-flex items-center gap-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 mb-6"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back to Exhibition
      </Link>

      {/* Artwork Detail */}
      <ArtworkDetail artwork={artwork} />

      {/* AI Dialogue Section */}
      {dialogues.length > 0 && (
        <div className="mt-8">
          <DialogueViewer dialogues={dialogues} artworkTitle={artwork.title} />
        </div>
      )}

      {/* RPAIT Critiques Section (Negative Space of the Tide) */}
      {critiques.length > 0 && personas.length > 0 && (
        <div className="mt-8">
          <CritiqueViewer
            critiques={critiques}
            personas={personas}
            artworkTitle={artwork.title}
          />
        </div>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
        {prevArtwork ? (
          <Link
            to={`/exhibitions/${exhibitionId}/${prevArtwork.id}`}
            className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-slate-600"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <div className="text-left">
              <p className="text-xs text-gray-400">Previous</p>
              <p className="text-sm font-medium line-clamp-1">{prevArtwork.title}</p>
            </div>
          </Link>
        ) : (
          <div />
        )}

        {nextArtwork ? (
          <Link
            to={`/exhibitions/${exhibitionId}/${nextArtwork.id}`}
            className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-slate-600"
          >
            <div className="text-right">
              <p className="text-xs text-gray-400">Next</p>
              <p className="text-sm font-medium line-clamp-1">{nextArtwork.title}</p>
            </div>
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        ) : (
          <div />
        )}
      </div>

      {/* Related Artworks */}
      {relatedArtworks.length > 0 && (
        <div className="mt-12">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            {artwork.chapter ? `More from ${artwork.chapter.name}` : 'More Artworks'}
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {relatedArtworks.map((related) => (
              <ArtworkCard
                key={related.id}
                artwork={related}
                exhibitionId={exhibitionId || 'echoes-and-returns'}
              />
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}

export default ArtworkPage;
