/**
 * ExhibitionsPage
 *
 * Main page displaying all exhibitions
 * Includes four-state design: loading, error, empty, success
 *
 * @updated 2026-01-11 - Added four-state design per manual section 2.5
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Image, ArrowRight, Calendar, CheckCircle, Globe, MessageSquare, Award, Sparkles } from 'lucide-react';
import { ALL_EXHIBITIONS } from '../../data/exhibitions';
import { EmojiIcon, IOSCard, IOSCardContent, IOSCardFooter, IOSButton } from '../../components/ios';
import { StateHandler } from '../../components/common/StateHandlers';

export function ExhibitionsPage() {
  // Simulate loading state for better UX
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exhibitions, setExhibitions] = useState(ALL_EXHIBITIONS);

  // Simulate data loading
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Simulate network delay for realistic UX
        await new Promise(resolve => setTimeout(resolve, 500));
        setExhibitions(ALL_EXHIBITIONS);
      } catch {
        setError('Failed to load exhibitions. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  // Retry handler
  const handleRetry = () => {
    setLoading(true);
    setError(null);
    setTimeout(() => {
      setExhibitions(ALL_EXHIBITIONS);
      setLoading(false);
    }, 500);
  };

  // Calculate total stats
  const totalArtworks = exhibitions.reduce((sum, e) => sum + e.artworks_count, 0);
  const totalExhibitions = exhibitions.length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
    >
      {/* Header - Repositioned as Qualitative Evidence */}
      <div className="text-center mb-8">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center gap-2 px-4 py-2 bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 rounded-full text-sm font-medium mb-4"
        >
          <Award className="w-4 h-4" />
          Qualitative Evidence Library
        </motion.div>
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring' }}
          className="inline-block mb-4"
        >
          <EmojiIcon category="content" name="frame" size="xl" />
        </motion.div>
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-3">
          Cross-Cultural Interpretation Samples
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-6">
          Explore real-world examples of AI-powered art criticism across cultural perspectives.
          See how VULCA evaluates cultural understanding through concrete interpretation samples.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4 text-sm text-gray-500 dark:text-gray-400">
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-slate-600" />
            <span>8 Cultural Perspectives</span>
          </div>
          <div className="flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-amber-600" />
            <span>Multi-Agent Dialogues</span>
          </div>
          <div className="flex items-center gap-2">
            <Award className="w-4 h-4 text-orange-500" />
            <span>RPAIT Scoring</span>
          </div>
        </div>
        <div className="mt-6">
          <Link to="/canvas">
            <IOSButton variant="primary" size="sm" className="inline-flex items-center gap-1.5">
              <Sparkles className="w-4 h-4" />
              Open Canvas
            </IOSButton>
          </Link>
        </div>
      </div>

      {/* Evidence Value Proposition */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="mb-8 bg-gradient-to-r from-amber-50 to-slate-50 dark:from-amber-900/20 dark:to-slate-900/20 rounded-2xl p-6 border border-amber-200 dark:border-amber-800"
      >
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Why Qualitative Evidence Matters
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 max-w-xl">
              Numbers tell part of the story. These exhibitions provide concrete examples of how AI models
              interpret art across cultures — evidence you can show stakeholders and include in reports.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link to="/solutions/museums">
              <IOSButton variant="secondary" size="sm">
                Museum Solutions
                <ArrowRight className="w-4 h-4 ml-1" />
              </IOSButton>
            </Link>
          </div>
        </div>
      </motion.div>

      {/* State Handler Wrapper */}
      <StateHandler
        loading={loading}
        error={error}
        isEmpty={!exhibitions || exhibitions.length < 1}
        onRetry={handleRetry}
        loadingMessage="Loading exhibitions..."
        emptyIcon={<Image className="w-8 h-8 text-gray-400" />}
        emptyTitle="No Exhibitions"
        emptyDescription="There are no exhibitions available at the moment. Check back later for new shows."
        emptyVariant="image"
      >
        {/* Exhibition Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {exhibitions.map((exhibition, index) => (
          <motion.div
            key={exhibition.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + index * 0.1 }}
          >
            <Link to={`/exhibitions/${exhibition.id}`}>
              <IOSCard
                variant="elevated"
                interactive
                animate
                className="h-full overflow-hidden"
              >
                {/* Cover Image */}
                <div className="relative h-48 overflow-hidden">
                  <img
                    src={exhibition.cover_image}
                    alt={exhibition.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      const img = e.target as HTMLImageElement;
                      img.style.display = 'none';
                      const parent = img.parentElement;
                      if (parent && !parent.querySelector('.fallback-gradient')) {
                        const fallback = document.createElement('div');
                        fallback.className = 'fallback-gradient w-full h-full absolute inset-0';
                        fallback.style.background = 'linear-gradient(135deg, #334155 0%, #C87F4A 50%, #B8923D 100%)';
                        parent.insertBefore(fallback, parent.firstChild);
                      }
                    }}
                  />
                  {/* Gradient Overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
                  {/* Status Badge */}
                  <div className="absolute top-3 right-3">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        exhibition.status === 'live'
                          ? 'bg-green-500 text-white'
                          : exhibition.status === 'upcoming'
                          ? 'bg-slate-600 text-white'
                          : 'bg-gray-500 text-white'
                      }`}
                    >
                      {exhibition.status.toUpperCase()}
                    </span>
                  </div>
                  {/* Title Overlay */}
                  <div className="absolute bottom-0 left-0 right-0 p-4">
                    <h3 className="text-xl font-bold text-white mb-1">
                      {exhibition.name}
                    </h3>
                    {exhibition.name_zh && (
                      <p className="text-sm text-white/80 italic">
                        {exhibition.name_zh}
                      </p>
                    )}
                  </div>
                </div>

                <IOSCardContent>
                  <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-4">
                    {exhibition.description}
                  </p>

                  {/* Features */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {exhibition.has_chapters && (
                      <span className="px-2 py-1 text-xs bg-slate-100 dark:bg-slate-900/30 text-slate-700 dark:text-slate-500 rounded-lg">
                        Chapters
                      </span>
                    )}
                    {exhibition.has_dialogues && (
                      <span className="px-2 py-1 text-xs bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-500 rounded-lg">
                        AI Dialogues
                      </span>
                    )}
                    {exhibition.has_rpait && (
                      <span className="px-2 py-1 text-xs bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 rounded-lg">
                        RPAIT Scores
                      </span>
                    )}
                  </div>

                  {/* Stats */}
                  <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                    <span className="flex items-center gap-1">
                      <EmojiIcon category="content" name="frame" size="xs" />
                      {exhibition.artworks_count} artworks
                    </span>
                  </div>
                </IOSCardContent>

                <IOSCardFooter>
                  <IOSButton variant="primary" className="w-full">
                    View Exhibition
                  </IOSButton>
                </IOSCardFooter>
              </IOSCard>
            </Link>
          </motion.div>
          ))}
        </div>
      </StateHandler>

      {/* Stats Section - Only show when not loading */}
      {!loading && !error && exhibitions.length > 0 && (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-2xl p-6 text-center">
          <p className="text-3xl font-bold text-slate-600">{totalArtworks}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Total Artworks</p>
        </div>
        <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-2xl p-6 text-center">
          <p className="text-3xl font-bold text-green-500">{totalExhibitions}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Exhibitions</p>
        </div>
        <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-2xl p-6 text-center">
          <p className="text-3xl font-bold text-orange-500">50+</p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Artists</p>
        </div>
        <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-2xl p-6 text-center">
          <p className="text-3xl font-bold text-amber-600">14</p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">AI Critics</p>
        </div>
      </motion.div>
      )}

      {/* Open Source CTA */}
      {!loading && !error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-12 bg-gradient-to-r from-amber-700 to-slate-700 rounded-2xl p-8 text-white"
        >
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div>
              <h3 className="text-2xl font-bold mb-2">Create Your Own Cultural Artworks</h3>
              <p className="text-amber-100">
                Use Canvas to create, critique, and evolve cultural art with 8 cultural perspectives.
              </p>
            </div>
            <Link to="/canvas">
              <IOSButton variant="secondary" size="lg" className="bg-white text-amber-700 hover:bg-amber-50">
                Open Canvas
                <ArrowRight className="w-4 h-4 ml-2" />
              </IOSButton>
            </Link>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

export default ExhibitionsPage;
