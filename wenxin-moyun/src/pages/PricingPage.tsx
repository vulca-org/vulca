import { Link } from 'react-router-dom';
import {
  Calendar,
  CheckCircle2,
  X,
  ArrowRight,
  Sparkles,
  Zap,
  Building2,
  HelpCircle,
  Code2
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useState } from 'react';
import {
  IOSButton,
  IOSCard,
  IOSCardHeader,
  IOSCardContent,
  IOSCardFooter,
  IOSCardGrid,
} from '../components/ios';
import { VULCA_VERSION } from '../config/version';

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6 }
};

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'For academic research and open-source projects',
    icon: Sparkles,
    color: 'gray',
    cta: 'Try Public Demo',
    ctaLink: '/canvas',
    ctaVariant: 'secondary' as const,
    deliverables: ['Public demo access', '6D overview only'],
    features: [
      { name: 'Public leaderboard access', included: true },
      { name: 'Limited demo evaluations', included: true },
      { name: 'Citation export (BibTeX, RIS)', included: true },
      { name: 'Community support', included: true },
      { name: 'Batch evaluations', included: false },
      { name: '47D diagnostics', included: false },
      { name: 'Custom benchmarks', included: false },
      { name: 'API access', included: false },
    ],
  },
  {
    name: 'Pilot',
    price: '$2,500',
    period: 'per engagement',
    billingNote: '1 model, 1 benchmark dataset',
    description: 'For model selection and pre-release audits',
    icon: Zap,
    color: 'blue',
    cta: 'Request Pilot',
    ctaLink: '/demo',
    ctaVariant: 'primary' as const,
    popular: true,
    deliverables: ['Full 47D report (PDF)', '8 cultural perspectives', 'Delivery: 48-72 hours'],
    features: [
      { name: 'Everything in Free', included: true },
      { name: 'Full 47D evaluation report', included: true },
      { name: '8 cultural perspective analysis', included: true },
      { name: 'Risk identification & recommendations', included: true },
      { name: 'Evidence samples for findings', included: true },
      { name: 'PDF deliverable report', included: true },
      { name: 'Dedicated support', included: true },
      { name: 'API access', included: false },
    ],
  },
  {
    name: 'API',
    price: '$0.25',
    period: 'per evaluation',
    billingNote: 'Pay-as-you-go, 100 free credits',
    description: 'For developers integrating cultural compliance',
    icon: Code2,
    color: 'emerald',
    cta: 'Get API Key',
    ctaLink: '/demo',
    ctaVariant: 'primary' as const,
    deliverables: ['REST API access', 'L1-L5 scoring', 'Cultural tradition detection', '30 req/min'],
    features: [
      { name: 'REST API (evaluate + identify)', included: true },
      { name: 'L1-L5 cultural scoring', included: true },
      { name: 'Auto tradition detection', included: true },
      { name: '9 cultural traditions', included: true },
      { name: 'Scout evidence gathering', included: true },
      { name: 'Risk & taboo detection', included: true },
      { name: '30 requests/minute', included: true },
      { name: 'OpenAPI/Swagger docs', included: true },
    ],
  },
  {
    name: 'Enterprise',
    price: 'From $15,000',
    period: 'annual',
    description: 'For continuous evaluation and private data',
    icon: Building2,
    color: 'purple',
    cta: 'Talk to Sales',
    ctaLink: '/demo',
    ctaVariant: 'secondary' as const,
    deliverables: ['Unlimited evaluations', 'Custom benchmarks', 'API access', 'Regression monitoring'],
    features: [
      { name: 'Everything in API', included: true },
      { name: 'Unlimited evaluations', included: true },
      { name: 'Custom benchmark upload', included: true },
      { name: 'Private workspace & RBAC', included: true },
      { name: 'Dedicated API endpoint', included: true },
      { name: 'Regression monitoring', included: true },
      { name: 'SLA & priority support', included: true },
      { name: 'Custom integrations', included: true },
    ],
  },
];

const faqs = [
  {
    q: 'What is included in a Pilot evaluation?',
    a: 'A Pilot includes a comprehensive 47D evaluation across all 8 cultural perspectives, delivered as a PDF report with evidence samples, risk identification, and actionable recommendations. Standard delivery is 48-72 hours.',
  },
  {
    q: 'What is your evaluation SOP?',
    a: 'Our 5-step process: (1) Benchmark selection — choose from our curated library or upload custom data; (2) Model inference — run your model against selected benchmarks; (3) Multi-perspective scoring — 47D evaluation across 8 cultural perspectives; (4) QA review — human expert validation of flagged outputs; (5) Report generation — PDF deliverable with evidence samples and recommendations.',
  },
  {
    q: 'Can I evaluate custom models?',
    a: 'Yes! Pilot and Enterprise plans support evaluation of any model via API access. You provide model endpoints or outputs, and we run the VULCA framework.',
  },
  {
    q: 'Is there a free trial for Enterprise?',
    a: 'We offer a Pilot engagement as the entry point for enterprises. This lets you see the full value of VULCA before committing to an annual plan.',
  },
  {
    q: 'What citation formats are supported?',
    a: 'We support BibTeX, RIS, CSL JSON, APA, MLA, Chicago, and Harvard formats for all evaluation results.',
  },
  {
    q: 'How does the API pricing work?',
    a: 'The API plan is pay-per-evaluation at $0.25 per image. You get 100 free credits to start. Each evaluation returns L1-L5 cultural scores, rationales, risk flags, and improvement recommendations. Rate limit is 30 requests per minute per API key.',
  },
  {
    q: 'Do you offer academic discounts?',
    a: 'Yes! Academic institutions can access the Free tier and request discounted Pilot evaluations. Contact us for details.',
  },
];

export default function PricingPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

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
            From Public Demo to Enterprise Evaluation
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-3xl mx-auto">
            Choose the plan that fits your cultural AI evaluation needs
          </p>
        </motion.div>
      </section>

      {/* Pricing Cards */}
      <section>
        <IOSCardGrid columns={4} gap="lg">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <IOSCard
                variant="elevated"
                className={`h-full relative ${plan.popular ? 'ring-2 ring-slate-600' : ''}`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-slate-600 text-white text-xs font-semibold rounded-full">
                    Most Popular
                  </div>
                )}
                <IOSCardHeader
                  emoji={<plan.icon className={`w-8 h-8 text-${plan.color}-500`} />}
                  title={plan.name}
                  subtitle={plan.description}
                />
                <IOSCardContent>
                  <div className="mb-6">
                    <span className="text-4xl font-bold text-gray-900 dark:text-white">
                      {plan.price}
                    </span>
                    <span className="text-gray-500 dark:text-gray-400 ml-2">
                      / {plan.period}
                    </span>
                    {'billingNote' in plan && plan.billingNote && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {plan.billingNote}
                      </p>
                    )}
                  </div>

                  <ul className="space-y-3">
                    {plan.features.map((feature) => (
                      <li key={feature.name} className="flex items-start gap-2">
                        {feature.included ? (
                          <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" />
                        ) : (
                          <X className="w-5 h-5 text-gray-300 dark:text-gray-600 flex-shrink-0" />
                        )}
                        <span className={feature.included ? 'text-gray-700 dark:text-gray-300' : 'text-gray-400 dark:text-gray-500'}>
                          {feature.name}
                        </span>
                      </li>
                    ))}
                  </ul>
                </IOSCardContent>
                <IOSCardFooter>
                  <Link to={plan.ctaLink} className="w-full">
                    <IOSButton
                      variant={plan.ctaVariant}
                      size="md"
                      className="w-full flex items-center justify-center gap-2"
                    >
                      {plan.cta}
                      <ArrowRight className="w-4 h-4" />
                    </IOSButton>
                  </Link>
                </IOSCardFooter>
              </IOSCard>
            </motion.div>
          ))}
        </IOSCardGrid>
      </section>

      {/* Scope & Deliverables Section */}
      <section className="py-16">
        <motion.div {...fadeInUp} className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            What's Included
          </h2>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Transparent deliverables for every engagement level
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Included */}
          <IOSCard variant="elevated">
            <IOSCardHeader
              emoji={<CheckCircle2 className="w-8 h-8 text-green-500" />}
              title="Included in All Plans"
            />
            <IOSCardContent>
              <ul className="space-y-3">
                {[
                  `${VULCA_VERSION.totalDimensions}-dimension evaluation report (Pilot+)`,
                  `${VULCA_VERSION.totalPerspectives} cultural perspective analysis`,
                  `Comparison with ${VULCA_VERSION.totalModels} benchmark models`,
                  'PDF export with full methodology',
                  'Evidence samples for flagged outputs',
                  'BibTeX/RIS citation export',
                  'Risk identification & recommendations',
                ].map((item) => (
                  <li key={item} className="flex items-start gap-2">
                    <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700 dark:text-gray-300 text-sm">{item}</span>
                  </li>
                ))}
              </ul>
            </IOSCardContent>
          </IOSCard>

          {/* Not Included */}
          <IOSCard variant="elevated">
            <IOSCardHeader
              emoji={<X className="w-8 h-8 text-gray-400" />}
              title="Enterprise Only / Custom"
            />
            <IOSCardContent>
              <ul className="space-y-3">
                {[
                  'Custom dimension development',
                  'On-premise deployment',
                  'White-label licensing',
                  'Real-time API access',
                  'Custom benchmark upload',
                  'Private workspace & RBAC',
                  'SLA & priority support',
                ].map((item) => (
                  <li key={item} className="flex items-start gap-2">
                    <X className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-500 dark:text-gray-400 text-sm">{item}</span>
                  </li>
                ))}
              </ul>
              <div className="mt-4 p-3 bg-slate-50 dark:bg-slate-900/30 rounded-lg">
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Need custom features? <Link to="/demo" className="text-slate-600 dark:text-slate-400 font-medium hover:underline">Talk to our team</Link> about Enterprise plans.
                </p>
              </div>
            </IOSCardContent>
          </IOSCard>
        </div>
      </section>

      {/* How It Works - Process Flow */}
      <section className="py-16">
        <motion.div {...fadeInUp} className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            How It Works
          </h2>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            From booking to report delivery — a streamlined evaluation process
          </p>
        </motion.div>

        <div className="max-w-4xl mx-auto">
          {/* Process Steps */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative">
            {/* Connecting line for desktop */}
            <div className="hidden md:block absolute top-8 left-[12.5%] right-[12.5%] h-0.5 bg-gradient-to-r from-slate-300 via-slate-400 to-slate-300 dark:from-slate-700 dark:via-slate-600 dark:to-slate-700" />

            {[
              { step: 1, title: 'Book Demo', duration: '15 min', icon: Calendar, color: 'slate' },
              { step: 2, title: 'Pilot Kickoff', duration: '30 min setup', icon: Zap, color: 'blue' },
              { step: 3, title: 'Model Submission', duration: 'API / Upload', icon: ArrowRight, color: 'purple' },
              { step: 4, title: 'Report Delivery', duration: '48-72 hours', icon: CheckCircle2, color: 'green' },
            ].map((item, index) => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="relative flex flex-col items-center text-center"
              >
                {/* Step circle */}
                <div className={`w-16 h-16 rounded-full bg-${item.color}-100 dark:bg-${item.color}-900/30 flex items-center justify-center mb-4 relative z-10 border-4 border-white dark:border-gray-900`}>
                  <item.icon className={`w-6 h-6 text-${item.color}-600 dark:text-${item.color}-400`} />
                </div>

                {/* Step number badge */}
                <span className="absolute -top-1 -right-1 w-6 h-6 bg-slate-600 text-white text-xs font-bold rounded-full flex items-center justify-center z-20">
                  {item.step}
                </span>

                {/* Step content */}
                <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
                  {item.title}
                </h4>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {item.duration}
                </p>

                {/* Mobile arrow (between steps) */}
                {index < 3 && (
                  <div className="md:hidden mt-4 mb-2">
                    <ArrowRight className="w-5 h-5 text-gray-300 dark:text-gray-600 rotate-90" />
                  </div>
                )}
              </motion.div>
            ))}
          </div>

          {/* CTA after flow */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mt-12"
          >
            <Link to="/demo">
              <IOSButton variant="primary" size="md" className="inline-flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Start with Step 1: Book a Demo
              </IOSButton>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Feature Comparison Table */}
      <section className="bg-gray-50 dark:bg-gray-900/50 -mx-4 px-4 py-16 rounded-2xl">
        <motion.div {...fadeInUp} className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Feature Comparison
          </h2>
        </motion.div>

        <div className="overflow-x-auto">
          <table className="w-full max-w-4xl mx-auto">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="py-4 px-4 text-left text-sm font-semibold text-gray-900 dark:text-white">Feature</th>
                <th className="py-4 px-4 text-center text-sm font-semibold text-gray-900 dark:text-white">Free</th>
                <th className="py-4 px-4 text-center text-sm font-semibold text-gray-900 dark:text-white">Pilot</th>
                <th className="py-4 px-4 text-center text-sm font-semibold text-gray-900 dark:text-white">API</th>
                <th className="py-4 px-4 text-center text-sm font-semibold text-gray-900 dark:text-white">Enterprise</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {[
                ['Public leaderboard', true, true, true, true],
                ['Demo evaluations', '5/month', 'Unlimited', 'Pay-per-use', 'Unlimited'],
                ['L1-L5 cultural scoring', false, true, true, true],
                ['47D diagnostics', false, true, true, true],
                ['8 cultural perspectives', false, true, true, true],
                ['PDF reports', false, true, false, true],
                ['REST API access', false, false, true, true],
                ['Tradition auto-detection', false, false, true, true],
                ['Scout evidence', false, true, true, true],
                ['Custom benchmarks', false, false, false, true],
                ['RBAC & workspace', false, false, false, true],
                ['SLA support', false, false, false, true],
              ].map(([feature, free, pilot, api, enterprise], index) => (
                <tr key={index}>
                  <td className="py-3 px-4 text-sm text-gray-700 dark:text-gray-300">{feature as string}</td>
                  {[free, pilot, api, enterprise].map((value, i) => (
                    <td key={i} className="py-3 px-4 text-center">
                      {typeof value === 'boolean' ? (
                        value ? (
                          <CheckCircle2 className="w-5 h-5 text-green-500 mx-auto" />
                        ) : (
                          <X className="w-5 h-5 text-gray-300 dark:text-gray-600 mx-auto" />
                        )
                      ) : (
                        <span className="text-sm text-gray-700 dark:text-gray-300">{value}</span>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* API Code Example */}
      <section className="py-16">
        <motion.div {...fadeInUp} className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Developer-Friendly API
          </h2>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Integrate cultural compliance scoring in minutes with our REST API
          </p>
        </motion.div>

        <div className="max-w-3xl mx-auto grid md:grid-cols-2 gap-6">
          <IOSCard variant="elevated">
            <IOSCardHeader
              emoji={<Code2 className="w-6 h-6 text-emerald-500" />}
              title="Evaluate Artwork"
              subtitle="POST /api/v1/evaluate"
            />
            <IOSCardContent>
              <pre className="text-xs bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto whitespace-pre">
{`curl -X POST /api/v1/evaluate \\
  -H "Authorization: Bearer YOUR_KEY" \\
  -d '{
    "image_url": "https://...",
    "tradition": "chinese_xieyi",
    "subject": "ink landscape",
    "include_evidence": true
  }'`}
              </pre>
              <p className="text-xs text-gray-500 mt-3">
                Returns L1-L5 scores, rationales, risk flags, and cultural diagnosis
              </p>
            </IOSCardContent>
          </IOSCard>

          <IOSCard variant="elevated">
            <IOSCardHeader
              emoji={<Code2 className="w-6 h-6 text-emerald-500" />}
              title="Identify Tradition"
              subtitle="POST /api/v1/identify-tradition"
            />
            <IOSCardContent>
              <pre className="text-xs bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto whitespace-pre">
{`curl -X POST /api/v1/identify-tradition \\
  -H "Authorization: Bearer YOUR_KEY" \\
  -d '{
    "image_url": "https://..."
  }'

// Response:
// { "tradition": "chinese_xieyi",
//   "confidence": 0.87,
//   "recommended_weights": {...} }`}
              </pre>
              <p className="text-xs text-gray-500 mt-3">
                Auto-detect tradition from 9 cultural categories with confidence scores
              </p>
            </IOSCardContent>
          </IOSCard>
        </div>
      </section>

      {/* FAQ */}
      <section>
        <motion.div {...fadeInUp} className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Frequently Asked Questions
          </h2>
        </motion.div>

        <div className="max-w-3xl mx-auto space-y-4">
          {faqs.map((faq, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              viewport={{ once: true }}
            >
              <button
                onClick={() => setOpenFaq(openFaq === index ? null : index)}
                className="w-full flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md transition-shadow"
              >
                <span className="text-left font-medium text-gray-900 dark:text-white flex items-center gap-2">
                  <HelpCircle className="w-5 h-5 text-slate-600" />
                  {faq.q}
                </span>
                <ArrowRight className={`w-5 h-5 text-gray-400 transition-transform ${openFaq === index ? 'rotate-90' : ''}`} />
              </button>
              {openFaq === index && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="px-4 py-3 bg-gray-50 dark:bg-gray-900/50 rounded-b-xl -mt-2"
                >
                  <p className="text-gray-600 dark:text-gray-400 pl-7">{faq.a}</p>
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="py-12 text-center">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Not sure which plan is right for you?
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
          Book a call and we'll help you find the best fit
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
