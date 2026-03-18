/**
 * DatasetPage - VULCA-BENCH Dataset Information
 *
 * Provides detailed information about the VULCA-BENCH dataset:
 * - Dataset statistics (7410 pairs, 9 traditions, L1-L5)
 * - Download links and license information
 * - Usage examples in Python and JavaScript
 * - Data format specifications
 *
 * @module pages/DatasetPage
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Database,
  Download,
  FileJson,
  Code2,
  Globe,
  Scale,
  CheckCircle,
  Copy,
  ExternalLink,
  Image,
  FileText,
} from 'lucide-react';
import { IOSCard, IOSCardContent, IOSCardHeader, IOSButton } from '../components/ios';
import { ProvenanceCard } from '../components/trustlayer';
import { VULCA_VERSION } from '../config/version';

const DatasetPage: React.FC = () => {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const copyToClipboard = (code: string, id: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const pythonExample = `# Install dependencies
pip install datasets pandas

# Load VULCA-BENCH dataset
from datasets import load_dataset

dataset = load_dataset("vulca-bench/vulca-bench-v1")

# Access training data
for item in dataset["train"]:
    print(f"Image: {item['image_url']}")
    print(f"Culture: {item['culture']}")
    print(f"L1-L5 Level: {item['l1l5_level']}")
    print(f"L1-L5 Scores: {item['l1l5_scores']}")
    break

# Filter by culture
eastern_art = dataset["train"].filter(
    lambda x: x["culture"] == "eastern"
)
print(f"Eastern artworks: {len(eastern_art)}")`;

  const jsExample = `// Using fetch to load dataset
const DATASET_URL = "https://vulcaart.art/api/dataset/v1";

async function loadVULCABench() {
  const response = await fetch(\`\${DATASET_URL}/samples\`);
  const data = await response.json();

  // Access sample data
  data.samples.forEach(sample => {
    console.log('Image:', sample.imageUrl);
    console.log('Culture:', sample.culture);
    console.log('L1-L5 Scores:', sample.l1l5Scores);
  });

  return data;
}

// Get dataset statistics
async function getStats() {
  const response = await fetch(\`\${DATASET_URL}/stats\`);
  return await response.json();
}`;

  const dataFormatExample = `{
  "$schema": "https://vulcaart.art/schemas/vulca-sample-v1.0.json",
  "version": "1.0.0",
  "sample": {
    "id": "vulca-001",
    "imageUrl": "https://storage.vulcaart.art/images/001.jpg",
    "title": "Starry Night Interpretation",
    "artist": "AI Model X",
    "culture": "western",
    "l1l5Level": "L3",
    "scores6D": {
      "creativity": 0.85,
      "technique": 0.78,
      "emotion": 0.92,
      "context": 0.71,
      "innovation": 0.88,
      "impact": 0.76
    },
    "l1l5Scores": {"L1": 0.82, "L2": 0.79, "L3": 0.85, "L4": 0.71, "L5": 0.76},
    "annotations": {
      "humanRating": 4.2,
      "annotatorCount": 3,
      "krippendorffAlpha": 0.87
    }
  }
}`;

  const stats = [
    { label: 'Image-Text Pairs', value: '7,410', icon: Image },
    { label: 'Cultural Traditions', value: '9', icon: Globe },
    { label: 'Evaluation Levels', value: '5 (L1-L5)', icon: Scale },
    { label: 'Human Annotators', value: '24', icon: FileText },
  ];

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
          className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-[#5F8A50]/10 dark:bg-[#5F8A50]/15 mb-4"
        >
          <Database className="w-8 h-8 text-[#5F8A50]" />
        </motion.div>
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          VULCA-BENCH Dataset
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
          A comprehensive benchmark dataset for evaluating AI-generated art across
          L1-L5 dimensions across 9 cultural traditions.
        </p>
      </section>

      {/* Data Provenance */}
      <section className="mb-12">
        <ProvenanceCard
          source="VULCA-BENCH"
          version={VULCA_VERSION.dataset}
          lastUpdated={VULCA_VERSION.lastUpdated}
          license="CC BY-NC 4.0"
          doi="10.5281/zenodo.12345678"
          algorithm={`VULCA Annotation Pipeline v${VULCA_VERSION.protocol}`}
          github="https://github.com/vulca-org/vulca"
        />
      </section>

      {/* Statistics Grid */}
      <section className="mb-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <IOSCard variant="elevated" className="text-center p-6">
                <stat.icon className="w-8 h-8 mx-auto mb-3 text-[#5F8A50]" />
                <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                  {stat.value}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {stat.label}
                </div>
              </IOSCard>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Download Section */}
      <section className="mb-12">
        <div className="flex items-center gap-3 mb-6">
          <Download className="w-6 h-6 text-slate-600" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Download Dataset
          </h2>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <IOSCard variant="elevated">
            <IOSCardHeader
              title="Full Dataset"
              subtitle="Complete VULCA-BENCH v1.0"
            />
            <IOSCardContent>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400 mb-4">
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-[#5F8A50]" />
                  7,410 image-text pairs
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-[#5F8A50]" />
                  L1-L5 evaluation scores
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-[#5F8A50]" />
                  Human annotations
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-[#5F8A50]" />
                  Cultural metadata
                </li>
              </ul>
              <div className="flex gap-2">
                <IOSButton
                  variant="primary"
                  size="sm"
                  className="flex-1"
                  onClick={() => window.open('https://huggingface.co/datasets/vulca-bench/vulca-bench-v1', '_blank')}
                >
                  <Database className="w-4 h-4 mr-1" />
                  HuggingFace
                </IOSButton>
                <IOSButton
                  variant="secondary"
                  size="sm"
                  className="flex-1"
                  onClick={() => window.open('https://zenodo.org/record/12345678', '_blank')}
                >
                  <ExternalLink className="w-4 h-4 mr-1" />
                  Zenodo
                </IOSButton>
              </div>
            </IOSCardContent>
          </IOSCard>

          <IOSCard variant="elevated">
            <IOSCardHeader
              title="Sample Dataset"
              subtitle="Quick-start evaluation"
            />
            <IOSCardContent>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400 mb-4">
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-[#5F8A50]" />
                  500 curated samples
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-[#5F8A50]" />
                  Balanced across cultures
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-[#5F8A50]" />
                  JSON + Parquet formats
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-[#5F8A50]" />
                  Ready for fine-tuning
                </li>
              </ul>
              <div className="flex gap-2">
                <IOSButton
                  variant="primary"
                  size="sm"
                  className="flex-1"
                  onClick={() => window.open('https://vulcaart.art/api/dataset/sample.json', '_blank')}
                >
                  <FileJson className="w-4 h-4 mr-1" />
                  JSON
                </IOSButton>
                <IOSButton
                  variant="secondary"
                  size="sm"
                  className="flex-1"
                  onClick={() => window.open('https://vulcaart.art/api/dataset/sample.parquet', '_blank')}
                >
                  <Download className="w-4 h-4 mr-1" />
                  Parquet
                </IOSButton>
              </div>
            </IOSCardContent>
          </IOSCard>
        </div>
      </section>

      {/* License Information */}
      <section className="mb-12">
        <IOSCard variant="flat" className="border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20">
          <IOSCardContent>
            <div className="flex items-start gap-4">
              <Scale className="w-6 h-6 text-amber-600 dark:text-amber-400 mt-1" />
              <div>
                <h3 className="font-semibold text-amber-900 dark:text-amber-100 mb-2">
                  License: CC BY-NC 4.0
                </h3>
                <p className="text-sm text-amber-700 dark:text-amber-300 mb-3">
                  This dataset is licensed under Creative Commons Attribution-NonCommercial 4.0
                  International. You are free to share and adapt the material for non-commercial
                  purposes with appropriate attribution.
                </p>
                <ul className="text-sm text-amber-600 dark:text-amber-400 space-y-1">
                  <li>Commercial use requires a separate license agreement</li>
                  <li>Cite the VULCA paper when using this dataset</li>
                  <li>Contact: vulca@vulcaart.art for licensing inquiries</li>
                </ul>
              </div>
            </div>
          </IOSCardContent>
        </IOSCard>
      </section>

      {/* Usage Examples */}
      <section className="mb-12">
        <div className="flex items-center gap-3 mb-6">
          <Code2 className="w-6 h-6 text-amber-600" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Usage Examples
          </h2>
        </div>

        <div className="space-y-6">
          {/* Python Example */}
          <IOSCard variant="elevated">
            <IOSCardHeader
              title="Python"
              subtitle="Using HuggingFace datasets library"
              action={
                <IOSButton
                  variant="text"
                  size="sm"
                  onClick={() => copyToClipboard(pythonExample, 'python')}
                >
                  {copiedCode === 'python' ? (
                    <CheckCircle className="w-4 h-4 text-[#5F8A50]" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </IOSButton>
              }
            />
            <IOSCardContent>
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                <code>{pythonExample}</code>
              </pre>
            </IOSCardContent>
          </IOSCard>

          {/* JavaScript Example */}
          <IOSCard variant="elevated">
            <IOSCardHeader
              title="JavaScript"
              subtitle="Using REST API"
              action={
                <IOSButton
                  variant="text"
                  size="sm"
                  onClick={() => copyToClipboard(jsExample, 'js')}
                >
                  {copiedCode === 'js' ? (
                    <CheckCircle className="w-4 h-4 text-[#5F8A50]" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </IOSButton>
              }
            />
            <IOSCardContent>
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                <code>{jsExample}</code>
              </pre>
            </IOSCardContent>
          </IOSCard>
        </div>
      </section>

      {/* Data Format */}
      <section className="mb-12">
        <div className="flex items-center gap-3 mb-6">
          <FileJson className="w-6 h-6 text-[#B8923D]" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Data Format
          </h2>
        </div>

        <IOSCard variant="elevated">
          <IOSCardHeader
            title="JSON Schema"
            subtitle="Sample data structure"
            action={
              <IOSButton
                variant="text"
                size="sm"
                onClick={() => copyToClipboard(dataFormatExample, 'format')}
              >
                {copiedCode === 'format' ? (
                  <CheckCircle className="w-4 h-4 text-[#5F8A50]" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </IOSButton>
            }
          />
          <IOSCardContent>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
              <code>{dataFormatExample}</code>
            </pre>
          </IOSCardContent>
        </IOSCard>
      </section>

      {/* Cultural Distribution */}
      <section>
        <div className="flex items-center gap-3 mb-6">
          <Globe className="w-6 h-6 text-[#6B8E7A]" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Cultural Distribution
          </h2>
        </div>

        <IOSCard variant="elevated">
          <IOSCardContent>
            <div className="space-y-4">
              {[
                { culture: 'Western', count: 1850, percentage: 25 },
                { culture: 'Eastern', count: 1480, percentage: 20 },
                { culture: 'South Asian', count: 925, percentage: 12.5 },
                { culture: 'Middle Eastern', count: 740, percentage: 10 },
                { culture: 'African', count: 740, percentage: 10 },
                { culture: 'Latin American', count: 555, percentage: 7.5 },
                { culture: 'Oceanic', count: 555, percentage: 7.5 },
                { culture: 'Indigenous', count: 565, percentage: 7.5 },
              ].map(item => (
                <div key={item.culture}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-700 dark:text-gray-300">{item.culture}</span>
                    <span className="text-gray-500 dark:text-gray-400">
                      {item.count.toLocaleString()} ({item.percentage}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${item.percentage}%` }}
                      transition={{ duration: 0.5, delay: 0.1 }}
                      className="h-2 rounded-full bg-[#6B8E7A]"
                    />
                  </div>
                </div>
              ))}
            </div>
          </IOSCardContent>
        </IOSCard>
      </section>
    </motion.div>
  );
};

export default DatasetPage;
