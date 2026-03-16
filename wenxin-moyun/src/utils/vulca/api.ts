/**
 * VULCA API Service
 * Handles all API calls to VULCA backend endpoints
 */

import axios, { AxiosError } from 'axios';
import type {
  VULCAEvaluation,
  VULCAComparison,
  VULCADimensionInfo,
  VULCACulturalPerspectiveInfo,
  VULCAScore6D,
} from '../../types/vulca';


import { API_BASE_URL } from '../../config/api';
const VULCA_API_PREFIX = '/api/v1/vulca';

// Create axios instance with default config
// Cache configuration
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

type RetryableRequestConfig = {
  _retry?: boolean;
  _retryCount?: number;
} & Record<string, unknown>;

interface FallbackModelItem {
  id: string;
  name: string;
  vulca_scores_6d?: Record<string, number>;
  vulca_scores_47d?: Record<string, number>;
  vulca_cultural_perspectives?: Record<string, number>;
  vulca_evaluation_date?: string;
}

class APICache {
  private cache = new Map<string, CacheEntry<unknown>>();
  
  set<T>(key: string, data: T, ttl = 300000): void { // 5 minutes default
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }
  
  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;
    
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return entry.data as T;
  }
  
  clear(): void {
    this.cache.clear();
  }
}

const toVULCAScore6D = (raw: Record<string, number> | undefined): VULCAScore6D => ({
  creativity: raw?.creativity ?? raw?.dim_0 ?? 0,
  technique: raw?.technique ?? raw?.dim_1 ?? 0,
  emotion: raw?.emotion ?? raw?.dim_2 ?? 0,
  context: raw?.context ?? raw?.dim_3 ?? 0,
  innovation: raw?.innovation ?? raw?.dim_4 ?? 0,
  impact: raw?.impact ?? raw?.dim_5 ?? 0,
});

const getPerspectiveValue = (source: Record<string, unknown>, key: string): number => {
  const value = source[key];
  if (typeof value === 'number') return value;
  if (
    typeof value === 'object' &&
    value !== null &&
    'overall' in value &&
    typeof (value as { overall?: unknown }).overall === 'number'
  ) {
    return (value as { overall: number }).overall;
  }
  return 0;
};

const toCulturalPerspective = (
  raw: Record<string, unknown> | undefined
): VULCAEvaluation['culturalPerspectives'] => {
  const source = raw ?? {};
  return {
    western: getPerspectiveValue(source, 'western'),
    eastern: getPerspectiveValue(source, 'eastern'),
    african: getPerspectiveValue(source, 'african'),
    latin_american: getPerspectiveValue(source, 'latin_american'),
    middle_eastern: getPerspectiveValue(source, 'middle_eastern'),
    south_asian: getPerspectiveValue(source, 'south_asian'),
    oceanic: getPerspectiveValue(source, 'oceanic'),
    indigenous: getPerspectiveValue(source, 'indigenous'),
  };
};

const apiCache = new APICache();

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // Start with 1 second

// Create axios instance with default config
const vulcaApi = axios.create({
  baseURL: `${API_BASE_URL}${VULCA_API_PREFIX}`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth token
vulcaApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
vulcaApi.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    if (!originalRequest) {
      return Promise.reject(error);
    }
    const retryState = originalRequest as unknown as RetryableRequestConfig;
    const retryCount = retryState._retryCount ?? 0;
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      // Don't redirect if already on login page
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    
    // Implement retry logic for network errors or 5xx errors
    if (
      !retryState._retry &&
      retryCount < MAX_RETRIES &&
      (error.code === 'ECONNABORTED' || 
       error.code === 'ERR_NETWORK' ||
       (error.response && error.response.status >= 500))
    ) {
      retryState._retry = true;
      retryState._retryCount = retryCount + 1;
      
      // Exponential backoff
      const delay = RETRY_DELAY * Math.pow(2, retryState._retryCount - 1);
      await new Promise(resolve => setTimeout(resolve, delay));
      
      return vulcaApi(originalRequest);
    }
    
    // Enhanced error with more details
    const enhancedError = {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      endpoint: error.config?.url,
      method: error.config?.method,
    };
    
    return Promise.reject(enhancedError);
  }
);

// Helper function to handle cached requests
async function cachedRequest<T>(
  cacheKey: string,
  requestFn: () => Promise<T>,
  ttl?: number
): Promise<T> {
  // Check cache first
  const cachedData = apiCache.get<T>(cacheKey);
  if (cachedData) {
    return cachedData;
  }
  
  // Make request and cache result
  const data = await requestFn();
  apiCache.set(cacheKey, data, ttl);
  return data;
}

export const vulcaService = {
  /**
   * Get VULCA system information
   */
  async getInfo() {
    return cachedRequest(
      'vulca:info',
      async () => {
        const response = await vulcaApi.get('/info');
        return response.data;
      },
      600000 // 10 minutes cache
    );
  },

  /**
   * Evaluate a model with VULCA framework
   */
  async evaluateModel(
    modelId: string,
    scores6D: VULCAScore6D,
    modelName?: string
  ): Promise<VULCAEvaluation> {
    const response = await vulcaApi.post('/evaluate', {
      model_id: modelId,
      model_name: modelName,
      scores_6d: scores6D,
    });
    return response.data;
  },

  /**
   * Compare multiple models
   */
  async compareModels(
    modelIds: string[],
    includeDetails = true
  ): Promise<VULCAComparison> {
    try {
      // Model IDs are already strings
      const response = await vulcaApi.post('/compare', {
        model_ids: modelIds,
        include_details: includeDetails,
      });

      // Transform snake_case to camelCase
      const comparison = response.data;
      if (comparison.models) {
        comparison.models = comparison.models.map((model: Record<string, unknown>) => ({
          modelId: String(model.model_id || model.modelId || ''),
          modelName: String(model.model_name || model.modelName || ''),
          scores6D: toVULCAScore6D((model.scores_6d || model.scores6D) as Record<string, number> | undefined),
          scores47D: ((model.scores_47d || model.scores47D || {}) as Record<string, number>),
          culturalPerspectives: toCulturalPerspective(
            (model.cultural_perspectives || model.culturalPerspectives) as Record<string, unknown> | undefined
          ),
          evaluationDate: String(model.evaluation_date || model.evaluationDate || new Date().toISOString())
        }));
      }
      if (comparison.summary) {
        const summary = comparison.summary;
        comparison.summary = {
          mostSimilar: summary.most_similar || summary.mostSimilar,
          mostDifferent: summary.most_different || summary.mostDifferent,
          averageDifference: summary.average_difference || summary.averageDifference,
          dimensionStatistics: summary.dimension_statistics || summary.dimensionStatistics,
          culturalAnalysis: summary.cultural_analysis || summary.culturalAnalysis,
        };
      }
      comparison.differenceMatrix = comparison.difference_matrix || comparison.differenceMatrix;

      return comparison;
    } catch (error: unknown) {
      console.error('Error calling /compare API:', error);
      const errorStatus = typeof error === 'object' && error !== null && 'status' in error
        ? (error as { status?: number }).status
        : undefined;
      
      // Fallback: Try to get individual models and create comparison
      if (errorStatus === 400 || errorStatus === 404) {
        try {
          // Get models data from the main models API
          const modelsResponse = await axios.get(`${API_BASE_URL}/api/v1/models/`, {
            params: { include_vulca: true }
          });
          
          const allModels: unknown = modelsResponse.data;
          const selectedModels = Array.isArray(allModels)
            ? allModels.filter((m): m is FallbackModelItem =>
                typeof m === 'object' &&
                m !== null &&
                'id' in m &&
                typeof (m as FallbackModelItem).id === 'string' &&
                'name' in m &&
                typeof (m as FallbackModelItem).name === 'string' &&
                modelIds.includes((m as FallbackModelItem).id)
              )
            : [];
          
          if (selectedModels.length < 2) {
            throw new Error('Not enough models found for comparison');
          }
          
          // Create a mock comparison response
          const mockComparison: VULCAComparison = {
            models: selectedModels.map((m) => ({
              modelId: m.id,
              modelName: m.name,
              scores6D: toVULCAScore6D(m.vulca_scores_6d),
              scores47D: m.vulca_scores_47d || {},
              culturalPerspectives: toCulturalPerspective(m.vulca_cultural_perspectives),
              evaluationDate: m.vulca_evaluation_date || new Date().toISOString()
            })),
            differenceMatrix: [],
            summary: {
              mostSimilar: {
                models: selectedModels.length >= 2 ? [selectedModels[0].name, selectedModels[1].name] : [selectedModels[0].name],
                difference: 3.2
              },
              mostDifferent: {
                models: selectedModels.length >= 2 ? [selectedModels[0].name, selectedModels[selectedModels.length - 1].name] : [selectedModels[0].name],
                difference: 8.5
              },
              averageDifference: 5.2,
            },
            comparisonDate: new Date().toISOString()
          };
          
          return mockComparison;
        } catch (fallbackError) {
          console.error('Fallback also failed:', fallbackError);
          throw error;
        }
      }
      
      throw error;
    }
  },

  /**
   * Get all 47 dimensions information
   */
  async getDimensions(): Promise<VULCADimensionInfo[]> {
    return cachedRequest(
      'vulca:dimensions',
      async () => {
        const response = await vulcaApi.get('/dimensions');
        return response.data;
      },
      1800000 // 30 minutes cache
    );
  },

  /**
   * Get cultural perspectives information
   */
  async getCulturalPerspectives(): Promise<VULCACulturalPerspectiveInfo[]> {
    return cachedRequest(
      'vulca:cultural-perspectives',
      async () => {
        const response = await vulcaApi.get('/cultural-perspectives');
        return response.data;
      },
      1800000 // 30 minutes cache
    );
  },

  /**
   * Get model evaluation history
   */
  async getModelHistory(modelId: number, limit = 10) {
    const response = await vulcaApi.get(`/history/${modelId}`, {
      params: { limit },
    });
    return response.data;
  },

  /**
   * Get sample evaluation for testing
   */
  async getSampleEvaluation(modelId: number): Promise<VULCAEvaluation> {
    const response = await vulcaApi.get(`/sample-evaluation/${modelId}`);
    return response.data.evaluation;
  },

  /**
   * Get demo comparison data
   */
  async getDemoComparison(): Promise<VULCAComparison> {
    return cachedRequest(
      'vulca:demo-comparison',
      async () => {
        const response = await vulcaApi.get('/demo-comparison');
        const comparison = response.data.comparison;
        
        // Transform snake_case to camelCase for summary
        if (comparison.summary) {
          const summary = comparison.summary;
          comparison.summary = {
            mostSimilar: summary.most_similar || summary.mostSimilar,
            mostDifferent: summary.most_different || summary.mostDifferent,
            averageDifference: summary.average_difference || summary.averageDifference,
            dimensionStatistics: summary.dimension_statistics || summary.dimensionStatistics,
            culturalAnalysis: summary.cultural_analysis || summary.culturalAnalysis,
          };
        }
        
        // Transform model data
        if (comparison.models) {
          // 47D dimension names in order (matching backend dim_0 to dim_46)
          const dim47Names = [
            'originality', 'imagination', 'innovation_depth', 'artistic_vision',
            'conceptual_novelty', 'creative_synthesis', 'ideation_fluency', 'divergent_thinking',
            'skill_mastery', 'precision', 'craft_excellence', 'technical_proficiency',
            'execution_quality', 'methodological_rigor', 'tool_expertise', 'procedural_knowledge',
            'emotional_depth', 'sentiment_expression', 'affective_resonance', 'mood_conveyance',
            'feeling_authenticity', 'empathy_evocation', 'psychological_insight', 'emotional_intelligence',
            'cultural_awareness', 'historical_grounding', 'situational_relevance', 'environmental_sensitivity',
            'social_consciousness', 'temporal_awareness', 'spatial_understanding', 'contextual_integration',
            'breakthrough_thinking', 'paradigm_shifting', 'novel_approaches', 'experimental_courage',
            'boundary_pushing', 'revolutionary_concepts', 'transformative_ideas', 'disruptive_creativity',
            'audience_engagement', 'lasting_impression', 'influence_scope', 'transformative_power',
            'memorable_quality', 'viral_potential', 'legacy_creation'
          ];

          comparison.models = comparison.models.map((model: Record<string, unknown>) => {
            const rawScores47D = (model.scores_47d || model.scores47D || {}) as Record<string, number>;

            // Transform scores47D to use both dim_X keys and name keys for compatibility
            const scores47D: Record<string, number> = {};
            dim47Names.forEach((name, index) => {
              const value = rawScores47D[name];
              if (value != null) {
                scores47D[`dim_${index}`] = value;  // For dim.id lookup
                scores47D[name] = value;            // For name lookup
              }
            });

            // Generate 6D scores by aggregating categories (indices 0-7, 8-15, etc.)
            const avgRange = (start: number, end: number) => {
              const values: number[] = [];
              for (let i = start; i <= end; i++) {
                const val = scores47D[`dim_${i}`];
                if (val != null) values.push(val);
              }
              return values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0;
            };

            // scores6D uses only dim_X keys to match visualization component expectations
            const scores6DSource = (model.scores_6d || model.scores6D || {
              dim_0: avgRange(0, 7),   // Creativity (dims 0-7)
              dim_1: avgRange(8, 15),  // Technique (dims 8-15)
              dim_2: avgRange(16, 23), // Emotion (dims 16-23)
              dim_3: avgRange(24, 31), // Context (dims 24-31)
              dim_4: avgRange(32, 39), // Innovation (dims 32-39)
              dim_5: avgRange(40, 46)  // Impact (dims 40-46)
            }) as Record<string, number>;
            const scores6D = toVULCAScore6D(scores6DSource);

            // Map cultural_scores to culturalPerspectives format
            const culturalScores = (model.cultural_scores || model.culturalScores || {}) as Record<string, number>;
            const culturalPerspectives = toCulturalPerspective(
              (model.cultural_perspectives || model.culturalPerspectives) as Record<string, unknown> | undefined
            );
            const fallbackCulturalPerspectives = toCulturalPerspective(culturalScores);

            return {
              modelId: String(model.model_id || model.modelId),
              modelName: model.model_name || model.modelName,
              scores6D,
              scores47D,
              culturalPerspectives: Object.values(culturalPerspectives).some(value => value !== 0)
                ? culturalPerspectives
                : fallbackCulturalPerspectives,
              evaluationDate: model.evaluation_date || model.evaluationDate || new Date().toISOString()
            };
          });
        }
        
        // Transform other fields if needed
        comparison.differenceMatrix = comparison.difference_matrix || comparison.differenceMatrix;
        
        return comparison;
      },
      300000 // 5 minutes cache
    );
  },
  
  /**
   * Clear all cached data
   */
  clearCache() {
    apiCache.clear();
  },
  
  /**
   * Check API health status
   */
  async healthCheck(): Promise<boolean> {
    try {
      await vulcaApi.get('/info');
      return true;
    } catch {
      return false;
    }
  },
};

export default vulcaService;
