import { useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  ArrowRight,
  Calendar,
  Building2,
  GraduationCap,
  Palette,
  CheckCircle2,
  TrendingUp,
  FileText,
  Globe,
  Target,
  Eye
} from 'lucide-react';
import { motion } from 'framer-motion';
import {
  IOSButton,
  IOSCard,
  IOSCardHeader,
  IOSCardContent,
  IOSCardGrid,
  IOSSegmentedControl,
} from '../../components/ios';
import type { SegmentItem } from '../../components/ios';
import AILabSolutionPage from './AILabSolutionPage';
import ResearchSolutionPage from './ResearchSolutionPage';
import MuseumSolutionPage from './MuseumSolutionPage';

const TAB_KEYS = ['overview', 'ai-labs', 'research', 'museums'] as const;
type TabKey = typeof TAB_KEYS[number];

const TAB_SEGMENTS: SegmentItem[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'ai-labs', label: 'AI Labs' },
  { id: 'research', label: 'Research' },
  { id: 'museums', label: 'Museums' },
];

const solutions = [
  {
    icon: Building2,
    color: 'blue',
    title: 'AI Labs & Companies',
    subtitle: 'Model selection & release',
    description: 'Make informed decisions for model selection, fine-tuning validation, and safe public release with comprehensive cultural evaluation.',
    benefits: [
      'Pre-release cultural risk audits',
      '47D regression tracking across versions',
      'Competitive benchmarking',
      'Release decision documentation',
    ],
    tabKey: 'ai-labs' as TabKey,
    metrics: [
      { label: 'Dimensions', value: '47' },
      { label: 'Perspectives', value: '8' },
    ],
  },
  {
    icon: GraduationCap,
    color: 'purple',
    title: 'Research Institutions',
    subtitle: 'Academic benchmarking',
    description: 'Publish with confidence using reproducible, citable evaluation methodology backed by peer-reviewed research.',
    benefits: [
      'Citation-ready reports (BibTeX, APA, etc.)',
      'Version-controlled reproducibility',
      'Standardized benchmark comparisons',
      'Academic collaboration support',
    ],
    tabKey: 'research' as TabKey,
    metrics: [
      { label: 'Citation Formats', value: '7' },
      { label: 'Reproducible', value: '100%' },
    ],
  },
  {
    icon: Palette,
    color: 'orange',
    title: 'Museums & Galleries',
    subtitle: 'Cultural AI curation',
    description: 'Deploy AI for cultural interpretation with confidence in cross-cultural accuracy and interpretive quality.',
    benefits: [
      'Multi-cultural validation',
      'Interpretive AI quality assurance',
      'Cross-cultural sensitivity analysis',
      'Exhibition AI deployment support',
    ],
    tabKey: 'museums' as TabKey,
    metrics: [
      { label: 'Cultures', value: '8+' },
      { label: 'Art Critics', value: '8' },
    ],
  },
];

function SolutionsOverview() {
  const [, setSearchParams] = useSearchParams();

  const switchToTab = (tabKey: TabKey) => {
    setSearchParams({ tab: tabKey });
  };

  return (
    <>
      {/* Solutions Grid */}
      <section>
        <div className="space-y-12">
          {solutions.map((solution, index) => (
            <motion.div
              key={solution.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <IOSCard variant="elevated" className="overflow-hidden">
                <div className="md:flex">
                  {/* Left: Icon and Metrics */}
                  <div className={`md:w-1/3 p-8 bg-${solution.color}-50 dark:bg-${solution.color}-900/20 flex flex-col items-center justify-center`}>
                    <solution.icon className={`w-16 h-16 text-${solution.color}-500 mb-4`} />
                    <div className="flex gap-6">
                      {solution.metrics.map((metric) => (
                        <div key={metric.label} className="text-center">
                          <div className={`text-2xl font-bold text-${solution.color}-600 dark:text-${solution.color}-400`}>
                            {metric.value}
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400">{metric.label}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Right: Content */}
                  <div className="md:w-2/3 p-8">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                      {solution.title}
                    </h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                      {solution.subtitle}
                    </p>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">
                      {solution.description}
                    </p>

                    <div className="grid sm:grid-cols-2 gap-3 mb-6">
                      {solution.benefits.map((benefit) => (
                        <div key={benefit} className="flex items-start gap-2">
                          <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" />
                          <span className="text-sm text-gray-700 dark:text-gray-300">{benefit}</span>
                        </div>
                      ))}
                    </div>

                    <IOSButton
                      variant="secondary"
                      size="md"
                      className="flex items-center gap-2"
                      onClick={() => switchToTab(solution.tabKey)}
                    >
                      Learn More
                      <ArrowRight className="w-4 h-4" />
                    </IOSButton>
                  </div>
                </div>
              </IOSCard>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Use Cases */}
      <section className="bg-gray-50 dark:bg-gray-900/50 -mx-4 px-4 py-16 rounded-2xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Common Use Cases
          </h2>
        </motion.div>

        <IOSCardGrid columns={3} gap="md">
          {[
            { icon: TrendingUp, title: 'Model Selection', desc: 'Compare models on cultural dimensions before deployment' },
            { icon: Target, title: 'Pre-Release Audit', desc: 'Identify cultural risks before public release' },
            { icon: FileText, title: 'Publication Support', desc: 'Generate reproducible results for papers' },
            { icon: Globe, title: 'Localization QA', desc: 'Validate cultural appropriateness across regions' },
            { icon: Eye, title: 'Bias Detection', desc: 'Surface subtle cultural biases in model outputs' },
            { icon: Building2, title: 'Compliance', desc: 'Document cultural evaluation for regulatory needs' },
          ].map((item) => (
            <IOSCard key={item.title} variant="flat">
              <IOSCardHeader
                emoji={<item.icon className="w-6 h-6 text-slate-600" />}
                title={item.title}
              />
              <IOSCardContent>
                <p className="text-sm text-gray-600 dark:text-gray-400">{item.desc}</p>
              </IOSCardContent>
            </IOSCard>
          ))}
        </IOSCardGrid>
      </section>
    </>
  );
}

export default function SolutionsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const currentTab = (searchParams.get('tab') ?? 'overview') as TabKey;
  const selectedIndex = TAB_KEYS.indexOf(currentTab) >= 0 ? TAB_KEYS.indexOf(currentTab) : 0;

  const handleTabChange = useCallback(
    (index: number) => {
      const tabKey = TAB_KEYS[index];
      if (tabKey === 'overview') {
        setSearchParams({});
      } else {
        setSearchParams({ tab: tabKey });
      }
    },
    [setSearchParams],
  );

  return (
    <div className="space-y-20">
      {/* Hero */}
      <section className="pt-8 pb-12">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-4xl mx-auto"
        >
          <h1 className="text-page-title mb-6">
            Solutions for Every Team
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-3xl mx-auto">
            Whether you're building AI, researching models, or deploying cultural technology — VULCA provides the evaluation framework you need.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/demo">
              <IOSButton variant="primary" size="lg" className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Book a Demo
              </IOSButton>
            </Link>
            <Link to="/pricing">
              <IOSButton variant="secondary" size="lg" className="flex items-center gap-2">
                View Pricing
              </IOSButton>
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Tab Switcher */}
      <section className="flex justify-center">
        <IOSSegmentedControl
          segments={TAB_SEGMENTS}
          selectedIndex={selectedIndex}
          onChange={handleTabChange}
          size="regular"
          className="w-full max-w-lg"
        />
      </section>

      {/* Tab Content */}
      {currentTab === 'overview' && <SolutionsOverview />}
      {currentTab === 'ai-labs' && <AILabSolutionPage />}
      {currentTab === 'research' && <ResearchSolutionPage />}
      {currentTab === 'museums' && <MuseumSolutionPage />}

      {/* CTA */}
      <section className="py-12 text-center">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Ready to get started?
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
          Book a demo to discuss your specific evaluation needs
        </p>
        <Link to="/demo">
          <IOSButton variant="primary" size="lg" className="flex items-center gap-2 mx-auto">
            <Calendar className="w-5 h-5" />
            Book a Demo
          </IOSButton>
        </Link>
      </section>
    </div>
  );
}
