/**
 * Organization Colors Constants
 * Centralized color definitions for AI organizations
 * Used across charts, leaderboards, and visualizations
 */

export const ORGANIZATION_COLORS: Record<string, string> = {
  // Major AI Labs - Primary
  'OpenAI': '#10b981',
  'Anthropic': '#d97757',
  'Google': '#334155',
  'Meta': '#475569',
  'Microsoft': '#6B8E7A',

  // Chinese AI Labs
  'Alibaba': '#ff6900',
  'Baidu': '#334155',
  'Tencent': '#5F8A50',
  'ByteDance': '#fe2c55',
  'Moonshot': '#B8923D',
  'Zhipu': '#C87F4A',
  'Zhipu AI': '#C87F4A',
  'MiniMax': '#f59e0b',
  'Minimax': '#f59e0b',
  'iFlytek': '#0891b2',
  'iFLYTEK': '#0891b2',
  'DeepSeek': '#334155',
  'SenseTime': '#0ea5e9',
  '01.AI': '#f43f5e',
  'Kunlun': '#84cc16',

  // International Labs
  'Mistral': '#FF6B35',
  'xAI': '#1D1D1F',
  'Stability AI': '#C87F4A',
  'Midjourney': '#8F7030',
  'Cohere': '#06b6d4',
  'AI21': '#C65D4D',
  'Hugging Face': '#fbbf24',
  'Together AI': '#14b8a6',
};

// Default color for unknown organizations
export const DEFAULT_ORG_COLOR = '#6b7280';

/**
 * Get color for an organization
 * Falls back to default gray if organization not found
 */
export function getOrganizationColor(org: string): string {
  return ORGANIZATION_COLORS[org] || DEFAULT_ORG_COLOR;
}

/**
 * Get all organization names
 */
export function getAllOrganizations(): string[] {
  return Object.keys(ORGANIZATION_COLORS);
}

/**
 * Check if an organization has a defined color
 */
export function hasOrganizationColor(org: string): boolean {
  return org in ORGANIZATION_COLORS;
}
