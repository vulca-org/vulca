import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Calendar,
  CheckCircle2,
  Shield,
  BarChart3,
  Zap,
  Building2,
  GraduationCap,
  FileText,
  Layers,
  Target,
  Eye,
  AlertTriangle,
  Download,
  Terminal,
  Copy,
  Check,
  ExternalLink,
  MessageSquare,
  GitFork,
  Sparkles,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useState } from 'react';
import { useLeaderboard } from '../hooks/useLeaderboard';
import {
  IOSButton,
  IOSCard,
  IOSCardHeader,
  IOSCardContent,
  IOSCardGrid,
} from '../components/ios';
import { downloadSampleReport } from '../utils/pdfExport';
import { VULCA_VERSION } from '../config/version';

// Animation variants
const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6 }
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
};

function OpenSourceInstall() {
  const [copied, setCopied] = useState(false);
  const installCmd = 'pip install vulca';

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(installCmd);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = installCmd;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <motion.div
      className="mt-8 flex flex-col items-center gap-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.7 }}
    >
      {/* pip install command block */}
      <div className="flex items-center gap-2 bg-gray-900 dark:bg-gray-950 rounded-xl px-5 py-3 shadow-lg border border-gray-700 dark:border-gray-600">
        <Terminal className="w-4 h-4 text-green-400 flex-shrink-0" />
        <code className="font-mono text-sm text-gray-100 select-all">
          {installCmd}
        </code>
        <button
          onClick={handleCopy}
          className="ml-3 p-1.5 rounded-md hover:bg-gray-700 transition-colors text-gray-400 hover:text-white"
          aria-label="Copy install command"
        >
          {copied ? (
            <Check className="w-4 h-4 text-green-400" />
          ) : (
            <Copy className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Open source action buttons */}
      <div className="flex flex-wrap items-center justify-center gap-3">
        <Link to="/canvas">
          <IOSButton
            variant="secondary"
            size="sm"
            className="flex items-center gap-2"
          >
            <ExternalLink className="w-4 h-4" />
            Try Online
          </IOSButton>
        </Link>
        <a
          href="https://github.com/vulca-org/vulca"
          target="_blank"
          rel="noopener noreferrer"
        >
          <IOSButton
            variant="secondary"
            size="sm"
            className="flex items-center gap-2"
          >
            <GitFork className="w-4 h-4" />
            GitHub
          </IOSButton>
        </a>
      </div>
    </motion.div>
  );
}

export default function HomePage() {
  const { entries: leaderboard } = useLeaderboard();

  return (
    <div className="space-y-24">
      {/* ============= HERO SECTION ============= */}
      <section className="relative pt-8 pb-12">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-4xl mx-auto"
        >
          {/* Trust badges - above headline */}
          <motion.div
            className="flex flex-wrap justify-center gap-3 mb-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 text-xs font-medium rounded-full">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Reproducible
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-slate-100 dark:bg-slate-800/30 text-slate-700 dark:text-slate-300 text-xs font-medium rounded-full">
              <BarChart3 className="w-3.5 h-3.5" />
              Decision-grade
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-bronze-500/10 dark:bg-bronze-500/20 text-[#C87F4A] dark:text-bronze-400 text-xs font-medium rounded-full">
              <Shield className="w-3.5 h-3.5" />
              Enterprise-ready
            </span>
          </motion.div>

          {/* Main headline */}
          <motion.h1
            className="text-large-title mb-6 leading-tight"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            Evaluate AI Models for{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-slate-700 to-bronze-500 dark:from-slate-400 dark:to-bronze-400">
              Cultural Understanding
            </span>
          </motion.h1>

          {/* Sub-headline */}
          <motion.p
            className="text-h2 text-gray-600 dark:text-gray-300 mb-4 max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            47 dimensions × 8 cultural perspectives
          </motion.p>

          <motion.p
            className="text-xl font-semibold text-transparent bg-clip-text bg-gradient-to-r from-[#B0683A] to-slate-600 dark:from-[#B0683A] dark:to-slate-400 mb-3 max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.45 }}
          >
            Stop guessing. Start measuring.
          </motion.p>

          <motion.p
            className="text-lg text-gray-500 dark:text-gray-400 mb-10 max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            Reproducible evaluation + Explainable diagnostics + Deliverable reports
          </motion.p>

          {/* CTAs - Three-button layout for better conversion */}
          <motion.div
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <Link to="/demo">
              <IOSButton
                variant="primary"
                size="lg"
                className="flex items-center gap-2 min-w-[200px] justify-center"
                data-testid="hero-book-demo"
              >
                <Calendar className="w-5 h-5" />
                Book a Demo
                <ArrowRight className="w-5 h-5" />
              </IOSButton>
            </Link>
            <IOSButton
              variant="secondary"
              size="lg"
              className="flex items-center gap-2 min-w-[200px] justify-center"
              onClick={downloadSampleReport}
              data-testid="hero-download-report"
            >
              <Download className="w-5 h-5" />
              Sample Report
            </IOSButton>
            <Link to="/canvas">
              <IOSButton
                variant="primary"
                size="lg"
                className="flex items-center gap-2 min-w-[180px] justify-center !bg-[#B0683A] hover:!bg-[#9A5A32] !border-[#B0683A]"
                data-testid="hero-try-now"
              >
                <Sparkles className="w-5 h-5" />
                Try It Now
              </IOSButton>
            </Link>
            <Link to="/canvas">
              <IOSButton
                variant="text"
                size="lg"
                className="flex items-center gap-2 min-w-[160px] justify-center text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-300"
                data-testid="hero-try-demo"
              >
                Try Public Demo
                <ArrowRight className="w-4 h-4" />
              </IOSButton>
            </Link>
          </motion.div>

          {/* Open Source Install Section */}
          <OpenSourceInstall />

          {/* Enterprise Value Propositions */}
          <motion.div
            className="mt-12 grid sm:grid-cols-2 gap-4 max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <div className="flex items-start gap-3 p-4 bg-slate-50 dark:bg-slate-900/30 rounded-xl border border-slate-200 dark:border-slate-800">
              <Building2 className="w-5 h-5 text-slate-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-medium text-gray-900 dark:text-white text-sm">For AI Companies</p>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Benchmark your models against {VULCA_VERSION.totalModels} competitors across {VULCA_VERSION.totalDimensions} dimensions before public release
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 bg-slate-50 dark:bg-slate-900/30 rounded-xl border border-slate-200 dark:border-slate-800">
              <GraduationCap className="w-5 h-5 text-bronze-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-medium text-gray-900 dark:text-white text-sm">For Research Institutions</p>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Publish with peer-reviewed evaluation methodology accepted at top-tier venues
                </p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* ============= SOCIAL PROOF STRIP ============= */}
      <section className="py-8 bg-gray-50 dark:bg-gray-900/50 -mx-4 px-4 rounded-2xl">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, amount: 0.1 }}
          className="text-center"
        >
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
            Peer-reviewed methodology featured in academic publications
          </p>
          <div className="flex flex-wrap justify-center items-center gap-6 md:gap-12">
            {/* Conference badges */}
            <div className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
              <FileText className="w-5 h-5 text-slate-600" />
              <span className="font-semibold text-gray-900 dark:text-white">EMNLP 2025</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
              <FileText className="w-5 h-5 text-green-600" />
              <span className="font-semibold text-gray-900 dark:text-white">WiNLP 2025</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
              <FileText className="w-5 h-5 text-bronze-500" />
              <span className="font-semibold text-gray-900 dark:text-white">arXiv 2026</span>
            </div>
          </div>
        </motion.div>
      </section>

      {/* ============= PROBLEM → OUTCOME ============= */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.1 }}
          className="text-center mb-12"
        >
          <h2 className="text-h1 mb-4">
            Why Cultural Evaluation Matters
          </h2>
          <p className="text-body max-w-2xl mx-auto">
            As AI models grow more powerful, cultural risks become harder to detect
          </p>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="initial"
          whileInView="animate"
          viewport={{ once: true, amount: 0.1 }}
        >
          <IOSCardGrid columns={3} gap="lg">
            {/* Problem 1 */}
            <motion.div variants={fadeInUp}>
              <IOSCard variant="elevated" className="h-full">
                <IOSCardHeader
                  emoji={<AlertTriangle className="w-8 h-8 text-orange-500" />}
                  title="Hidden Cultural Risks"
                />
                <IOSCardContent>
                  <p className="text-gray-600 dark:text-gray-400">
                    Stronger models can produce more sophisticated — yet subtly biased — cultural content that's harder to catch.
                  </p>
                </IOSCardContent>
              </IOSCard>
            </motion.div>

            {/* Problem 2 */}
            <motion.div variants={fadeInUp}>
              <IOSCard variant="elevated" className="h-full">
                <IOSCardHeader
                  emoji={<Target className="w-8 h-8 text-red-500" />}
                  title="Single Metric Fails"
                />
                <IOSCardContent>
                  <p className="text-gray-600 dark:text-gray-400">
                    A single score can't inform model selection or release decisions. You need multi-dimensional, explainable diagnostics.
                  </p>
                </IOSCardContent>
              </IOSCard>
            </motion.div>

            {/* Problem 3 */}
            <motion.div variants={fadeInUp}>
              <IOSCard variant="elevated" className="h-full">
                <IOSCardHeader
                  emoji={<CheckCircle2 className="w-8 h-8 text-green-500" />}
                  title="Reproducibility Required"
                />
                <IOSCardContent>
                  <p className="text-gray-600 dark:text-gray-400">
                    Evaluations must be reproducible and citable. Ad-hoc testing doesn't support audits or publications.
                  </p>
                </IOSCardContent>
              </IOSCard>
            </motion.div>
          </IOSCardGrid>
        </motion.div>
      </section>

      {/* ============= PRODUCT PILLARS ============= */}
      <section className="bg-gradient-to-b from-gray-50 to-white dark:from-gray-900/50 dark:to-gray-900/0 -mx-4 px-4 py-16 rounded-2xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.1 }}
          className="text-center mb-12"
        >
          <h2 className="text-h1 mb-4">
            The VULCA Platform
          </h2>
          <p className="text-body max-w-2xl mx-auto">
            Three pillars for comprehensive cultural AI evaluation
          </p>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="initial"
          whileInView="animate"
          viewport={{ once: true, amount: 0.1 }}
        >
          <IOSCardGrid columns={3} gap="lg">
            {/* Pillar 1: Benchmark Library */}
            <motion.div variants={fadeInUp}>
              <IOSCard variant="flat" className="h-full border-t-4 border-t-slate-500">
                <IOSCardHeader
                  emoji={<Layers className="w-8 h-8 text-slate-500" />}
                  title="Benchmark Library"
                  subtitle="L1-L5 Framework"
                />
                <IOSCardContent>
                  <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      130 artworks, 7,410+ annotations
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      5-level cognitive framework (L1-L5)
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      6D core → 47D expanded dimensions
                    </li>
                  </ul>
                </IOSCardContent>
              </IOSCard>
            </motion.div>

            {/* Pillar 2: Evaluation Engine */}
            <motion.div variants={fadeInUp}>
              <IOSCard variant="flat" className="h-full border-t-4 border-t-bronze-500">
                <IOSCardHeader
                  emoji={<Zap className="w-8 h-8 text-bronze-500" />}
                  title="Evaluation Engine"
                  subtitle="Multi-perspective"
                />
                <IOSCardContent>
                  <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      8 cultural perspectives (East/West)
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      Automated scoring pipeline
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      Batch evaluation support
                    </li>
                  </ul>
                </IOSCardContent>
              </IOSCard>
            </motion.div>

            {/* Pillar 3: Diagnostics */}
            <motion.div variants={fadeInUp}>
              <IOSCard variant="flat" className="h-full border-t-4 border-t-green-500">
                <IOSCardHeader
                  emoji={<Eye className="w-8 h-8 text-green-500" />}
                  title="Explainable Diagnostics"
                  subtitle="Actionable insights"
                />
                <IOSCardContent>
                  <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      Top-Δ dimension analysis
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      Failure taxonomy & evidence
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      Export-ready reports (PDF/JSON)
                    </li>
                  </ul>
                </IOSCardContent>
              </IOSCard>
            </motion.div>
          </IOSCardGrid>
        </motion.div>
      </section>

      {/* ============= HOW IT WORKS ============= */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.1 }}
          className="text-center mb-12"
        >
          <h2 className="text-h1 mb-4">
            How It Works
          </h2>
          <p className="text-body max-w-2xl mx-auto">
            From natural language intent to structured evaluation in three steps
          </p>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="initial"
          whileInView="animate"
          viewport={{ once: true, amount: 0.1 }}
          className="relative"
        >
          {/* Connecting line */}
          <div className="hidden md:block absolute top-1/2 left-0 right-0 h-0.5 bg-gray-200 dark:bg-gray-700 -translate-y-1/2 z-0" />

          <div className="grid md:grid-cols-3 gap-8 relative z-10">
            {/* Step 1 */}
            <motion.div variants={fadeInUp} className="text-center">
              <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800/50 rounded-full flex items-center justify-center mx-auto mb-4">
                <MessageSquare className="w-7 h-7 text-slate-600 dark:text-slate-300" />
              </div>
              <h3 className="text-h3 mb-2">
                Describe Your Intent
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Tell VULCA what you want to evaluate in natural language — no configuration needed
              </p>
            </motion.div>

            {/* Step 2 */}
            <motion.div variants={fadeInUp} className="text-center">
              <div className="w-16 h-16 bg-bronze-500/10 dark:bg-bronze-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <GitFork className="w-7 h-7 text-bronze-500 dark:text-bronze-400" />
              </div>
              <h3 className="text-h3 mb-2">
                Auto-Route to Pipeline
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                VULCA routes your request to the right cultural pipeline with matching perspectives and dimensions
              </p>
            </motion.div>

            {/* Step 3 */}
            <motion.div variants={fadeInUp} className="text-center">
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-7 h-7 text-green-600 dark:text-green-400" />
              </div>
              <h3 className="text-h3 mb-2">
                Get Scores & Recommendations
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Receive structured 47D scores, cultural bias analysis, and actionable recommendations in export-ready reports
              </p>
            </motion.div>
          </div>
        </motion.div>
      </section>

      {/* ============= EVIDENCE / STATS ============= */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.1 }}
          className="text-center mb-12"
        >
          <h2 className="text-h1 mb-4">
            Built on Real Data
          </h2>
          <p className="text-body max-w-2xl mx-auto">
            Comprehensive evaluation framework backed by rigorous research
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, amount: 0.1 }}
        >
          <div className="bg-gradient-to-r from-slate-50 to-bronze-500/10 dark:from-slate-800/30 dark:to-bronze-500/20 rounded-2xl p-8">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-slate-600 dark:text-slate-300 mb-2">
                  {leaderboard.length || VULCA_VERSION.totalModels}
                </div>
                <div className="text-gray-600 dark:text-gray-400">Models Evaluated</div>
              </div>
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-bronze-500 dark:text-bronze-400 mb-2">
                  47
                </div>
                <div className="text-gray-600 dark:text-gray-400">Dimensions</div>
              </div>
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-green-600 dark:text-green-400 mb-2">
                  8
                </div>
                <div className="text-gray-600 dark:text-gray-400">Cultural Perspectives</div>
              </div>
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-orange-600 dark:text-orange-400 mb-2">
                  130
                </div>
                <div className="text-gray-600 dark:text-gray-400">Artworks</div>
                <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">7,410+ annotations</div>
              </div>
            </div>

            <div className="mt-8 text-center">
              <IOSButton
                variant="secondary"
                size="md"
                className="inline-flex items-center gap-2"
                onClick={downloadSampleReport}
              >
                <Download className="w-4 h-4" />
                Download Sample Report
              </IOSButton>
            </div>
          </div>
        </motion.div>
      </section>

      {/* ============= FINAL CTA ============= */}
      <section className="py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.1 }}
          className="text-center max-w-3xl mx-auto"
        >
          <h2 className="text-h1 mb-4">
            Make Cultural Evaluation Part of Your Model Release Workflow
          </h2>
          <p className="text-body mb-8">
            Join teams using VULCA to build more culturally aware AI systems
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/demo">
              <IOSButton
                variant="primary"
                size="lg"
                className="flex items-center gap-2 min-w-[200px] justify-center"
              >
                <Calendar className="w-5 h-5" />
                Book a Demo
              </IOSButton>
            </Link>
            <Link to="/pricing">
              <IOSButton
                variant="secondary"
                size="lg"
                className="flex items-center gap-2 min-w-[200px] justify-center"
              >
                View Pricing
              </IOSButton>
            </Link>
          </div>
        </motion.div>
      </section>
    </div>
  );
}
