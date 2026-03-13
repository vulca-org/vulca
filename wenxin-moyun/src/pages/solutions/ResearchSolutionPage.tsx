import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Calendar,
  GraduationCap,
  CheckCircle2,
  FileText,
  BookOpen,
  GitBranch,
  Download,
  Quote,
  Users,
  Repeat,
  Database
} from 'lucide-react';
import { motion } from 'framer-motion';
import {
  IOSButton,
  IOSCard,
  IOSCardHeader,
  IOSCardContent,
  IOSCardGrid,
} from '../../components/ios';

export default function ResearchSolutionPage() {
  return (
    <div className="space-y-20">
      {/* Hero */}
      <section className="pt-8 pb-12">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-amber-100 dark:bg-amber-900/30 rounded-xl flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-amber-600" />
            </div>
            <span className="text-sm font-medium text-amber-700 dark:text-amber-500">
              Solution for Research
            </span>
          </div>

          <h1 className="text-page-title mb-6">
            Reproducible Cultural Evaluation for Academic Research
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
            Publish with confidence using our peer-reviewed, citable methodology. Full version control and reproducibility guarantees.
          </p>

          <div className="flex flex-col sm:flex-row gap-4">
            <Link to="/demo">
              <IOSButton variant="primary" size="lg" className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Request Academic Access
              </IOSButton>
            </Link>
            <Link to="/research">
              <IOSButton variant="secondary" size="lg" className="flex items-center gap-2">
                View Publications
              </IOSButton>
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Academic Challenges */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Built for Academic Rigor
          </h2>
        </motion.div>

        <IOSCardGrid columns={3} gap="lg">
          <IOSCard variant="elevated">
            <IOSCardHeader
              emoji={<Repeat className="w-8 h-8 text-amber-600" />}
              title="Reproducibility Crisis"
            />
            <IOSCardContent>
              <p className="text-gray-600 dark:text-gray-400">
                Ad-hoc evaluation methods make it impossible for others to reproduce your results. VULCA provides version-controlled, deterministic evaluation.
              </p>
            </IOSCardContent>
          </IOSCard>

          <IOSCard variant="elevated">
            <IOSCardHeader
              emoji={<Quote className="w-8 h-8 text-slate-600" />}
              title="Citation Complexity"
            />
            <IOSCardContent>
              <p className="text-gray-600 dark:text-gray-400">
                Properly citing evaluation methodology is often unclear. VULCA exports in 7 citation formats with all provenance metadata included.
              </p>
            </IOSCardContent>
          </IOSCard>

          <IOSCard variant="elevated">
            <IOSCardHeader
              emoji={<Users className="w-8 h-8 text-green-500" />}
              title="Collaboration Barriers"
            />
            <IOSCardContent>
              <p className="text-gray-600 dark:text-gray-400">
                Sharing evaluation results across institutions is difficult. Standardized VULCA format enables seamless collaboration.
              </p>
            </IOSCardContent>
          </IOSCard>
        </IOSCardGrid>
      </section>

      {/* Features for Researchers */}
      <section className="bg-gray-50 dark:bg-gray-900/50 -mx-4 px-4 py-16 rounded-2xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Features for Researchers
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-amber-100 dark:bg-amber-900/30 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-amber-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">7 Citation Formats</h3>
            </div>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> BibTeX</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> RIS (EndNote, Zotero)</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> CSL JSON (Mendeley)</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> APA, MLA, Chicago, Harvard</li>
            </ul>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-slate-100 dark:bg-slate-900/30 rounded-lg flex items-center justify-center">
                <GitBranch className="w-5 h-5 text-slate-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Version Control</h3>
            </div>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> Framework version tracking</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> Dataset version control</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> Deterministic evaluation</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> Full audit trail</li>
            </ul>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                <Download className="w-5 h-5 text-green-500" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Export Options</h3>
            </div>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> PDF report with figures</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> JSON structured data</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> CSV for statistical analysis</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> LaTeX tables</li>
            </ul>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-orange-100 dark:bg-orange-900/30 rounded-lg flex items-center justify-center">
                <Database className="w-5 h-5 text-orange-500" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Benchmark Access</h3>
            </div>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> 130 curated artworks</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> 47D evaluation framework</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> 8 cultural perspectives</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> Ground truth annotations</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Publications */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Peer-Reviewed Publications
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            VULCA methodology is backed by published research
          </p>
        </motion.div>

        <div className="max-w-3xl mx-auto space-y-4">
          {[
            {
              title: 'VULCA: Evaluating Vision-Language Models in Culturally Situated Art Critiques',
              venue: 'EMNLP 2025 Findings',
              badge: 'Main Framework',
            },
            {
              title: 'Seeing Symbols, Missing Cultures: Symbolic Shortcuts in VLMs',
              venue: 'GeBNLP 2025',
              badge: 'Cultural Bias',
            },
          ].map((paper) => (
            <div
              key={paper.title}
              className="flex items-start gap-4 bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm"
            >
              <BookOpen className="w-6 h-6 text-amber-600 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h3 className="font-medium text-gray-900 dark:text-white">{paper.title}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">{paper.venue}</p>
              </div>
              <span className="px-2 py-1 bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-500 text-xs rounded-full">
                {paper.badge}
              </span>
            </div>
          ))}
        </div>

        <div className="text-center mt-8">
          <Link to="/research">
            <IOSButton variant="secondary" size="md" className="flex items-center gap-2 mx-auto">
              View All Papers
              <ArrowRight className="w-4 h-4" />
            </IOSButton>
          </Link>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-amber-50 dark:bg-amber-900/20 -mx-4 px-4 py-12 rounded-2xl text-center">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Academic Discount Available
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto">
          Research institutions can access VULCA at reduced rates. Contact us for details.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link to="/demo">
            <IOSButton variant="primary" size="lg" className="flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Request Academic Access
            </IOSButton>
          </Link>
          <Link to="/research">
            <IOSButton variant="secondary" size="lg" className="flex items-center gap-2">
              Explore Dataset
            </IOSButton>
          </Link>
        </div>
      </section>
    </div>
  );
}
