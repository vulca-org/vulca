/**
 * SEO Configuration
 *
 * Centralized SEO metadata for all pages.
 * Used for dynamic meta tag updates and structured data.
 *
 * @module config/seo
 */

import { VULCA_VERSION } from './version';

export interface PageSEO {
  title: string;
  description: string;
  keywords?: string[];
  ogImage?: string;
  canonicalPath?: string;
  structuredData?: object;
}

export const DEFAULT_SEO: PageSEO = {
  title: 'VULCA - AI-Native Creation Organism',
  description: 'L1-L5 evaluation across 9 cultural traditions. Reproducible benchmarking for AI art and culture understanding.',
  keywords: ['AI evaluation', 'cultural AI', 'VLM benchmark', 'art understanding', 'VULCA'],
  ogImage: '/og-image.png',
};

export const PAGE_SEO: Record<string, PageSEO> = {
  '/': {
    title: 'VULCA - AI-Native Creation Organism',
    description: 'Create, critique, and evolve cultural art through multi-agent AI pipelines. Canvas-first creation with Scout, Draft, Critic, and Queen agents.',
    keywords: ['AI creation', 'cultural AI', 'art creation', 'VULCA', 'AI pipeline'],
  },
  '/canvas': {
    title: 'Canvas - VULCA',
    description: 'Unified creation and evaluation workspace. Create cultural art with AI agents — Scout, Draft, Critic, and Queen collaborate in real-time.',
    keywords: ['AI canvas', 'art creation', 'AI pipeline', 'cultural creation', 'VULCA canvas'],
  },
  '/gallery': {
    title: 'Gallery - VULCA',
    description: 'Community gallery of AI-created cultural artworks. Like, fork, and evolve creations from the VULCA community.',
    keywords: ['AI gallery', 'art gallery', 'community art', 'cultural art', 'VULCA gallery'],
  },
  '/research': {
    title: 'Research - VULCA',
    description: 'VULCA research: L1-L5 cognitive framework, evaluation methodology, 9 cultural traditions, dataset, and publications.',
    keywords: ['VULCA research', 'methodology', 'dataset', 'EMNLP 2025', 'cultural AI evaluation'],
  },
  '/models': {
    title: 'Models - VULCA',
    description: 'AI models evaluated on cultural understanding. Compare GPT-4V, Claude, Gemini and more across L1-L5 dimensions.',
    keywords: ['AI models', 'model comparison', 'VLM ranking', 'benchmark results'],
  },
};

/**
 * Update document meta tags
 */
export function updatePageMeta(path: string): void {
  const seo = PAGE_SEO[path] || DEFAULT_SEO;

  // Update title
  document.title = seo.title;

  // Update meta description
  let metaDescription = document.querySelector('meta[name="description"]');
  if (!metaDescription) {
    metaDescription = document.createElement('meta');
    metaDescription.setAttribute('name', 'description');
    document.head.appendChild(metaDescription);
  }
  metaDescription.setAttribute('content', seo.description);

  // Update OG tags
  const ogTags = {
    'og:title': seo.title,
    'og:description': seo.description,
    'og:url': `https://vulcaart.art${path}`,
    'og:image': seo.ogImage || DEFAULT_SEO.ogImage,
  };

  Object.entries(ogTags).forEach(([property, content]) => {
    let meta = document.querySelector(`meta[property="${property}"]`);
    if (!meta) {
      meta = document.createElement('meta');
      meta.setAttribute('property', property);
      document.head.appendChild(meta);
    }
    meta.setAttribute('content', content || '');
  });

  // Update Twitter tags
  const twitterTags = {
    'twitter:title': seo.title,
    'twitter:description': seo.description,
  };

  Object.entries(twitterTags).forEach(([name, content]) => {
    let meta = document.querySelector(`meta[name="${name}"]`);
    if (!meta) {
      meta = document.createElement('meta');
      meta.setAttribute('name', name);
      document.head.appendChild(meta);
    }
    meta.setAttribute('content', content || '');
  });
}

/**
 * Generate JSON-LD structured data for the organization
 */
export function getOrganizationStructuredData(): object {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'VULCA',
    url: 'https://vulcaart.art',
    logo: 'https://vulcaart.art/logo.png',
    description: 'AI-Native Creation Organism',
    sameAs: [
      'https://github.com/vulca-org/vulca',
      'https://twitter.com/vulca_ai',
    ],
  };
}

/**
 * Generate JSON-LD structured data for the software application
 */
export function getSoftwareApplicationStructuredData(): object {
  return {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: 'VULCA',
    applicationCategory: 'AI Evaluation Tool',
    operatingSystem: 'Web',
    offers: {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'USD',
      description: 'Free public demo available',
    },
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: '4.8',
      ratingCount: String(VULCA_VERSION.totalModels),
    },
  };
}

/**
 * Generate JSON-LD structured data for the dataset
 */
export function getDatasetStructuredData(): object {
  return {
    '@context': 'https://schema.org',
    '@type': 'Dataset',
    name: 'VULCA-BENCH',
    description: 'A Multicultural Vision-Language Benchmark for Culturally Grounded Art Understanding',
    url: 'https://vulcaart.art/research',
    license: 'https://creativecommons.org/licenses/by-nc/4.0/',
    creator: {
      '@type': 'Organization',
      name: 'VULCA Team',
    },
    distribution: {
      '@type': 'DataDownload',
      encodingFormat: 'JSON',
      contentUrl: 'https://vulcaart.art/dataset/download',
    },
    variableMeasured: [
      'L1-L5 evaluation dimensions',
      '9 cultural traditions',
      '7,410 image-text pairs',
    ],
  };
}

export default {
  updatePageMeta,
  getOrganizationStructuredData,
  getSoftwareApplicationStructuredData,
  getDatasetStructuredData,
  PAGE_SEO,
  DEFAULT_SEO,
};
