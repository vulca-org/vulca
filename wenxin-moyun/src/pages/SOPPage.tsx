import { Link } from 'react-router-dom';
import {
  Calendar,
  ClipboardList,
  Target,
  Zap,
  FileCheck,
  MessageSquare,
  BarChart3,
  CheckCircle2,
  Clock,
  Users,
  Settings,
  FileText,
  TrendingUp,
  RefreshCw,
} from 'lucide-react';
import { motion } from 'framer-motion';
import {
  IOSButton,
  IOSCard,
  IOSCardHeader,
  IOSCardContent,
  IOSCardGrid,
} from '../components/ios';

const evaluationSteps = [
  {
    step: 1,
    title: 'Benchmark Selection',
    icon: Target,
    description: 'Choose from our curated art benchmark or bring your own dataset',
    details: [
      'Select from 130+ curated artworks',
      'Upload custom evaluation datasets',
      'Define cultural perspectives to evaluate',
      'Configure evaluation dimensions (6D or 47D)',
    ],
  },
  {
    step: 2,
    title: 'Model Inference',
    icon: Zap,
    description: 'Run your models against the selected benchmark',
    details: [
      'API integration for cloud models',
      'Local deployment support',
      'Parallel inference for efficiency',
      'Automatic output collection',
    ],
  },
  {
    step: 3,
    title: 'Multi-Perspective Scoring',
    icon: Users,
    description: 'Evaluate outputs from 8 cultural perspectives',
    details: [
      'East Asian perspectives (CN, JP, KR)',
      'Western perspectives (UK, US)',
      'Global South perspectives (IN, AF)',
      'Cross-cultural alignment analysis',
    ],
  },
  {
    step: 4,
    title: 'QA Review',
    icon: FileCheck,
    description: 'Quality assurance by expert reviewers',
    details: [
      'Human verification of scores',
      'Outlier detection and review',
      'Consistency checks across models',
      'Bias detection and mitigation',
    ],
  },
  {
    step: 5,
    title: 'Report Generation',
    icon: BarChart3,
    description: 'Comprehensive evaluation report delivery',
    details: [
      'Detailed scoring breakdown',
      'Comparative analysis',
      'Visualization dashboards',
      'Actionable recommendations',
    ],
  },
];

const pilotSOP = [
  {
    day: 'Day 1-2',
    phase: 'Requirements Alignment',
    icon: MessageSquare,
    tasks: [
      'Kickoff call with stakeholders',
      'Define evaluation objectives',
      'Select benchmark dataset',
      'Configure evaluation parameters',
    ],
  },
  {
    day: 'Day 3-7',
    phase: 'Evaluation Execution',
    icon: Settings,
    tasks: [
      'Model API integration',
      'Run inference on benchmark',
      'Multi-perspective scoring',
      'Initial QA review',
    ],
  },
  {
    day: 'Day 8-10',
    phase: 'Report Generation',
    icon: FileText,
    tasks: [
      'Data analysis and visualization',
      'Draft report preparation',
      'Internal review and refinement',
      'Preliminary findings summary',
    ],
  },
  {
    day: 'Day 11-14',
    phase: 'Delivery & Feedback',
    icon: CheckCircle2,
    tasks: [
      'Report presentation call',
      'Q&A and clarifications',
      'Feedback collection',
      'Next steps discussion',
    ],
  },
];

const enterpriseSOP = [
  {
    title: 'Continuous Monitoring',
    icon: TrendingUp,
    description: 'Ongoing evaluation of model performance',
    features: [
      'Weekly automated evaluations',
      'Performance trend tracking',
      'Alert on regression detection',
      'Real-time dashboard access',
    ],
  },
  {
    title: 'Regression Testing',
    icon: RefreshCw,
    description: 'Regular testing against baseline benchmarks',
    features: [
      'Scheduled regression runs',
      'Version comparison reports',
      'Detailed change analysis',
      'Root cause investigation',
    ],
  },
  {
    title: 'Quarterly Reports',
    icon: BarChart3,
    description: 'Comprehensive periodic analysis',
    features: [
      'Executive summary',
      'Trend analysis over time',
      'Competitive benchmarking',
      'Strategic recommendations',
    ],
  },
];

export default function SOPPage() {
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
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-slate-50 dark:bg-slate-900/20 rounded-full mb-6">
            <ClipboardList className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            <span className="text-sm font-medium text-slate-700 dark:text-slate-400">
              Standard Operating Procedures
            </span>
          </div>

          <h1 className="text-page-title mb-6">
            Our Evaluation Process
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
            A clear, repeatable methodology for comprehensive AI art evaluation
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/demo">
              <IOSButton variant="primary" size="lg" className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Start Your Evaluation
              </IOSButton>
            </Link>
            <Link to="/pricing">
              <IOSButton variant="secondary" size="lg">
                View Pricing
              </IOSButton>
            </Link>
          </div>
        </motion.div>
      </section>

      {/* 5-Step Evaluation Process */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            5-Step Evaluation Process
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Our standardized methodology ensures consistent, high-quality results
          </p>
        </motion.div>

        <div className="max-w-4xl mx-auto">
          <div className="relative">
            {/* Connecting line */}
            <div className="absolute left-8 top-12 bottom-12 w-0.5 bg-slate-200 dark:bg-slate-800 hidden md:block" />

            <div className="space-y-8">
              {evaluationSteps.map((step, index) => (
                <motion.div
                  key={step.step}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="flex gap-6"
                >
                  {/* Step number */}
                  <div className="relative z-10 flex-shrink-0">
                    <div className="w-16 h-16 bg-slate-600 rounded-2xl flex items-center justify-center shadow-lg">
                      <span className="text-2xl font-bold text-white">{step.step}</span>
                    </div>
                  </div>

                  {/* Content */}
                  <IOSCard variant="elevated" className="flex-grow">
                    <IOSCardHeader
                      emoji={<step.icon className="w-6 h-6 text-slate-600" />}
                      title={step.title}
                    />
                    <IOSCardContent>
                      <p className="text-gray-600 dark:text-gray-400 mb-4">
                        {step.description}
                      </p>
                      <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {step.details.map((detail) => (
                          <li key={detail} className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                            <CheckCircle2 className="w-4 h-4 text-slate-600 flex-shrink-0" />
                            {detail}
                          </li>
                        ))}
                      </ul>
                    </IOSCardContent>
                  </IOSCard>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Pilot SOP Timeline */}
      <section className="bg-gray-50 dark:bg-gray-900/50 -mx-4 px-4 py-16 rounded-2xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-orange-100 dark:bg-orange-900/30 rounded-full mb-4">
            <Clock className="w-4 h-4 text-orange-600 dark:text-orange-400" />
            <span className="text-sm font-medium text-orange-700 dark:text-orange-400">
              Pilot Package
            </span>
          </div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Pilot Evaluation Timeline
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            A focused 2-week engagement to evaluate your AI models
          </p>
        </motion.div>

        <IOSCardGrid columns={4} gap="md">
          {pilotSOP.map((phase, index) => (
            <motion.div
              key={phase.day}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <IOSCard variant="elevated" className="h-full">
                <IOSCardHeader
                  emoji={<phase.icon className="w-5 h-5 text-orange-500" />}
                  title={phase.day}
                  subtitle={phase.phase}
                />
                <IOSCardContent>
                  <ul className="space-y-2">
                    {phase.tasks.map((task) => (
                      <li key={task} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400">
                        <CheckCircle2 className="w-4 h-4 text-orange-500 flex-shrink-0 mt-0.5" />
                        <span>{task}</span>
                      </li>
                    ))}
                  </ul>
                </IOSCardContent>
              </IOSCard>
            </motion.div>
          ))}
        </IOSCardGrid>

        <div className="text-center mt-8">
          <Link to="/demo">
            <IOSButton variant="primary" size="lg" className="flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Start Pilot Evaluation
            </IOSButton>
          </Link>
        </div>
      </section>

      {/* Enterprise SOP */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-100 dark:bg-green-900/30 rounded-full mb-4">
            <TrendingUp className="w-4 h-4 text-green-600 dark:text-green-400" />
            <span className="text-sm font-medium text-green-700 dark:text-green-400">
              Enterprise Package
            </span>
          </div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Enterprise SOP
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Continuous evaluation and monitoring for production AI systems
          </p>
        </motion.div>

        <IOSCardGrid columns={3} gap="lg">
          {enterpriseSOP.map((item, index) => (
            <motion.div
              key={item.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <IOSCard variant="elevated" className="h-full">
                <IOSCardHeader
                  emoji={<item.icon className="w-6 h-6 text-green-500" />}
                  title={item.title}
                />
                <IOSCardContent>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    {item.description}
                  </p>
                  <ul className="space-y-2">
                    {item.features.map((feature) => (
                      <li key={feature} className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                        <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </IOSCardContent>
              </IOSCard>
            </motion.div>
          ))}
        </IOSCardGrid>
      </section>

      {/* CTA */}
      <section className="bg-slate-50 dark:bg-slate-900/20 -mx-4 px-4 py-12 rounded-2xl text-center">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Ready to Get Started?
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto">
          Contact us to discuss your evaluation needs and choose the right package for your organization
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link to="/demo">
            <IOSButton variant="primary" size="lg" className="flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Book a Demo
            </IOSButton>
          </Link>
          <Link to="/pricing">
            <IOSButton variant="secondary" size="lg">
              View Pricing Plans
            </IOSButton>
          </Link>
        </div>
      </section>
    </div>
  );
}
