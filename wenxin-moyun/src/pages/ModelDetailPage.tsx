import { useState } from 'react';
import { useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import RouterLink from '../components/common/RouterLink';
import { Breadcrumb } from '../components/common/Breadcrumb';
import { Loader2, Cpu, FileText, Quote, Share2, Sparkles } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { mockModels } from '../data/mockData';
import { motion } from 'framer-motion';
import { useModelDetail } from '../hooks/useModelDetail';
import { useModelBenchmark } from '../hooks/useModelBenchmark';
import { ResponseDisplay } from '../components/model/ResponseDisplay';
import {
  IOSButton,
  IOSCard,
  IOSCardHeader,
  IOSCardContent,
  IOSCardFooter,
  IOSCardGrid,
  EmojiIcon,
  StatusEmoji,
  RankEmoji,
  TypeEmoji
} from '../components/ios';
import { CiteModal } from '../components/trustlayer';

export default function ModelDetailPage() {
  const { id } = useParams();
  const { model, artworks, loading, error } = useModelDetail(id);
  const { benchmarkData } = useModelBenchmark(id);
  const [showCiteModal, setShowCiteModal] = useState(false);

  if (loading) {
    return (
      <IOSCard variant="elevated" className="min-h-[400px] flex items-center justify-center">
        <IOSCardContent>
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="w-8 h-8 animate-spin text-slate-600" />
            <span className="text-gray-600 dark:text-gray-400">Loading model details...</span>
          </div>
        </IOSCardContent>
      </IOSCard>
    );
  }

  if (error || !model) {
    return (
      <IOSCard variant="elevated" className="text-center py-20">
        <IOSCardContent>
          <div className="flex flex-col items-center gap-4">
            <EmojiIcon category="feedback" name="error" size="lg" />
            <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200">Model Not Found</h2>
            <RouterLink to="/models">
              <IOSButton variant="primary">
                <EmojiIcon category="actions" name="back" size="sm" />
                Back to Models
              </IOSButton>
            </RouterLink>
          </div>
        </IOSCardContent>
      </IOSCard>
    );
  }

  // Prepare radar chart data
  const radarData = [
    { subject: 'Rhythm & Meter', value: model.metrics.rhythm, fullMark: 100 },
    { subject: 'Composition', value: model.metrics.composition, fullMark: 100 },
    { subject: 'Narrative', value: model.metrics.narrative, fullMark: 100 },
    { subject: 'Emotion', value: model.metrics.emotion, fullMark: 100 },
    { subject: 'Creativity', value: model.metrics.creativity, fullMark: 100 },
    { subject: 'Cultural', value: model.metrics.cultural, fullMark: 100 },
  ];

  return (
    <div className="max-w-7xl mx-auto">
      {/* Breadcrumb Navigation */}
      <div className="mb-6">
        <Breadcrumb
          items={[
            { label: 'Models', href: '/models', icon: <Cpu className="w-4 h-4" /> },
            { label: model.name }
          ]}
        />
      </div>

      {/* Model Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <IOSCard variant="elevated" padding="lg" className="mb-8">
        <IOSCardHeader
          title={model.name}
          subtitle={`${model.organization} · ${model.version}`}
          emoji={<TypeEmoji type={model.category === 'text' ? 'poem' : model.category === 'visual' ? 'painting' : 'music'} size="lg" />}
          action={
            <div className="text-right">
              <div className="text-4xl font-bold text-slate-700 dark:text-slate-500">
                {model.overallScore}
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Overall Score</p>
            </div>
          }
        />
        <IOSCardContent className="space-y-6">

          <p className="text-gray-700 dark:text-gray-300">
            {model.description}
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
              <EmojiIcon category="actions" name="calendar" size="sm" className="mr-2" />
              Release Date: {model.releaseDate}
            </div>
            <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
              <EmojiIcon category="content" name="category" size="sm" className="mr-2" />
              Type: {model.category === 'text' ? 'Text' : model.category === 'visual' ? 'Visual' : 'Multimodal'}
            </div>
          </div>

          {/* VULCA Report CTA */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-slate-50 to-amber-50 dark:from-slate-900/20 dark:to-amber-900/20 border border-slate-200 dark:border-slate-800">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800">
                  <FileText className="w-5 h-5 text-slate-700 dark:text-slate-500" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 dark:text-white">
                    VULCA Evaluation Report
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    L1-L5 analysis across 9 cultural traditions
                  </p>
                </div>
              </div>
              <div className="flex gap-2 flex-shrink-0">
                <RouterLink to="/canvas">
                  <IOSButton variant="secondary" size="sm">
                    <Sparkles className="w-4 h-4 mr-1.5" />
                    Open Canvas
                  </IOSButton>
                </RouterLink>
                <IOSButton variant="secondary" size="sm" onClick={() => setShowCiteModal(true)}>
                  <Quote className="w-4 h-4 mr-1.5" />
                  Cite
                </IOSButton>
                <IOSButton
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    if (navigator.share) {
                      navigator.share({
                        title: `VULCA Evaluation: ${model.name}`,
                        text: `Check out ${model.name}'s VULCA cultural AI evaluation results`,
                        url: window.location.href,
                      });
                    } else {
                      navigator.clipboard.writeText(window.location.href);
                      toast.success('Link copied to clipboard!');
                    }
                  }}
                >
                  <Share2 className="w-4 h-4 mr-1.5" />
                  Share
                </IOSButton>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {model.tags.map((tag) => (
              <IOSButton
                key={tag}
                variant="secondary"
                size="sm"
                className="text-xs"
              >
                <EmojiIcon category="content" name="tag" size="xs" className="mr-1" />
                {tag}
              </IOSButton>
            ))}
          </div>
        </IOSCardContent>
        </IOSCard>
      </motion.div>

      <IOSCardGrid columns={2} gap="lg">
        {/* Radar Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <IOSCard variant="elevated" padding="lg">
            <IOSCardHeader
              title="Capability Radar Chart"
              emoji={<EmojiIcon category="rating" name="star" size="md" />}
            />
            <IOSCardContent>
              <ResponsiveContainer width="100%" height={400}>
                <RadarChart data={radarData}>
                  <defs>
                    <linearGradient id="radarGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#64748B" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#64748B" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <PolarGrid 
                    stroke="#E5E5EA" 
                    strokeWidth={1}
                    className="dark:stroke-gray-600"
                  />
                  <PolarAngleAxis
                    dataKey="subject"
                    tick={{ 
                      fill: '#8E8E93', 
                      fontSize: 12,
                      fontWeight: 500
                    }}
                    className="text-gray-600 dark:text-gray-400"
                  />
                  <PolarRadiusAxis
                    angle={90}
                    domain={[0, 100]}
                    tick={{ 
                      fill: '#8E8E93',
                      fontSize: 10
                    }}
                    className="text-gray-500 dark:text-gray-400"
                  />
                  <Radar
                    name={model.name}
                    dataKey="value"
                    stroke="#64748B"
                    fill="url(#radarGradient)"
                    fillOpacity={0.4}
                    strokeWidth={3}
                    dot={{
                      fill: '#64748B',
                      strokeWidth: 2,
                      r: 4
                    }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </IOSCardContent>
          </IOSCard>
        </motion.div>

        {/* Metrics Details */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <IOSCard variant="elevated" padding="lg">
            <IOSCardHeader
              title="Detailed Scores"
              emoji={<EmojiIcon category="rating" name="chart" size="md" />}
            />
            <IOSCardContent>
              <div className="space-y-6">
                {radarData.map((item, index) => {
                  const getScoreColor = (score: number) => {
                    if (score >= 90) return 'from-[#5F8A50] to-[#4A7040]';
                    if (score >= 80) return 'from-slate-600 to-slate-700';
                    if (score >= 70) return 'from-[#B8923D] to-[#8F7030]';
                    return 'from-[#C65D4D] to-[#A04A3D]';
                  };
                  
                  const getScoreEmoji = (score: number) => {
                    if (score >= 90) return <RankEmoji rank={1} size="sm" />;
                    if (score >= 80) return <RankEmoji rank={2} size="sm" />;
                    if (score >= 70) return <RankEmoji rank={3} size="sm" />;
                    return <StatusEmoji status="pending" size="sm" />;
                  };
                  
                  return (
                    <div key={item.subject} className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {getScoreEmoji(item.value)}
                          <span className="font-medium text-gray-700 dark:text-gray-300">
                            {item.subject}
                          </span>
                        </div>
                        <span className="font-bold text-lg text-gray-800 dark:text-gray-200">
                          {item.value}
                        </span>
                      </div>
                      <div className="relative">
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${item.value}%` }}
                            transition={{ 
                              duration: 1.2, 
                              delay: 0.3 + index * 0.1,
                              ease: 'easeOut'
                            }}
                            className={`h-full rounded-full bg-gradient-to-r ${getScoreColor(item.value)} shadow-sm`}
                          />
                        </div>
                        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-white/20 to-transparent pointer-events-none" />
                      </div>
                    </div>
                  );
                })}
              </div>
            </IOSCardContent>
          </IOSCard>
        </motion.div>
      </IOSCardGrid>

      {/* Strengths & Weaknesses */}
      {((model.scoreHighlights && model.scoreHighlights.length > 0) || 
        (model.scoreWeaknesses && model.scoreWeaknesses.length > 0)) && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="mt-8"
        >
          <IOSCardGrid columns={2} gap="lg">
            {/* Highlights */}
            {model.scoreHighlights && model.scoreHighlights.length > 0 && (
              <IOSCard variant="elevated" padding="lg">
                <IOSCardHeader
                  title="Strengths & Highlights"
                  emoji={<EmojiIcon category="rating" name="star" size="md" />}
                />
                <IOSCardContent>
                  <div className="relative overflow-hidden rounded-xl p-4 bg-gradient-to-br from-[#5F8A50]/5 to-[#5F8A50]/5 dark:from-[#5F8A50]/10 dark:to-[#5F8A50]/10 backdrop-blur-sm border border-[#5F8A50]/20 dark:border-[#5F8A50]/20">
                    <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/10 to-transparent"></div>
                    <div className="relative space-y-3">
                      {model.scoreHighlights.map((highlight, idx) => (
                        <div key={idx} className="flex items-start">
                          <span className="text-[#5F8A50] mr-3 mt-0.5">✦</span>
                          <span className="text-sm text-[#4A7040] dark:text-[#87A878] leading-relaxed">
                            {highlight}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </IOSCardContent>
              </IOSCard>
            )}

            {/* Weaknesses */}
            {model.scoreWeaknesses && model.scoreWeaknesses.length > 0 && (
              <IOSCard variant="elevated" padding="lg">
                <IOSCardHeader
                  title="Areas for Improvement"
                  emoji={<EmojiIcon category="feedback" name="error" size="md" />}
                />
                <IOSCardContent>
                  <div className="relative overflow-hidden rounded-xl p-4 bg-gradient-to-br from-[#B8923D]/5 to-[#B8923D]/5 dark:from-[#B8923D]/10 dark:to-[#B8923D]/10 backdrop-blur-sm border border-[#B8923D]/20 dark:border-[#B8923D]/20">
                    <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/10 to-transparent"></div>
                    <div className="relative space-y-3">
                      {model.scoreWeaknesses.map((weakness, idx) => (
                        <div key={idx} className="flex items-start">
                          <span className="text-[#B8923D] mr-3 mt-0.5">◈</span>
                          <span className="text-sm text-[#8F7030] dark:text-[#D4A94E] leading-relaxed">
                            {weakness}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </IOSCardContent>
              </IOSCard>
            )}
          </IOSCardGrid>
        </motion.div>
      )}

      {/* Sample Works */}
      {artworks.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-8"
        >
          <IOSCard variant="elevated" padding="lg">
            <IOSCardHeader
              title="Representative Works"
              emoji={<EmojiIcon category="content" name="portfolio" size="md" />}
            />
            <IOSCardContent>
              <IOSCardGrid columns={2} gap="md">
                {artworks.map((work) => (
                  <IOSCard key={work.id} variant="flat" interactive>
                    <IOSCardHeader
                      title={work.title}
                      subtitle={work.type === 'poem' ? 'Poetry' : work.type === 'painting' ? 'Painting' : 'Story'}
                      emoji={<TypeEmoji type={work.type} size="md" />}
                      action={
                        <div className="flex items-center">
                          <RankEmoji rank={work.score >= 95 ? 1 : work.score >= 90 ? 2 : 3} size="sm" />
                          <span className="ml-1 font-semibold text-gray-700 dark:text-gray-300">
                            {work.score}
                          </span>
                        </div>
                      }
                    />
                    <IOSCardContent className="space-y-4">
                      {work.prompt && (
                        <div className="p-3 ios-glass rounded-lg">
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            <strong>Prompt: </strong>{work.prompt}
                          </p>
                        </div>
                      )}
                      <div className="prose prose-sm dark:prose-invert max-w-none">
                        <pre className="whitespace-pre-wrap font-sans text-gray-700 dark:text-gray-300 text-sm leading-relaxed">
                          {work.content}
                        </pre>
                      </div>
                    </IOSCardContent>
                    <IOSCardFooter>
                      <div className="flex items-center justify-between w-full">
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {work.createdAt}
                        </span>
                        <IOSButton variant="text" size="sm">
                          <EmojiIcon category="actions" name="expand" size="xs" />
                          View Full
                        </IOSButton>
                      </div>
                    </IOSCardFooter>
                  </IOSCard>
                ))}
              </IOSCardGrid>
            </IOSCardContent>
          </IOSCard>
        </motion.div>
      )}

      {/* Similar Models */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="mt-8"
      >
        <IOSCard variant="elevated" padding="lg">
          <IOSCardHeader
            title="Similar Models"
            emoji={<EmojiIcon category="content" name="compare" size="md" />}
          />
          <IOSCardContent>
            <IOSCardGrid columns={3} gap="md">
              {mockModels
                .filter(m => m.id !== model.id && m.category === model.category)
                .slice(0, 3)
                .map((similarModel) => (
                  <RouterLink key={similarModel.id} to={`/model/${similarModel.id}`}>
                    <IOSCard variant="flat" interactive animate className="h-full">
                      <IOSCardContent className="p-4">
                        <div className="flex items-center space-x-3">
                          <img
                            src={similarModel.avatar}
                            alt={similarModel.name}
                            className="w-12 h-12 rounded-lg object-cover"
                          />
                          <div className="flex-1">
                            <h4 className="font-semibold text-gray-800 dark:text-gray-200 text-sm">
                              {similarModel.name}
                            </h4>
                            <div className="flex items-center gap-1 mt-1">
                              <RankEmoji 
                                rank={similarModel.overallScore != null && similarModel.overallScore >= 90 ? 1 : similarModel.overallScore != null && similarModel.overallScore >= 80 ? 2 : 3} 
                                size="xs" 
                              />
                              <p className="text-sm text-gray-500 dark:text-gray-400">
                                {similarModel.overallScore != null ? similarModel.overallScore : 'N/A'}
                              </p>
                            </div>
                          </div>
                        </div>
                      </IOSCardContent>
                    </IOSCard>
                  </RouterLink>
                ))}
            </IOSCardGrid>
          </IOSCardContent>
        </IOSCard>
      </motion.div>

      {/* Benchmark Test Results with Full Responses */}
      {benchmarkData && benchmarkData.detailed_scores && benchmarkData.detailed_scores.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-8"
        >
          <IOSCard variant="elevated" padding="lg">
            <IOSCardHeader
              title="Benchmark Test Results"
              subtitle={`${benchmarkData.test_count} tests completed • ${benchmarkData.success_count} successful`}
              emoji={<EmojiIcon category="rating" name="trophy" size="md" />}
            />
            <IOSCardContent>
              {/* Display tabs for each dimension */}
              <div className="space-y-8">
                {['rhythm', 'composition', 'narrative', 'emotion', 'creativity', 'cultural'].map((dimension) => {
                  const dimensionResponses = benchmarkData.detailed_scores.filter(
                    (r) => r.dimension === dimension
                  );

                  if (dimensionResponses.length === 0) return null;

                  return (
                    <div key={dimension} className="border-t pt-6 first:border-t-0 first:pt-0">
                      <ResponseDisplay
                        responses={dimensionResponses}
                        dimension={dimension}
                      />
                    </div>
                  );
                })}
              </div>
            </IOSCardContent>
          </IOSCard>
        </motion.div>
      )}

      {/* Citation Modal */}
      <CiteModal
        citation={{
          key: `vulca_${model.id}_${new Date().getFullYear()}`,
          title: `VULCA Evaluation Report: ${model.name} Cultural AI Assessment`,
          authors: ['VULCA Team'],
          booktitle: 'VULCA AI-Native Creation Organism',
          year: 2025,
          doi: '10.18653/v1/2025.findings-emnlp.103',
          url: `https://vulcaart.art/model/${model.id}`,
        }}
        visible={showCiteModal}
        onClose={() => setShowCiteModal(false)}
      />
    </div>
  );
}
