import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Toaster, toast } from 'react-hot-toast';
import { useAutoAnimate } from '@formkit/auto-animate/react';
import { categories, mockModels } from '../data/mockData';
import { useLeaderboard } from '../hooks/useLeaderboard';
import LeaderboardCard from '../components/leaderboard/LeaderboardCard';
import LeaderboardTable from '../components/leaderboard/LeaderboardTable';
import AdvancedFilterPanel from '../components/filters/AdvancedFilterPanel';
import ViewModeToggle from '../components/leaderboard/ViewModeToggle';
import { useUIStore } from '../store/uiStore';
import { useFilterStore } from '../store/filterStore';
import type { LeaderboardEntry } from '../types/types';
import type { FilterState } from '../store/filterStore';
import { IOSButton, IOSCard, IOSCardHeader, IOSCardContent } from '../components/ios';
import {
  Trophy, ScrollText, Palette, BookOpen, Music, RefreshCw, Search,
  TrendingUp, Quote, Copy, Check, Calendar, ArrowRight, FileText, ExternalLink
} from 'lucide-react';
import { LoadingOverlay } from '../components/common/LoadingOverlay';
import { CiteModal } from '../components/trustlayer';
import type { Citation } from '../utils/trustedExport';
import { VULCA_VERSION, VERSION_BADGE } from '../config/version';

// Category icons mapping
const categoryIcons: Record<string, React.ReactNode> = {
  overall: <Trophy className="w-5 h-5" />,
  poetry: <ScrollText className="w-5 h-5" />,
  painting: <Palette className="w-5 h-5" />,
  narrative: <BookOpen className="w-5 h-5" />,
  music: <Music className="w-5 h-5" />,
  multimodal: <RefreshCw className="w-5 h-5" />,
};

type FilterPanelValues = Omit<FilterState, 'search'>;

export default function LeaderboardPage() {
  const { category = 'overall' } = useParams();
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState(category);
  const { entries, loading, error } = useLeaderboard(selectedCategory === 'overall' ? undefined : selectedCategory);
  const [, setHoveredEntry] = useState<LeaderboardEntry | null>(null);
  const [expandedVulcaModels, setExpandedVulcaModels] = useState<Set<string>>(new Set());
  const [listRef] = useAutoAnimate();
  
  const { viewMode } = useUIStore();
  const { 
    filterEntries, 
    setFilters,
    organizations: selectedOrgs,
    tags: selectedTags,
    categories: selectedCategories,
    scoreRange,
    winRateRange,
    dateRange,
    weights,
    clearFilters
  } = useFilterStore();

  // Get unique values for filter options
  const organizations = useMemo(() => {
    const orgs = new Set<string>();
    mockModels.forEach(model => orgs.add(model.organization));
    return Array.from(orgs);
  }, []);
  
  const tags = useMemo(() => {
    const allTags = new Set<string>();
    mockModels.forEach(model => {
      model.tags.forEach(tag => allTags.add(tag));
    });
    return Array.from(allTags);
  }, []);
  
  const categoryNames = useMemo(() => {
    return categories.filter(cat => cat.id !== 'overall').map(cat => cat.name);
  }, []);
  
  // Apply filters
  const filteredData = useMemo(() => {
    return filterEntries(entries);
  }, [entries, filterEntries]);
  
  useEffect(() => {
    if (error) {
      toast.error('Failed to load data, please try again later');
    }
  }, [error]);

  const handleFilterChange = (values: FilterPanelValues) => {
    setFilters({
      organizations: values.organizations,
      tags: values.tags,
      categories: values.categories,
      scoreRange: values.scoreRange,
      winRateRange: values.winRateRange,
      dateRange: values.dateRange,
      weights: values.weights
    });
  };

  // 处理VULCA展开/收起
  const toggleVulcaExpansion = (modelId: string) => {
    setExpandedVulcaModels(prev => {
      const newSet = new Set(prev);
      if (newSet.has(modelId)) {
        newSet.delete(modelId);
      } else {
        newSet.add(modelId);
      }
      return newSet;
    });
  };

  return (
    <div className="max-w-7xl mx-auto">
      <Toaster position="top-right" />
      
      {/* Header */}
      <div className="mb-8">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-bold text-gray-800 dark:text-gray-200 mb-4"
        >
          AI Art Creation Leaderboard
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-gray-600 dark:text-gray-400"
        >
          Comprehensive ranking of AI models' artistic creation capabilities based on multi-dimensional evaluation
        </motion.p>
      </div>
      
      {/* Controls Bar */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div className="flex items-center gap-3">
          <AdvancedFilterPanel 
            config={{
              organizations,
              tags,
              categories: categoryNames
            }}
            values={{
              organizations: selectedOrgs,
              tags: selectedTags,
              categories: selectedCategories,
              scoreRange,
              winRateRange,
              dateRange,
              weights
            }}
            onChange={handleFilterChange}
            onReset={clearFilters}
          />
          <ViewModeToggle />
        </div>
        <div className="text-sm text-gray-500 dark:text-gray-400">
          Showing {filteredData.length} / {entries.length} models
        </div>
      </div>

      {/* Category Tabs */}
      <div className="mb-8 overflow-x-auto scrollbar-hide">
        <div className="flex space-x-2 min-w-max">
          {categories.map((cat) => (
            <IOSButton
              key={cat.id}
              variant={selectedCategory === cat.id ? 'primary' : 'secondary'}
              size="md"
              onClick={() => setSelectedCategory(cat.id)}
              className="flex items-center gap-2"
            >
              {categoryIcons[cat.id]}
              <span>{cat.name}</span>
            </IOSButton>
          ))}
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <LoadingOverlay message="Loading leaderboard data..." size="md" />
      )}

      {/* Error State */}
      {error && (
        <div role="alert" aria-live="assertive" className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-4 rounded-lg mb-4 border border-red-200 dark:border-red-800">
          {error}
        </div>
      )}

      {/* Leaderboard Display */}
      {!loading && !error && (
        <div ref={listRef}>
          {viewMode === 'table' ? (
            <LeaderboardTable 
              data={filteredData}
              loading={loading}
              onRowClick={(entry) => navigate(`/model/${entry.model.id}`)}
              expandedVulcaModels={expandedVulcaModels}
              onToggleVulca={toggleVulcaExpansion}
            />
          ) : viewMode === 'card' || viewMode === 'detailed' ? (
            <div className={`
              grid gap-6
              ${viewMode === 'card' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1 lg:grid-cols-2'}
            `}>
              {filteredData.map((entry, index) => (
                <LeaderboardCard
                  key={entry.model.id}
                  entry={entry}
                  index={index}
                  viewMode={viewMode}
                  onHover={setHoveredEntry}
                />
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {filteredData.map((entry, index) => (
                <LeaderboardCard
                  key={entry.model.id}
                  entry={entry}
                  index={index}
                  viewMode="compact"
                  onHover={setHoveredEntry}
                />
              ))}
            </div>
          )}
        </div>
      )}
      
      {/* Empty State - Enhanced UI */}
      {!loading && !error && filteredData.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-16"
        >
          <div className="bg-gray-50 dark:bg-gray-900/50 rounded-2xl p-8 max-w-md mx-auto">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-200 dark:bg-gray-800 flex items-center justify-center">
              <Search className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
              No Models Found
            </h3>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              No models match your current filter criteria. Try adjusting your filters or reset to see all models.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <IOSButton
                variant="primary"
                onClick={clearFilters}
              >
                Reset All Filters
              </IOSButton>
              <IOSButton
                variant="secondary"
                onClick={() => setSelectedCategory('overall')}
              >
                View All Categories
              </IOSButton>
            </div>
          </div>
        </motion.div>
      )}

      {/* Stats Summary */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="ios-glass liquid-glass-container rounded-lg p-6 text-center">
          <div className="text-3xl font-bold text-slate-700 dark:text-slate-300">
            {filteredData.length}
          </div>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Evaluated Models</p>
        </div>
        <div className="ios-glass liquid-glass-container rounded-lg p-6 text-center">
          <div className="text-3xl font-bold text-cultural-bronze-600 dark:text-cultural-bronze-400">
            {filteredData[0]?.score != null ? filteredData[0].score.toFixed(3) : 0}
          </div>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Highest Score</p>
        </div>
        <div className="ios-glass liquid-glass-container rounded-lg p-6 text-center">
          <div className="text-3xl font-bold text-[#5F8A50] dark:text-[#87A878]">
            {filteredData.length > 0 && filteredData.some(e => e.score != null)
              ? (filteredData.filter(e => e.score != null).reduce((acc, e) => acc + (e.score || 0), 0) / filteredData.filter(e => e.score != null).length).toFixed(3)
              : 'N/A'}
          </div>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Average Score</p>
        </div>
      </div>

      {/* Top-Δ Dimensions Analysis */}
      {filteredData.length >= 2 && (
        <TopDeltaSection topModels={filteredData.slice(0, 3)} />
      )}

      {/* Citation & Export Section */}
      <CitationSection
        category={selectedCategory}
        modelCount={filteredData.length}
      />

      {/* Open Source CTA */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="mt-12 bg-gradient-to-br from-[#334155] to-[#C87F4A] rounded-2xl p-8 text-white"
      >
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div>
            <h3 className="text-2xl font-bold mb-2">Try Full L1-L5 Evaluation</h3>
            <p className="text-slate-100">
              Run comprehensive cultural evaluation with L1-L5 dimensions across 13 cultural traditions in Canvas.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row gap-3">
            <Link to="/canvas">
              <IOSButton variant="secondary" size="lg">
                Open Canvas
                <ArrowRight className="w-4 h-4 ml-2" />
              </IOSButton>
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

// Top-Δ Dimensions Component
function TopDeltaSection({ topModels }: { topModels: LeaderboardEntry[] }) {
  if (topModels.length < 2) return null;

  // Calculate dimension differences between top 2 models
  const model1 = topModels[0];
  const model2 = topModels[1];

  // Mock dimension data for demonstration
  const dimensionDeltas = [
    { name: 'Cultural Context', model1Score: 0.92, model2Score: 0.78, delta: 0.14 },
    { name: 'Emotional Depth', model1Score: 0.88, model2Score: 0.75, delta: 0.13 },
    { name: 'Historical Awareness', model1Score: 0.85, model2Score: 0.73, delta: 0.12 },
    { name: 'Symbolic Interpretation', model1Score: 0.90, model2Score: 0.79, delta: 0.11 },
    { name: 'Cross-Cultural Synthesis', model1Score: 0.87, model2Score: 0.77, delta: 0.10 },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="mt-8"
    >
      <IOSCard variant="elevated">
        <IOSCardHeader
          emoji={<TrendingUp className="w-6 h-6 text-slate-600" />}
          title="Top-Δ Dimensions"
          subtitle={`Largest performance gaps between ${model1.model.name} and ${model2.model.name}`}
        />
        <IOSCardContent>
          <div className="space-y-4">
            {dimensionDeltas.map((dim, index) => (
              <div key={dim.name} className="flex items-center gap-4">
                <span className="w-6 h-6 rounded-full bg-slate-100 dark:bg-slate-900/30 flex items-center justify-center text-xs font-bold text-slate-700 dark:text-slate-500">
                  {index + 1}
                </span>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-900 dark:text-white">{dim.name}</span>
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-[#5F8A50] dark:text-[#87A878] font-medium">{dim.model1Score.toFixed(2)}</span>
                      <span className="text-gray-400">vs</span>
                      <span className="text-gray-600 dark:text-gray-400">{dim.model2Score.toFixed(2)}</span>
                      <span className="ml-2 px-2 py-0.5 bg-[#5F8A50]/10 dark:bg-[#5F8A50]/15 text-[#4A7040] dark:text-[#87A878] rounded text-xs font-medium">
                        +{(dim.delta * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full flex">
                      <div
                        className="bg-slate-600 transition-all duration-500"
                        style={{ width: `${dim.model1Score * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              These dimensions show the most significant performance differences. Use this data to identify
              specific areas where models excel or need improvement.
            </p>
            <Link to="/canvas" className="inline-flex items-center gap-1 mt-2 text-sm text-slate-700 dark:text-slate-500 hover:underline">
              Explore full evaluation
              <ExternalLink className="w-3 h-3" />
            </Link>
          </div>
        </IOSCardContent>
      </IOSCard>
    </motion.div>
  );
}

// Citation Section Component
function CitationSection({
  category,
  modelCount
}: {
  category: string;
  modelCount: number;
}) {
  const [copied, setCopied] = useState(false);
  const [showCiteModal, setShowCiteModal] = useState(false);

  const bibtexCitation = `@misc{vulca_leaderboard_${category}_2025,
  title={VULCA Leaderboard: ${category.charAt(0).toUpperCase() + category.slice(1)} Category},
  author={VULCA Team},
  year={2025},
  howpublished={\\url{https://vulcaart.art/models}},
  note={Version ${VERSION_BADGE.short}, ${modelCount} models evaluated, accessed ${VULCA_VERSION.lastUpdated}}
}`;

  const leaderboardCitation: Citation = {
    key: `vulca_leaderboard_${category}_2025`,
    title: `VULCA Leaderboard: ${category.charAt(0).toUpperCase() + category.slice(1)} Category Evaluation Results`,
    authors: ['VULCA Team'],
    booktitle: 'VULCA AI-Native Creation Organism',
    year: 2025,
    doi: '10.18653/v1/2025.findings-emnlp.103',
    url: `https://vulcaart.art/models/${category}`,
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(bibtexCitation);
    setCopied(true);
    toast.success('Citation copied to clipboard');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.25 }}
      className="mt-8"
    >
      <IOSCard variant="flat">
        <IOSCardHeader
          emoji={<Quote className="w-6 h-6 text-amber-600" />}
          title="Cite This Result"
          subtitle="Use this citation for academic publications"
        />
        <IOSCardContent>
          <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 font-mono text-xs text-gray-700 dark:text-gray-300 overflow-x-auto">
            <pre className="whitespace-pre-wrap">{bibtexCitation}</pre>
          </div>
          <div className="flex flex-wrap items-center gap-4 mt-4">
            <IOSButton
              variant="primary"
              size="sm"
              onClick={() => setShowCiteModal(true)}
            >
              <Quote className="w-4 h-4 mr-1" />
              All Citation Formats
            </IOSButton>
            <IOSButton
              variant="secondary"
              size="sm"
              onClick={handleCopy}
            >
              {copied ? <Check className="w-4 h-4 mr-1" /> : <Copy className="w-4 h-4 mr-1" />}
              {copied ? 'Copied!' : 'Copy BibTeX'}
            </IOSButton>
            <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <FileText className="w-4 h-4" />
              <span>Version: <span className="font-medium text-gray-700 dark:text-gray-300">{VERSION_BADGE.short}</span></span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <Calendar className="w-4 h-4" />
              <span>Evaluated: <span className="font-medium text-gray-700 dark:text-gray-300">{VULCA_VERSION.lastUpdated}</span></span>
            </div>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">
            For reproducibility, please include the version number and evaluation date in your citations.
            Full methodology available in our{' '}
            <Link to="/research" className="text-slate-700 dark:text-slate-500 hover:underline">documentation</Link>.
          </p>
        </IOSCardContent>
      </IOSCard>

      {/* Citation Modal */}
      <CiteModal
        citation={leaderboardCitation}
        visible={showCiteModal}
        onClose={() => setShowCiteModal(false)}
      />
    </motion.div>
  );
}
