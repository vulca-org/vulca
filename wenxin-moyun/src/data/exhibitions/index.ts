/**
 * Exhibitions Data Module
 *
 * Exports exhibition data and utilities for the VULCA Art Platform
 * Supports multiple exhibitions:
 * - Echoes and Returns (回响与归来)
 * - Negative Space of the Tide (潮汐的负形)
 * - Northeast Asia Memory (东北亚记忆)
 *
 * @updated 2026-02-05 - Added Northeast Asia Memory exhibition
 */

// Echoes and Returns exports
export {
  EXHIBITION_ID,
  EXHIBITION_INFO,
  CHAPTERS,
  transformArtwork,
  groupByChapter,
  buildExhibition,
} from './echoes-and-returns';

export type { RawArtwork } from './echoes-and-returns';

// Negative Space of the Tide — lightweight metadata only (heavy data loaded on-demand)
export {
  NEGATIVE_SPACE_ID,
  NEGATIVE_SPACE_INFO,
  NEGATIVE_SPACE_THEME,
} from './negative-space';

// Northeast Asia Memory exports
export {
  NORTHEAST_ASIA_ID,
  NORTHEAST_ASIA_INFO,
  NORTHEAST_ASIA_CHAPTERS,
  buildNortheastAsiaExhibition,
} from './northeast-asia';

export type { NortheastAsiaRawArtwork } from './northeast-asia';

// Re-export types for convenience
export type {
  Exhibition,
  Chapter,
  Artwork,
  Artist,
  Dialogue,
  DialogueTurn,
  DialogueParticipant,
  ExhibitionFilters,
  ArtworkListItem,
  // Multi-exhibition types
  ArtworkFlat,
  ArtworkImage,
  ArtworkMetadata,
  Persona,
  Critique,
  RPAITScores,
  RPAITDimension,
  ExhibitionTheme,
} from '../../types/exhibition';

export { RPAIT_LABELS, RPAIT_COLORS } from '../../types/exhibition';

// Static JSON data paths
export const ECHOES_DATA_URL = '/data/echoes-and-returns.json';
export const NORTHEAST_ASIA_DATA_URL = '/data/northeast-asia.json';
export const NORTHEAST_ASIA_DIALOGUES_URL = '/data/northeast-dialogues.json';

// Exhibition IDs
export const EXHIBITION_IDS = {
  ECHOES_AND_RETURNS: 'echoes-and-returns',
  NEGATIVE_SPACE: 'negative-space-of-the-tide',
  NORTHEAST_ASIA: 'northeast-asia-memory',
} as const;

// All exhibitions metadata for listing
export const ALL_EXHIBITIONS = [
  {
    id: 'echoes-and-returns',
    name: 'Echoes and Returns',
    name_zh: '回响与归来',
    description: 'A contemporary art exhibition exploring themes of cultural transmission, innovation, resonance, and identity through 87 artworks.',
    description_zh: '一场当代艺术展览，通过87件作品探索文化传承、创新、共鸣与身份认同的主题。',
    cover_image: '/data/exhibitions/echoes-cover.jpg',
    artworks_count: 87,
    status: 'live' as const,
    has_chapters: true,
    has_dialogues: true,
    has_rpait: false,
  },
  {
    id: 'negative-space-of-the-tide',
    name: 'Negative Space of the Tide',
    name_zh: '潮汐的负形',
    description: 'An in-depth dialogue on AI and artistic creation, exploring the nature of machine creativity through the perspectives of 6 critics from diverse cultural backgrounds.',
    description_zh: '一场关于人工智能与艺术创作的深度对话，通过6位来自不同文化背景的评论家视角，探索机器创造力的本质。',
    cover_image: '/exhibitions/negative-space/cover.jpg',
    artworks_count: 43,
    status: 'live' as const,
    has_chapters: false,
    has_dialogues: false,
    has_rpait: true,
    theme: {
      primaryColor: '#B85C3C',
      accentColor: '#D4A574',
    },
  },
  {
    id: 'northeast-asia-memory',
    name: 'Northeast Asia Memory',
    name_zh: '东北亚记忆',
    description: 'An exhibition exploring memory, identity, displacement, and sensory experience across Northeast Asia through 18 artworks by artists from China, Japan, Korea, and the UK.',
    description_zh: '一场跨越东北亚的展览，通过来自中国、日本、韩国与英国的18位艺术家作品，探索记忆、身份、流动与感官体验。',
    cover_image: '/data/exhibitions/northeast-asia/image_01.png',
    artworks_count: 18,
    status: 'live' as const,
    has_chapters: true,
    has_dialogues: true,
    has_rpait: false,
  },
] as const;

export type ExhibitionId = typeof EXHIBITION_IDS[keyof typeof EXHIBITION_IDS];

