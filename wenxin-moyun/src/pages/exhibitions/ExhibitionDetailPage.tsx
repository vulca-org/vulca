/**
 * ExhibitionDetailPage
 *
 * Displays exhibition details with artwork grid and chapter navigation
 */

import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useExhibitions } from '../../hooks/exhibitions';
import { ArtworkCard, ChapterPills } from '../../components/exhibition';
import { IOSButton, EmojiIcon } from '../../components/ios';

export function ExhibitionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { exhibition, chapters, filteredArtworks, filters, setFilters, loading, error } =
    useExhibitions(id);

  const [searchQuery, setSearchQuery] = useState('');

  // Handle search
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setFilters({ ...filters, search: query });
  };

  // Handle chapter selection
  const handleChapterSelect = (chapterId: number | null) => {
    setFilters({ ...filters, chapter: chapterId ?? undefined });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-slate-600 border-t-transparent rounded-full mx-auto" />
          <p className="mt-4 text-gray-500 dark:text-gray-400">Loading exhibition...</p>
        </div>
      </div>
    );
  }

  if (error || !exhibition) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <EmojiIcon category="status" name="warning" size="xl" className="mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Exhibition Not Found
          </h2>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            {error || 'The exhibition you are looking for does not exist.'}
          </p>
          <Link to="/exhibitions">
            <IOSButton variant="primary">Back to Exhibitions</IOSButton>
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
      className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
    >
      {/* Back Button */}
      <Link to="/exhibitions" className="inline-flex items-center gap-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 mb-6">
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back to Exhibitions
      </Link>

      {/* Hero Section */}
      <div className="relative rounded-3xl overflow-hidden mb-8">
        <div className="aspect-[21/9] relative">
          <img
            src={exhibition.cover_image}
            alt={exhibition.name}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
        </div>
        <div className="absolute bottom-0 left-0 right-0 p-8">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">
            {exhibition.name}
          </h1>
          <p className="text-xl text-white/80 mb-4">{exhibition.name_zh}</p>
          <p className="text-white/70 max-w-2xl">{exhibition.description}</p>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="mb-6 space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <input
            type="text"
            aria-label="Search artworks"
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Search artworks, artists, mediums..."
            className="w-full px-4 py-3 pl-12 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-slate-600"
          />
          <svg
            className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          {searchQuery && (
            <button
              onClick={() => handleSearch('')}
              className="absolute right-2 top-1/2 -translate-y-1/2 w-11 h-11 flex items-center justify-center text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
              aria-label="Clear search"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Chapter Pills */}
        <ChapterPills
          chapters={chapters}
          selectedChapterId={filters.chapter ?? null}
          onSelectChapter={handleChapterSelect}
        />
      </div>

      {/* Results Count */}
      <div className="flex items-center justify-between mb-6">
        <p className="text-gray-500 dark:text-gray-400">
          {filteredArtworks.length} artwork{filteredArtworks.length !== 1 ? 's' : ''}
          {filters.chapter && (
            <span>
              {' '}
              in{' '}
              <span className="text-gray-700 dark:text-gray-300">
                {chapters.find((c) => c.id === filters.chapter)?.name}
              </span>
            </span>
          )}
        </p>
      </div>

      {/* Artwork Grid */}
      {filteredArtworks.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {filteredArtworks.map((artwork, index) => (
            <motion.div
              key={artwork.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: Math.min(index * 0.05, 0.5) }}
            >
              <ArtworkCard artwork={artwork} exhibitionId={id || 'echoes-and-returns'} />
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <EmojiIcon category="actions" name="search" size="xl" className="mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            No artworks found
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            Try adjusting your search or filters
          </p>
          <IOSButton
            variant="secondary"
            className="mt-4"
            onClick={() => {
              setSearchQuery('');
              setFilters({});
            }}
          >
            Clear Filters
          </IOSButton>
        </div>
      )}
    </motion.div>
  );
}

export default ExhibitionDetailPage;
