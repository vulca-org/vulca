/**
 * Prerender script for VULCA marketing pages
 * Generates static HTML with proper meta tags for SEO
 */

import { renderToString } from 'react-dom/server';
import { PrerenderPage } from './prerender/PrerenderPage';

// Page-specific SEO data
const pagesSEO: Record<string, { title: string; description: string; keywords: string }> = {
  '/': {
    title: 'VULCA - AI-Native Creation Organism',
    description: 'Create, critique, and evolve cultural art through multi-agent AI pipelines.',
    keywords: 'AI creation, cultural AI, art creation, AI benchmark, VULCA',
  },
  '/canvas': {
    title: 'Canvas - VULCA',
    description: 'Unified creation and evaluation workspace with Scout, Draft, Critic, and Queen AI agents.',
    keywords: 'AI canvas, art creation, AI pipeline, cultural creation',
  },
  '/gallery': {
    title: 'Gallery - VULCA',
    description: 'Community gallery of AI-created cultural artworks. Like, fork, and evolve creations.',
    keywords: 'AI gallery, art gallery, community art, cultural art',
  },
  '/research': {
    title: 'Research - VULCA',
    description: 'L1-L5 cognitive framework, 6D to 47D evaluation, methodology, dataset, and publications.',
    keywords: 'VULCA research, methodology, dataset, EMNLP 2025, cultural AI',
  },
  '/models': {
    title: 'Models - VULCA',
    description: '42+ AI models evaluated across 47 dimensions. Compare GPT, Claude, Gemini, and more.',
    keywords: 'AI models, model comparison, GPT, Claude, AI ranking',
  },
};

// Prerender function called by vite-prerender-plugin
export async function prerender(data: { url: string }) {
  const url = data.url || '/';
  const seo = pagesSEO[url] || pagesSEO['/'];

  const html = renderToString(<PrerenderPage seo={seo} />);

  // Return all marketing routes to prerender
  const links = new Set(Object.keys(pagesSEO));

  return {
    html,
    links,
    head: {
      lang: 'en',
      title: seo.title,
      elements: new Set([
        { type: 'meta', props: { name: 'description', content: seo.description } },
        { type: 'meta', props: { name: 'keywords', content: seo.keywords } },
        { type: 'meta', props: { property: 'og:title', content: seo.title } },
        { type: 'meta', props: { property: 'og:description', content: seo.description } },
        { type: 'meta', props: { property: 'og:type', content: 'website' } },
        { type: 'meta', props: { property: 'og:url', content: `https://vulcaart.art${url}` } },
        { type: 'meta', props: { name: 'twitter:title', content: seo.title } },
        { type: 'meta', props: { name: 'twitter:description', content: seo.description } },
        { type: 'link', props: { rel: 'canonical', href: `https://vulcaart.art${url}` } },
      ]),
    },
  };
}
