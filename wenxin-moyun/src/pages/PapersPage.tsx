/**
 * PapersPage - Academic Publications
 *
 * Displays VULCA-related academic publications with:
 * - Paper cards with abstracts
 * - Multi-format citation (CiteModal integration)
 * - Links to demos, code, and arxiv
 * - Author information
 *
 * @module pages/PapersPage
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  FileText,
  ExternalLink,
  Github,
  Globe,
  Calendar,
  Users,
  Award,
  BookOpen,
} from 'lucide-react';
import { IOSCard, IOSCardContent, IOSButton } from '../components/ios';
import { CiteModal, ProvenanceCard } from '../components/trustlayer';
import type { Citation } from '../utils/trustedExport';
import { VULCA_VERSION } from '../config/version';

interface Paper {
  id: string;
  title: string;
  authors: string[];
  venue: string;
  year: number;
  abstract: string;
  doi?: string;
  arxiv?: string;
  github?: string;
  demo?: string;
  pdf?: string;
  bibtexKey: string;
  tags: string[];
  featured?: boolean;
}

const papers: Paper[] = [
  {
    id: 'vulca-framework',
    title: 'A Structured Framework for Evaluating and Enhancing Interpretive Capabilities of Multimodal LLMs in Culturally Situated Tasks',
    authors: ['Haorui Yu', 'Ramon Ruiz-Dolz', 'Qiufeng Yi'],
    venue: 'EMNLP 2025 Findings',
    year: 2025,
    abstract: `We introduce VULCA—the Vision-Understanding and Language-based Cultural Adaptability Framework—a structured evaluation and enhancement framework for assessing VLMs in culturally situated tasks. VULCA combines three core components: (1) a multi-dimensional human expert benchmark (MHEB) constructed from 163 art commentaries annotated across five cultural capability dimensions; (2) a persona-guided recontextualization mechanism using eight interpretive personas and a domain-specific knowledge base; and (3) a joint evaluation pipeline integrating vector-space semantic alignment with rubric-based capability scoring. We demonstrate over 20% improvement in symbolic reasoning and over 30% improvement in argumentative coherence on Gemini 2.5 Pro using our proposed method.`,
    doi: '10.18653/v1/2025.findings-emnlp.103',
    arxiv: '2509.23208',
    github: 'https://github.com/vulca-org/vulca',
    demo: 'https://vulcaart.art/#/vulca',
    bibtexKey: 'yu2025vulca',
    tags: ['Framework', 'Multimodal', 'Cultural AI', 'Evaluation'],
    featured: true,
  },
  {
    id: 'vulca-bench',
    title: 'VULCA-Bench: A Multicultural Vision-Language Benchmark for Evaluating Cultural Understanding',
    authors: ['Haorui Yu', 'Ramon Ruiz-Dolz', 'Diji Yang', 'Hang He', 'Fengrui Zhang', 'Qiufeng Yi'],
    venue: 'arXiv Preprint',
    year: 2026,
    abstract: `We present VULCA-Bench, a multicultural art-critique benchmark containing 7,410 matched image-critique pairs spanning eight cultural traditions with Chinese-English bilingual coverage. The benchmark is operationalized through a five-layer framework (L1–L5) spanning 225 culture-specific dimensions that preserve Cultural Symmetry—equal methodological treatment across cultures regardless of sample size. We formalize the Cultural Symmetry Principle, which enforces schema and protocol parity across cultures. Pilot experiments show that VULCA-Bench exposes systematic failures in higher-layer cultural reasoning (L3–L5) not captured by standard VLM benchmarks. The complete dataset is available under CC BY 4.0 license.`,
    arxiv: '2601.07986',
    github: 'https://github.com/vulca-org/vulca',
    bibtexKey: 'yu2026vulcabench',
    tags: ['Dataset', 'Benchmark', 'Multilingual', 'Cultural Symmetry'],
    featured: true,
  },
  {
    id: 'cross-cultural-critique',
    title: 'Cross-Cultural Expert-Level Art Critique Evaluation with Vision-Language Models',
    authors: ['Haorui Yu', 'Ramon Ruiz-Dolz', 'Xuehang Wen', 'Fengrui Zhang', 'Qiufeng Yi'],
    venue: 'arXiv Preprint (submitted to ACL 2026)',
    year: 2026,
    abstract: `We present a tri-tier evaluation framework for cross-cultural art-critique assessment: Tier I computes automated coverage and risk indicators offline; Tier II applies rubric-based scoring using a single primary judge across five dimensions; and Tier III calibrates the aggregate score to human ratings via isotonic regression, yielding a 5.2% reduction in MAE on a 152-sample held-out set. We evaluate 15 VLMs on 294 expert anchors spanning six cultural traditions. Key findings: (i) automated metrics are unreliable proxies for cultural depth, (ii) Western samples score higher than non-Western samples under our sampling and rubric, and (iii) cross-judge scale mismatch makes naive score averaging unreliable.`,
    arxiv: '2601.07984',
    bibtexKey: 'yu2026crosscultural',
    tags: ['Evaluation', 'VLM', 'Art Critique', 'Cross-Cultural'],
  },
  {
    id: 'fire-imagery',
    title: 'Seeing Symbols, Missing Cultures: Probing Vision-Language Models\' Reasoning on Fire Imagery and Cultural Meaning',
    authors: ['Haorui Yu', 'Yang Zhao', 'Yijia Chu', 'Qiufeng Yi'],
    venue: 'WiNLP @ ACL 2025',
    year: 2025,
    abstract: `Vision-Language Models often appear culturally competent but rely on superficial pattern matching rather than genuine cultural understanding. We introduce a diagnostic framework to probe VLM reasoning on fire-themed cultural imagery through both classification and explanation analysis. Testing 11 models (including GPT-4o, Claude 3.5/3.7/4, Qwen2.5-VL, Aya Vision) on Western festivals, non-Western traditions, and emergency scenes reveals systematic biases: models correctly identify prominent Western festivals but struggle with underrepresented cultural events, frequently offering vague labels or dangerously misclassifying emergencies as celebrations.`,
    arxiv: '2509.23311',
    github: 'https://github.com/vulca-org/vulca',
    bibtexKey: 'yu2025firesymbols',
    tags: ['Bias Analysis', 'VLM', 'Cultural Reasoning', 'Diagnostics'],
  },
];

const PapersPage: React.FC = () => {
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  const [showCiteModal, setShowCiteModal] = useState(false);

  const handleCite = (paper: Paper) => {
    setSelectedPaper(paper);
    setShowCiteModal(true);
  };

  const getCitation = (paper: Paper): Citation => ({
    key: paper.bibtexKey,
    title: paper.title,
    authors: paper.authors,
    booktitle: paper.venue,
    year: paper.year,
    doi: paper.doi,
    url: paper.arxiv ? `https://arxiv.org/abs/${paper.arxiv}` : undefined,
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
    >
      {/* Hero Section */}
      <section className="text-center mb-12">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring' }}
          className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-slate-100 dark:bg-slate-900/30 mb-4"
        >
          <FileText className="w-8 h-8 text-slate-600" />
        </motion.div>
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Publications
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
          Academic papers and research publications related to the VULCA framework
          for cross-cultural AI art understanding.
        </p>
      </section>

      {/* Data Provenance */}
      <section className="mb-12">
        <ProvenanceCard
          source="VULCA Research"
          version={VULCA_VERSION.framework}
          lastUpdated={VULCA_VERSION.lastUpdated}
          license="Academic Use"
          doi="10.18653/v1/2025.findings-emnlp.103"
          github="https://github.com/vulca-org/vulca"
        />
      </section>

      {/* Featured Papers */}
      <section className="mb-12">
        <div className="flex items-center gap-3 mb-6">
          <Award className="w-6 h-6 text-yellow-500" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Featured Papers
          </h2>
        </div>

        <div className="space-y-6">
          {papers
            .filter(p => p.featured)
            .map((paper, index) => (
              <motion.div
                key={paper.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <IOSCard variant="elevated" className="border-l-4 border-yellow-500">
                  <IOSCardContent className="p-6">
                    <div className="flex items-start justify-between gap-4 mb-4">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                          {paper.title}
                        </h3>
                        <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mb-2">
                          <span className="flex items-center gap-1">
                            <Users className="w-4 h-4" />
                            {paper.authors.slice(0, 2).join(', ')}
                            {paper.authors.length > 2 && ' et al.'}
                          </span>
                          <span className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            {paper.venue}, {paper.year}
                          </span>
                        </div>
                      </div>
                      <span className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 rounded-full text-xs font-medium">
                        Featured
                      </span>
                    </div>

                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-4">
                      {paper.abstract}
                    </p>

                    <div className="flex flex-wrap gap-2 mb-4">
                      {paper.tags.map(tag => (
                        <span
                          key={tag}
                          className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs text-gray-600 dark:text-gray-400"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <IOSButton
                        variant="primary"
                        size="sm"
                        onClick={() => handleCite(paper)}
                      >
                        <BookOpen className="w-4 h-4 mr-1" />
                        Cite
                      </IOSButton>
                      {paper.arxiv && (
                        <IOSButton
                          variant="secondary"
                          size="sm"
                          onClick={() => window.open(`https://arxiv.org/abs/${paper.arxiv}`, '_blank')}
                        >
                          <ExternalLink className="w-4 h-4 mr-1" />
                          arXiv
                        </IOSButton>
                      )}
                      {paper.github && (
                        <IOSButton
                          variant="secondary"
                          size="sm"
                          onClick={() => window.open(paper.github, '_blank')}
                        >
                          <Github className="w-4 h-4 mr-1" />
                          Code
                        </IOSButton>
                      )}
                      {paper.demo && (
                        <IOSButton
                          variant="secondary"
                          size="sm"
                          onClick={() => window.open(paper.demo, '_blank')}
                        >
                          <Globe className="w-4 h-4 mr-1" />
                          Demo
                        </IOSButton>
                      )}
                    </div>
                  </IOSCardContent>
                </IOSCard>
              </motion.div>
            ))}
        </div>
      </section>

      {/* All Papers */}
      <section>
        <div className="flex items-center gap-3 mb-6">
          <FileText className="w-6 h-6 text-gray-500" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            All Papers
          </h2>
        </div>

        <div className="space-y-4">
          {papers
            .filter(p => !p.featured)
            .map((paper, index) => (
              <motion.div
                key={paper.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <IOSCard variant="flat" className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                  <IOSCardContent className="p-4">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                      {paper.title}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mb-3">
                      <span>
                        {paper.authors.slice(0, 2).join(', ')}
                        {paper.authors.length > 2 && ' et al.'}
                      </span>
                      <span>{paper.venue}, {paper.year}</span>
                    </div>

                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
                      {paper.abstract}
                    </p>

                    <div className="flex flex-wrap gap-2">
                      <IOSButton
                        variant="text"
                        size="sm"
                        onClick={() => handleCite(paper)}
                      >
                        <BookOpen className="w-4 h-4 mr-1" />
                        Cite
                      </IOSButton>
                      {paper.arxiv && (
                        <IOSButton
                          variant="text"
                          size="sm"
                          onClick={() => window.open(`https://arxiv.org/abs/${paper.arxiv}`, '_blank')}
                        >
                          <ExternalLink className="w-4 h-4 mr-1" />
                          arXiv
                        </IOSButton>
                      )}
                      {paper.github && (
                        <IOSButton
                          variant="text"
                          size="sm"
                          onClick={() => window.open(paper.github, '_blank')}
                        >
                          <Github className="w-4 h-4 mr-1" />
                          Code
                        </IOSButton>
                      )}
                      {paper.demo && (
                        <IOSButton
                          variant="text"
                          size="sm"
                          onClick={() => window.open(paper.demo, '_blank')}
                        >
                          <Globe className="w-4 h-4 mr-1" />
                          Demo
                        </IOSButton>
                      )}
                    </div>
                  </IOSCardContent>
                </IOSCard>
              </motion.div>
            ))}
        </div>
      </section>

      {/* Citation Modal */}
      {selectedPaper && (
        <CiteModal
          citation={getCitation(selectedPaper)}
          visible={showCiteModal}
          onClose={() => {
            setShowCiteModal(false);
            setSelectedPaper(null);
          }}
        />
      )}
    </motion.div>
  );
};

export default PapersPage;
