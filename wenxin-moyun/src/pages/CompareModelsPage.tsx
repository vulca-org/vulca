/**
 * CompareModelsPage - Dynamic model comparison page
 * Route: /compare/:modelA-vs-:modelB
 *
 * SEO-friendly page for comparing two AI models across VULCA dimensions.
 * Generates structured data for search engines.
 */

import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  ArrowRight,
  Calendar,
  CheckCircle2,
  XCircle,
  Minus,
  Trophy,
  BarChart3,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import {
  IOSButton,
  IOSCard,
  IOSCardHeader,
  IOSCardContent,
} from '../components/ios';

// Sample model data - in production, this would come from API
const modelDatabase: Record<string, {
  name: string;
  organization: string;
  overallScore: number;
  dimensions: Record<string, number>;
  strengths: string[];
  weaknesses: string[];
}> = {
  'gpt-4o': {
    name: 'GPT-4o',
    organization: 'OpenAI',
    overallScore: 4.2,
    dimensions: {
      'Creativity': 4.3,
      'Technique': 4.5,
      'Emotion': 4.0,
      'Context': 4.1,
      'Innovation': 4.4,
      'Impact': 4.1,
    },
    strengths: ['Strong technical accuracy', 'Excellent multi-language support', 'Fast inference'],
    weaknesses: ['Limited cultural nuance in non-Western contexts', 'Occasional hallucinations'],
  },
  'claude-3-5-sonnet': {
    name: 'Claude 3.5 Sonnet',
    organization: 'Anthropic',
    overallScore: 4.3,
    dimensions: {
      'Creativity': 4.4,
      'Technique': 4.3,
      'Emotion': 4.5,
      'Context': 4.4,
      'Innovation': 4.2,
      'Impact': 4.0,
    },
    strengths: ['Nuanced cultural understanding', 'Strong emotional intelligence', 'Thoughtful responses'],
    weaknesses: ['Slower inference', 'Sometimes overly cautious'],
  },
  'gemini-1-5-pro': {
    name: 'Gemini 1.5 Pro',
    organization: 'Google',
    overallScore: 4.1,
    dimensions: {
      'Creativity': 4.0,
      'Technique': 4.3,
      'Emotion': 3.9,
      'Context': 4.2,
      'Innovation': 4.3,
      'Impact': 4.0,
    },
    strengths: ['Large context window', 'Strong multimodal capabilities', 'Good reasoning'],
    weaknesses: ['Less consistent cultural interpretations', 'Variable output quality'],
  },
};

// Normalize model slug to database key
function normalizeModelSlug(slug: string): string {
  return slug.toLowerCase().replace(/[^a-z0-9]/g, '-');
}

export default function CompareModelsPage() {
  const { comparison } = useParams<{ comparison: string }>();
  const [modelA, setModelA] = useState<string | null>(null);
  const [modelB, setModelB] = useState<string | null>(null);

  // Parse comparison parameter (e.g., "gpt-4o-vs-claude-3-5-sonnet")
  useEffect(() => {
    if (comparison) {
      const parts = comparison.split('-vs-');
      if (parts.length === 2) {
        setModelA(normalizeModelSlug(parts[0]));
        setModelB(normalizeModelSlug(parts[1]));
      }
    }
  }, [comparison]);

  const dataA = modelA ? modelDatabase[modelA] : null;
  const dataB = modelB ? modelDatabase[modelB] : null;

  // Generate comparison verdict
  const getVerdict = (scoreA: number, scoreB: number) => {
    const diff = scoreA - scoreB;
    if (Math.abs(diff) < 0.1) return { winner: 'tie', icon: Minus, color: 'gray' };
    if (diff > 0) return { winner: 'A', icon: CheckCircle2, color: 'green' };
    return { winner: 'B', icon: CheckCircle2, color: 'green' };
  };

  // If models not found
  if (!dataA || !dataB) {
    return (
      <div className="max-w-4xl mx-auto py-16 text-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Comparison Not Found
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mb-8">
          One or both models in this comparison are not in our database.
        </p>
        <Link to="/models">
          <IOSButton variant="primary">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Browse All Models
          </IOSButton>
        </Link>
      </div>
    );
  }

  const overallVerdict = getVerdict(dataA.overallScore, dataB.overallScore);

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="pt-8 pb-4">
        <Link to="/models" className="inline-flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-6">
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to Models
        </Link>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            {dataA.name} vs {dataB.name}
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Head-to-head comparison across VULCA's 47-dimension evaluation framework
          </p>
        </motion.div>
      </section>

      {/* Overall Score Comparison */}
      <section className="bg-gray-50 dark:bg-gray-900/50 -mx-4 px-4 py-12 rounded-2xl">
        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8 items-center">
            {/* Model A */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-center"
            >
              <div className={`inline-flex items-center justify-center w-20 h-20 rounded-2xl mb-4 ${
                overallVerdict.winner === 'A'
                  ? 'bg-green-100 dark:bg-green-900/30'
                  : 'bg-gray-100 dark:bg-gray-800'
              }`}>
                <span className="text-3xl font-bold text-gray-900 dark:text-white">
                  {dataA.overallScore.toFixed(1)}
                </span>
              </div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                {dataA.name}
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {dataA.organization}
              </p>
              {overallVerdict.winner === 'A' && (
                <span className="inline-flex items-center gap-1 mt-2 px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-medium rounded-full">
                  <Trophy className="w-3 h-3" />
                  Winner
                </span>
              )}
            </motion.div>

            {/* VS */}
            <div className="text-center">
              <div className="text-4xl font-bold text-gray-300 dark:text-gray-600">VS</div>
            </div>

            {/* Model B */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-center"
            >
              <div className={`inline-flex items-center justify-center w-20 h-20 rounded-2xl mb-4 ${
                overallVerdict.winner === 'B'
                  ? 'bg-green-100 dark:bg-green-900/30'
                  : 'bg-gray-100 dark:bg-gray-800'
              }`}>
                <span className="text-3xl font-bold text-gray-900 dark:text-white">
                  {dataB.overallScore.toFixed(1)}
                </span>
              </div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                {dataB.name}
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {dataB.organization}
              </p>
              {overallVerdict.winner === 'B' && (
                <span className="inline-flex items-center gap-1 mt-2 px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-medium rounded-full">
                  <Trophy className="w-3 h-3" />
                  Winner
                </span>
              )}
            </motion.div>
          </div>
        </div>
      </section>

      {/* Dimension Breakdown */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-slate-600" />
          6D Dimension Breakdown
        </h2>

        <div className="space-y-4">
          {Object.keys(dataA.dimensions).map((dimension) => {
            const scoreA = dataA.dimensions[dimension];
            const scoreB = dataB.dimensions[dimension];
            const verdict = getVerdict(scoreA, scoreB);

            return (
              <motion.div
                key={dimension}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="font-medium text-gray-900 dark:text-white">
                    {dimension}
                  </span>
                  {verdict.winner === 'tie' ? (
                    <span className="text-xs text-gray-500">Tie</span>
                  ) : (
                    <span className={`text-xs ${verdict.winner === 'A' ? 'text-slate-600' : 'text-[#C87F4A]'}`}>
                      {verdict.winner === 'A' ? dataA.name : dataB.name} wins
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {/* Model A bar */}
                  <div>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-600 dark:text-gray-400">{dataA.name}</span>
                      <span className="font-medium">{scoreA.toFixed(1)}</span>
                    </div>
                    <div className="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          verdict.winner === 'A' ? 'bg-slate-600' : 'bg-gray-400'
                        }`}
                        style={{ width: `${(scoreA / 5) * 100}%` }}
                      />
                    </div>
                  </div>

                  {/* Model B bar */}
                  <div>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-600 dark:text-gray-400">{dataB.name}</span>
                      <span className="font-medium">{scoreB.toFixed(1)}</span>
                    </div>
                    <div className="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          verdict.winner === 'B' ? 'bg-[#C87F4A]' : 'bg-gray-400'
                        }`}
                        style={{ width: `${(scoreB / 5) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* Strengths & Weaknesses */}
      <section className="grid md:grid-cols-2 gap-8">
        {/* Model A */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            title={dataA.name}
            subtitle={dataA.organization}
          />
          <IOSCardContent>
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-semibold text-green-600 dark:text-green-400 mb-2 flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4" />
                  Strengths
                </h4>
                <ul className="space-y-1">
                  {dataA.strengths.map((s) => (
                    <li key={s} className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
                      <span className="text-green-500 mt-1">+</span>
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-red-600 dark:text-red-400 mb-2 flex items-center gap-1">
                  <XCircle className="w-4 h-4" />
                  Weaknesses
                </h4>
                <ul className="space-y-1">
                  {dataA.weaknesses.map((w) => (
                    <li key={w} className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
                      <span className="text-red-500 mt-1">-</span>
                      {w}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </IOSCardContent>
        </IOSCard>

        {/* Model B */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            title={dataB.name}
            subtitle={dataB.organization}
          />
          <IOSCardContent>
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-semibold text-green-600 dark:text-green-400 mb-2 flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4" />
                  Strengths
                </h4>
                <ul className="space-y-1">
                  {dataB.strengths.map((s) => (
                    <li key={s} className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
                      <span className="text-green-500 mt-1">+</span>
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-red-600 dark:text-red-400 mb-2 flex items-center gap-1">
                  <XCircle className="w-4 h-4" />
                  Weaknesses
                </h4>
                <ul className="space-y-1">
                  {dataB.weaknesses.map((w) => (
                    <li key={w} className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
                      <span className="text-red-500 mt-1">-</span>
                      {w}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </IOSCardContent>
        </IOSCard>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900/50 dark:to-slate-800/50 -mx-4 px-4 py-12 rounded-2xl text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Need a Full 47D Comparison?
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-xl mx-auto">
          Get comprehensive evaluation across all 47 dimensions and 8 cultural perspectives
          with detailed evidence samples and actionable recommendations.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link to="/demo">
            <IOSButton variant="primary" size="lg" className="flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Book a Demo
            </IOSButton>
          </Link>
          <Link to="/canvas">
            <IOSButton variant="secondary" size="lg" className="flex items-center gap-2">
              Try VULCA Demo
              <ArrowRight className="w-4 h-4" />
            </IOSButton>
          </Link>
        </div>
      </section>

      {/* JSON-LD for this comparison page */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'ItemPage',
            'name': `${dataA.name} vs ${dataB.name} - VULCA Comparison`,
            'description': `Compare ${dataA.name} and ${dataB.name} across 47 evaluation dimensions. ${
              overallVerdict.winner === 'A'
                ? `${dataA.name} leads with ${dataA.overallScore.toFixed(1)} vs ${dataB.overallScore.toFixed(1)}`
                : overallVerdict.winner === 'B'
                ? `${dataB.name} leads with ${dataB.overallScore.toFixed(1)} vs ${dataA.overallScore.toFixed(1)}`
                : 'Both models score equally'
            }.`,
            'mainEntity': {
              '@type': 'CompareAction',
              'object': [
                {
                  '@type': 'SoftwareApplication',
                  'name': dataA.name,
                  'applicationCategory': 'AI Model',
                  'author': { '@type': 'Organization', 'name': dataA.organization },
                },
                {
                  '@type': 'SoftwareApplication',
                  'name': dataB.name,
                  'applicationCategory': 'AI Model',
                  'author': { '@type': 'Organization', 'name': dataB.organization },
                },
              ],
            },
          }),
        }}
      />
    </div>
  );
}
