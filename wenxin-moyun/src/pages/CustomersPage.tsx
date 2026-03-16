import { Link } from 'react-router-dom';
import {
  Calendar,
  ArrowRight,
  Building2,
  GraduationCap,
  Palette,
  Quote,
  Star,
  CheckCircle2
} from 'lucide-react';
import { motion } from 'framer-motion';
import {
  IOSButton,
  IOSCard,
  IOSCardContent,
  IOSCardGrid,
} from '../components/ios';
import { VULCA_VERSION } from '../config/version';

// Static color mapping for Tailwind v4 compatibility (no dynamic class interpolation)
const COLOR_MAP: Record<string, { text: string; bg: string; darkBg: string; textSm: string; darkTextSm: string }> = {
  purple: { text: 'text-[#C87F4A]',   bg: 'bg-[#C87F4A]/10',  darkBg: 'dark:bg-[#C87F4A]/20', textSm: 'text-[#C87F4A]',   darkTextSm: 'dark:text-[#DDA574]' },
  blue:   { text: 'text-[#334155]',   bg: 'bg-[#334155]/10',  darkBg: 'dark:bg-[#334155]/20', textSm: 'text-[#334155]',   darkTextSm: 'dark:text-[#94a3b8]' },
  orange: { text: 'text-[#B8923D]',   bg: 'bg-[#B8923D]/10',  darkBg: 'dark:bg-[#B8923D]/20', textSm: 'text-[#B8923D]',   darkTextSm: 'dark:text-[#D4A84E]' },
};

// Research institutions and organizations using VULCA evaluation framework
const customerLogos = [
  { name: 'ACL Research', category: 'research' },
  { name: 'EMNLP 2025', category: 'research' },
  { name: 'NLP Lab', category: 'ai-lab' },
  { name: 'VLM Research', category: 'ai-lab' },
  { name: 'Digital Humanities', category: 'museum' },
  { name: 'Cultural AI Lab', category: 'research' },
];

const caseStudies = [
  {
    title: 'Vision-Language Model Benchmark Study',
    company: 'NLP Research Group',
    category: 'Research',
    icon: GraduationCap,
    color: 'purple',
    challenge: `Needed a systematic framework to evaluate how ${VULCA_VERSION.totalModels} VLMs interpret cultural symbols and artistic contexts across ${VULCA_VERSION.totalPerspectives} cultural perspectives (Western, East Asian, South Asian, Middle Eastern, African, Latin American, Indigenous, and Cross-cultural).`,
    solution: 'Applied VULCA 47-dimension evaluation framework with 7,410 image-text pairs covering 225 fine-grained cultural dimensions. Used standardized prompts and multi-perspective scoring.',
    results: [
      'Published findings at EMNLP 2025',
      'Discovered "symbolic shortcuts" phenomenon in leading VLMs',
      'Created reproducible benchmark with full version control',
    ],
    quote: 'VULCA revealed that even top-performing models like GPT-4V struggle with cultural nuance - they recognize symbols but miss deeper cultural meanings.',
  },
  {
    title: 'Cross-Cultural Fire Imagery Analysis',
    company: 'Cultural AI Research',
    category: 'AI Labs',
    icon: Building2,
    color: 'blue',
    challenge: 'Investigating why VLMs fail to distinguish cultural meanings of fire imagery - from Greek mythology\'s Prometheus to Chinese festival traditions to Native American ceremonial contexts.',
    solution: 'Used VULCA\'s perspective-aware evaluation to probe VLMs on culturally-situated fire imagery across 6 cultural contexts. Applied the R-PAIT (Relevance, Perspective, Accuracy, Insight, Thoughtfulness) scoring rubric.',
    results: [
      'Identified systematic cultural reasoning gaps',
      'Presented findings at WiNLP 2025',
      'Demonstrated 35% accuracy gap between symbol recognition and cultural interpretation',
    ],
    quote: 'The framework showed us exactly where models "see" fire but completely miss whether it represents destruction, purification, or celebration depending on cultural context.',
  },
  {
    title: 'Digital Exhibition AI Curation',
    company: 'Contemporary Art Center',
    category: 'Museums',
    icon: Palette,
    color: 'orange',
    challenge: 'Deploying an AI-powered exhibition guide that could provide meaningful interpretations of contemporary artworks to visitors from diverse cultural backgrounds.',
    solution: 'Validated AI responses using VULCA\'s 47-dimension framework, focusing on Contextual Understanding (Historical, Cultural, Symbolic dimensions) and Critical Analysis (Composition, Technique, Innovation dimensions).',
    results: [
      'Validated interpretation quality across 4 languages',
      'Identified 8 critical cultural sensitivity improvements',
      'Achieved consistent quality scores above 4.2/5.0 across all perspectives',
    ],
    quote: 'VULCA helped us ensure our AI guide doesn\'t just describe what visitors see, but explains why it matters in their cultural context.',
  },
];

const testimonials = [
  {
    quote: 'The 47-dimension framework finally gives us a systematic way to measure cultural understanding beyond simple accuracy metrics. The R-PAIT scoring rubric is particularly valuable for qualitative assessment.',
    author: 'Research Team',
    role: 'VLM Evaluation',
    company: 'NLP Research Group',
  },
  {
    quote: 'What impressed us most was the 8-perspective evaluation. Our models scored well from Western perspectives but revealed significant gaps in South Asian and African cultural contexts - insights we would have missed with traditional benchmarks.',
    author: 'AI Safety Team',
    role: 'Cultural AI Assessment',
    company: 'Foundation Model Lab',
  },
  {
    quote: 'The reproducibility guarantees were essential for our publication. Full version control, standardized prompts, and exportable citations made the peer review process much smoother.',
    author: 'Publication Team',
    role: 'Academic Research',
    company: 'Computational Linguistics Lab',
  },
];

export default function CustomersPage() {
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
            Research-Backed Evaluation Framework
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
            Peer-reviewed methodology featured in leading AI conferences and journals
          </p>
        </motion.div>
      </section>

      {/* Publication Venues */}
      <section className="bg-gray-50 dark:bg-gray-900/50 -mx-4 px-4 py-12 rounded-2xl">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center"
        >
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-8">
            Featured in leading venues and research groups
          </p>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8">
            {customerLogos.map((logo, index) => (
              <motion.div
                key={logo.name}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                viewport={{ once: true }}
                className="flex items-center justify-center h-16 bg-white dark:bg-gray-800 rounded-lg shadow-sm px-4"
              >
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {logo.name}
                </span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* Research Applications */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Research Applications
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            How VULCA methodology has been applied in peer-reviewed research
          </p>
        </motion.div>

        <div className="space-y-8">
          {caseStudies.map((study, index) => (
            <motion.div
              key={study.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <IOSCard variant="elevated">
                <div className="md:flex">
                  {/* Left: Category */}
                  <div className={`md:w-1/4 p-6 ${COLOR_MAP[study.color]?.bg ?? 'bg-gray-50'} ${COLOR_MAP[study.color]?.darkBg ?? 'dark:bg-gray-900/20'} flex flex-col items-center justify-center text-center`}>
                    <study.icon className={`w-12 h-12 ${COLOR_MAP[study.color]?.text ?? 'text-gray-500'} mb-3`} />
                    <span className={`text-sm font-medium ${COLOR_MAP[study.color]?.textSm ?? 'text-gray-600'} ${COLOR_MAP[study.color]?.darkTextSm ?? 'dark:text-gray-400'}`}>
                      {study.category}
                    </span>
                    <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {study.company}
                    </span>
                  </div>

                  {/* Right: Content */}
                  <div className="md:w-3/4 p-6">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                      {study.title}
                    </h3>

                    <div className="grid md:grid-cols-2 gap-6 mb-6">
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Challenge</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{study.challenge}</p>
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Solution</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{study.solution}</p>
                      </div>
                    </div>

                    <div className="mb-6">
                      <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Results</h4>
                      <ul className="grid sm:grid-cols-3 gap-2">
                        {study.results.map((result) => (
                          <li key={result} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400">
                            <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                            {result}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <blockquote className="border-l-4 border-slate-600 pl-4 italic text-gray-600 dark:text-gray-400">
                      "{study.quote}"
                    </blockquote>
                  </div>
                </div>
              </IOSCard>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Researcher Feedback */}
      <section className="bg-gray-50 dark:bg-gray-900/50 -mx-4 px-4 py-16 rounded-2xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Researcher Feedback
          </h2>
        </motion.div>

        <IOSCardGrid columns={3} gap="lg">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={testimonial.author}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <IOSCard variant="flat" className="h-full">
                <IOSCardContent>
                  <div className="flex items-center gap-1 mb-4">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <Quote className="w-8 h-8 text-gray-200 dark:text-gray-700 mb-2" />
                  <p className="text-gray-700 dark:text-gray-300 mb-4">
                    {testimonial.quote}
                  </p>
                  <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                    <p className="font-semibold text-gray-900 dark:text-white">
                      {testimonial.author}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {testimonial.role}, {testimonial.company}
                    </p>
                  </div>
                </IOSCardContent>
              </IOSCard>
            </motion.div>
          ))}
        </IOSCardGrid>
      </section>

      {/* CTA */}
      <section className="py-12 text-center">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Apply VULCA to Your Research
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
          Use peer-reviewed methodology for your cultural AI evaluation needs
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link to="/demo">
            <IOSButton variant="primary" size="lg" className="flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Book a Demo
            </IOSButton>
          </Link>
          <Link to="/solutions">
            <IOSButton variant="secondary" size="lg" className="flex items-center gap-2">
              View Solutions
              <ArrowRight className="w-4 h-4" />
            </IOSButton>
          </Link>
        </div>
      </section>
    </div>
  );
}
