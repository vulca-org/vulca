/**
 * VULCA Visualization Component
 * Provides multiple visualization types for VULCA evaluation data
 */

import React, { useMemo, useState, useEffect } from 'react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  Cell,
} from 'recharts';
import { IOSCard, IOSButton } from '../ios';
import { ZoomableChartWrapper } from './ZoomableChartWrapper';
import type {
  ViewMode,
  VisualizationType,
  ViewLevel,
  VULCAEvaluation,
} from '../../types/vulca';
import DimensionGroupView from './DimensionGroupView';
import { DIMENSION_CATEGORIES, getDimensionCategory, getDimensionLabel, CULTURAL_PERSPECTIVES } from '../../utils/vulca-dimensions';
import { useChartTheme } from '../../hooks/useChartTheme';
import { useAutoChartType } from '../../hooks/vulca/useAutoChartType';

// Hook for detecting mobile viewport
const useIsMobile = (breakpoint = 768) => {
  const [isMobile, setIsMobile] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.innerWidth < breakpoint;
    }
    return false;
  });

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < breakpoint);
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, [breakpoint]);

  return isMobile;
};

// Enhanced helper function to format dimension names from any format
const formatDimensionName = (text: string): string => {
  if (!text) return '';
  
  // If already has proper spacing (contains space and doesn't have underscore), return as-is
  if (text.includes(' ') && !text.includes('_')) {
    return text;
  }
  
  // Handle snake_case: innovation_depth -> Innovation Depth
  if (text.includes('_')) {
    return text.split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  }
  
  // Handle camelCase/PascalCase: InnovationDepth -> Innovation Depth
  // More comprehensive approach for better camelCase handling
  let result = text
    // Insert space before uppercase letters that follow lowercase letters or digits
    .replace(/([a-z\d])([A-Z])/g, '$1 $2')
    // Insert space between consecutive uppercase letters followed by lowercase
    .replace(/([A-Z]+)([A-Z][a-z\d]+)/g, '$1 $2');
  
  // Ensure first letter is uppercase
  result = result.charAt(0).toUpperCase() + result.slice(1);
  
  // Clean up any multiple spaces
  return result.replace(/\s+/g, ' ').trim();
};

type ChartDataPoint = Record<string, string | number>;

interface HeatmapPoint {
  x: number;
  y: number;
  value: number;
  model: string;
  dimension: string;
}

interface HeatmapTooltipProps {
  active?: boolean;
  payload?: Array<{ payload: HeatmapPoint }>;
}

interface BarChartTooltipEntry {
  name?: string | number;
  value?: number | string;
  color?: string;
  payload?: { fullName?: string };
}

interface VULCAVisualizationProps {
  evaluations: VULCAEvaluation[];
  dimensions: { id: string; name: string; description: string }[];
  viewMode: ViewMode;
  visualizationType?: VisualizationType; // Now optional - auto-selected if not provided
  culturalPerspective?: string;
  viewLevel?: ViewLevel;
}

export const VULCAVisualization: React.FC<VULCAVisualizationProps> = ({
  evaluations,
  dimensions,
  viewMode,
  visualizationType: manualVisualizationType,
  culturalPerspective = 'eastern',
  viewLevel = 'overview',
}) => {
  // Detect mobile viewport for touch gestures
  const isMobile = useIsMobile();

  // 使用统一的图表主题 hook (支持深色/浅色模式)
  const { seriesColors, colors: themeColors } = useChartTheme();
  const colors = useMemo(() => seriesColors(5), [seriesColors]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [expandedGroup, setExpandedGroup] = useState<string | null>(null);
  const [selectedCulturalPerspective, setSelectedCulturalPerspective] = useState<string>(culturalPerspective);
  const [dimensionFilter, setDimensionFilter] = useState<'all' | 'high-variance' | 'top-performance' | 'custom'>('high-variance');
  const [customDimensionCount] = useState<number>(15);

  // Auto-select chart type based on data characteristics
  const { chartType: autoChartType } = useAutoChartType({
    viewMode,
    viewLevel,
    modelCount: evaluations.length,
    dimensionCount: dimensions.length,
  });

  // Use manual type if provided, otherwise use auto-selected type
  const visualizationType = manualVisualizationType || autoChartType;
  
  // Filter dimensions by category for 47D mode
  const filteredDimensions = useMemo(() => {
    if (viewMode === '6d') {
      return dimensions.slice(0, 6);
    }
    
    
    if (selectedCategory === 'all') {
      return dimensions;
    }
    const filtered = dimensions.filter(dim => {
      const category = getDimensionCategory(dim.id);
      return category === selectedCategory;
    });
    return filtered;
  }, [dimensions, viewMode, selectedCategory]);
  
  // Prepare data for different visualization types
  const radarData = useMemo(() => {
    if (!evaluations.length || !filteredDimensions.length) return [];
    
    // For radar chart, show all dimensions when in 47D mode
    const radarDimensions = filteredDimensions.slice(0, viewMode === '6d' ? 6 : 
      filteredDimensions.length);
    
    return radarDimensions.map(dim => {
      const dataPoint: ChartDataPoint = { dimension: dim.name };
      
      evaluations.forEach((evaluation, index) => {
        const scores = viewMode === '6d' ? evaluation.scores6D : evaluation.scores47D;
        // Use modelName, fallback to a readable name instead of model_0
        const modelKey = evaluation.modelName || `Model ${index + 1}`;
        dataPoint[modelKey] = scores ? (scores[dim.id as keyof typeof scores] || 0) : 0;
      });
      
      return dataPoint;
    });
  }, [evaluations, filteredDimensions, viewMode]);
  
  const barData = useMemo(() => {
    if (!evaluations.length) return [];
    
    return evaluations.map((evaluation, index) => {
      const scores = viewMode === '6d' ? evaluation.scores6D : evaluation.scores47D;
      return {
        model: evaluation.modelName,
        ...(scores ? Object.entries(scores)
          .slice(0, 8)
          .reduce((acc, [key, value]) => ({
            ...acc,
            [key]: value,
          }), {}) : {}),
        color: colors[index % colors.length],
      };
    });
  }, [evaluations, viewMode, colors]);
  
  const heatmapData = useMemo(() => {
    if (!evaluations.length || !filteredDimensions.length) return [];
    
    const data: HeatmapPoint[] = [];
    const dimSlice = filteredDimensions.slice(0, viewMode === '6d' ? 6 : 
      filteredDimensions.length);
    
    evaluations.forEach((evaluation, modelIndex) => {
      dimSlice.forEach((dim, dimIndex) => {
        const scores = viewMode === '6d' ? evaluation.scores6D : evaluation.scores47D;
        data.push({
          x: dimIndex,
          y: modelIndex,
          value: scores ? (scores[dim.id as keyof typeof scores] || 0) : 0,
          model: evaluation.modelName,
          dimension: dim.name,
        });
      });
    });
    
    return data;
  }, [evaluations, filteredDimensions, viewMode]);
  
  const parallelData = useMemo(() => {
    if (!evaluations.length) return [];
    
    // Prepare data for parallel coordinates
    const selectedDimensions = filteredDimensions.slice(0, viewMode === '6d' ? 6 : 
      filteredDimensions.length);
    
    return evaluations.map((evaluation, index) => {
      const scores = viewMode === '6d' ? evaluation.scores6D : evaluation.scores47D;
      const dataPoint: ChartDataPoint = {
        model: evaluation.modelName,
        color: colors[index % colors.length],
      };
      
      selectedDimensions.forEach(dim => {
        dataPoint[dim.id] = scores ? (scores[dim.id as keyof typeof scores] || 0) : 0;
      });
      
      return dataPoint;
    });
  }, [evaluations, filteredDimensions, viewMode, colors]);
  
  // Custom tooltip for heatmap
  const HeatmapTooltip = ({ active, payload }: HeatmapTooltipProps) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white dark:bg-gray-800 p-2 rounded shadow-lg border">
          <p className="font-semibold">{data.model}</p>
          <p className="text-sm">{data.dimension}</p>
          <p className="text-sm font-medium">Score: {data.value?.toFixed(1) || 'N/A'}</p>
        </div>
      );
    }
    return null;
  };
  
  // Get color for heatmap based on value
  const getHeatmapColor = (value: number) => {
    const normalized = value / 100;
    const hue = (1 - normalized) * 240; // Blue (240) to Red (0)
    return `hsl(${hue}, 70%, 50%)`;
  };
  
  // Render detailed parallel coordinates view with filtering
  const renderDetailedParallelView = () => {
    // Filter dimensions based on selected category
    const detailedDims = selectedCategory === 'all' 
      ? filteredDimensions 
      : filteredDimensions.filter(dim => getDimensionCategory(dim.id) === selectedCategory);
    
    // Prepare data with difference highlighting
    const enhancedData = evaluations.map((evaluation, evalIndex) => {
      const scores = viewMode === '6d' ? evaluation.scores6D : evaluation.scores47D;
      const dataPoint: ChartDataPoint = {
        model: evaluation.modelName,
        modelIndex: evalIndex,
      };
      
      detailedDims.forEach(dim => {
        const score = scores ? (scores[dim.id as keyof typeof scores] || 0) : 0;
        dataPoint[dim.id] = score;
        
        // Calculate variance for this dimension across all models
        if (evaluations.length > 1) {
          const allScores = evaluations.map(e => {
            const s = viewMode === '6d' ? e.scores6D : e.scores47D;
            return s ? (s[dim.id as keyof typeof s] || 0) : 0;
          });
          const avg = allScores.reduce((a, b) => a + b, 0) / allScores.length;
          const variance = Math.sqrt(allScores.reduce((sum, s) => sum + Math.pow(s - avg, 2), 0) / allScores.length);
          dataPoint[`${dim.id}_variance`] = variance;
          dataPoint[`${dim.id}_diff`] = Math.abs(score - avg);
        }
      });
      
      return dataPoint;
    });
    
    // Find dimensions with highest variance (most differentiating)
    const dimensionVariances = detailedDims.map(dim => {
      if (evaluations.length <= 1) return { dim, variance: 0 };
      
      const allScores = evaluations.map(e => {
        const s = viewMode === '6d' ? e.scores6D : e.scores47D;
        return s ? (s[dim.id as keyof typeof s] || 0) : 0;
      });
      const avg = allScores.reduce((a, b) => a + b, 0) / allScores.length;
      const variance = Math.sqrt(allScores.reduce((sum, s) => sum + Math.pow(s - avg, 2), 0) / allScores.length);
      
      return { dim, variance };
    }).sort((a, b) => b.variance - a.variance);
    
    // Select dimensions based on current filter
    let topDims = dimensionVariances.slice(0, 15).map(dv => dv.dim);
    
    switch (dimensionFilter) {
      case 'all':
        topDims = detailedDims.slice(0, 25); // Show more when all is selected
        break;
      case 'high-variance':
        topDims = dimensionVariances.slice(0, 15).map(dv => dv.dim);
        break;
      case 'top-performance': {
        // Find dimensions with highest average scores across models
        const performanceDims = detailedDims.map(dim => {
          const avgScore = evaluations.reduce((sum, e) => {
            const scores = viewMode === '6d' ? e.scores6D : e.scores47D;
            return sum + (scores ? (scores[dim.id as keyof typeof scores] || 0) : 0);
          }, 0) / evaluations.length;
          return { dim, avgScore };
        }).sort((a, b) => b.avgScore - a.avgScore);
        topDims = performanceDims.slice(0, 10).map(pd => pd.dim);
        break;
      }
      case 'custom':
        topDims = detailedDims.slice(0, customDimensionCount);
        break;
      default:
        topDims = dimensionVariances.slice(0, 15).map(dv => dv.dim);
    }
    
    return (
      <div className="space-y-4">
        {/* Smart dimension selection based on filter */}
        <div className="flex flex-wrap gap-2 p-4 bg-slate-50 dark:bg-slate-900/20 rounded-lg border border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-slate-700 dark:text-slate-400">
              📊 Showing {topDims.length} dimensions
            </span>
            <span className="text-xs text-slate-700 dark:text-slate-500 bg-slate-100 dark:bg-slate-900/50 px-2 py-1 rounded">
              {dimensionFilter === 'all' && 'All Available'}
              {dimensionFilter === 'high-variance' && 'High Variance'}
              {dimensionFilter === 'top-performance' && 'Top Performers'}
              {dimensionFilter === 'custom' && `Custom (${customDimensionCount})`}
            </span>
          </div>
          
          {/* Quick filter toggles */}
          <div className="flex gap-1 ml-auto">
            <IOSButton
              variant="text"
              size="sm"
              onClick={() => setDimensionFilter('high-variance')}
              className="text-xs"
            >
              ⚡ High Variance
            </IOSButton>
            <IOSButton
              variant="text"
              size="sm"
              onClick={() => setDimensionFilter('top-performance')}
              className="text-xs"
            >
              🏆 Top Performers
            </IOSButton>
          </div>
        </div>
        
        {/* Enhanced parallel coordinates chart */}
        <ResponsiveContainer width="100%" height={600}>
          <LineChart data={enhancedData}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
            <XAxis
              dataKey="model"
              angle={-45}
              textAnchor="end"
              height={100}
              tick={{ fontSize: 12 }}
            />
            <YAxis 
              domain={[0, 100]} 
              ticks={[0, 25, 50, 75, 100]}
              tick={{ fontSize: 12 }}
            />
            <Tooltip 
              content={({ active, payload, label }) => {
                if (!active || !payload || !payload.length) return null;
                
                const data = payload[0].payload;
                const topDiffs = payload
                  .filter(p => !p.dataKey.includes('_variance') && !p.dataKey.includes('_diff'))
                  .sort((a, b) => {
                    const diffA = data[`${a.dataKey}_diff`] || 0;
                    const diffB = data[`${b.dataKey}_diff`] || 0;
                    return diffB - diffA;
                  })
                  .slice(0, 5);
                
                return (
                  <div className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-lg border">
                    <p className="font-semibold mb-2">{label}</p>
                    <div className="space-y-1">
                      {topDiffs.map(entry => (
                        <div key={entry.dataKey} className="flex justify-between gap-4 text-sm">
                          <span>{entry.name}:</span>
                          <span className="font-medium">
                            {entry.value?.toFixed(1)}
                            {data[`${entry.dataKey}_diff`] > 10 && (
                              <span className="text-[#B8923D] ml-1">⚡</span>
                            )}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              }}
            />
            <Legend 
              wrapperStyle={{ paddingTop: '20px' }}
              iconType="line"
            />
            
            {/* Render lines with enhanced difference highlighting */}
            {topDims.map((dim, index) => {
              const variance = dimensionVariances.find(dv => dv.dim.id === dim.id)?.variance || 0;
              const avgScore = evaluations.reduce((sum, e) => {
                const scores = viewMode === '6d' ? e.scores6D : e.scores47D;
                return sum + (scores ? (scores[dim.id as keyof typeof scores] || 0) : 0);
              }, 0) / evaluations.length;
              
              // Classification based on variance and performance
              const isHighVariance = variance > 15;
              const isMediumVariance = variance > 8 && variance <= 15;
              const isHighPerformer = avgScore > 75;
              const isLowPerformer = avgScore < 40;
              
              // Dynamic styling based on characteristics - using theme colors
              let strokeColor = themeColors.grid.line;
              let strokeWidth = 1.5;
              let strokeOpacity = 0.5;
              let dotSize = 3;

              if (isHighVariance) {
                strokeColor = isHighPerformer ? themeColors.semantic.success : isLowPerformer ? themeColors.semantic.error : colors[index % colors.length];
                strokeWidth = 3.5;
                strokeOpacity = 1;
                dotSize = 6;
              } else if (isMediumVariance) {
                strokeColor = colors[index % colors.length];
                strokeWidth = 2.5;
                strokeOpacity = 0.8;
                dotSize = 4;
              } else if (isHighPerformer) {
                strokeColor = themeColors.semantic.success;
                strokeWidth = 2;
                strokeOpacity = 0.7;
                dotSize = 4;
              } else if (isLowPerformer) {
                strokeColor = themeColors.semantic.warning;
                strokeWidth = 2;
                strokeOpacity = 0.6;
                dotSize = 3;
              }
              
              return (
                <Line
                  key={dim.id}
                  type="monotone"
                  dataKey={dim.id}
                  name={`${getDimensionLabel(dim.id)} (σ:${variance.toFixed(1)})`}
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  strokeOpacity={strokeOpacity}
                  strokeDasharray={isHighVariance ? '0' : isMediumVariance ? '5,5' : '0'}
                  dot={{ 
                    r: dotSize, 
                    fill: strokeColor,
                    stroke: '#fff',
                    strokeWidth: 1
                  }}
                  activeDot={{ 
                    r: dotSize + 2, 
                    fill: strokeColor,
                    stroke: '#fff',
                    strokeWidth: 2
                  }}
                />
              );
            })}
          </LineChart>
        </ResponsiveContainer>
        
        {/* Enhanced analysis with difference highlighting - Mobile responsive */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <IOSCard variant="flat" className="border-l-4 border-red-500">
            <div className="p-4">
              <h5 className="text-sm font-medium text-red-600 dark:text-red-400 flex items-center">
                📊 Most Differentiating
              </h5>
              <p className="text-lg font-semibold mt-1">
                {dimensionVariances[0] ? getDimensionLabel(dimensionVariances[0].dim.id) : 'N/A'}
              </p>
              <p className="text-sm text-red-500 mt-1">
                σ = {dimensionVariances[0]?.variance.toFixed(1) || '0'}
              </p>
            </div>
          </IOSCard>
          
          <IOSCard variant="flat" className="border-l-4 border-[#5F8A50]">
            <div className="p-4">
              <h5 className="text-sm font-medium text-[#5F8A50] dark:text-[#87A878] flex items-center">
                🏆 Highest Performing
              </h5>
              <p className="text-lg font-semibold mt-1">
                {(() => {
                  const perfDims = dimensionVariances.map(dv => {
                    const avg = evaluations.reduce((sum, e) => {
                      const scores = viewMode === '6d' ? e.scores6D : e.scores47D;
                      return sum + (scores ? (scores[dv.dim.id as keyof typeof scores] || 0) : 0);
                    }, 0) / evaluations.length;
                    return { ...dv, avgScore: avg };
                  }).sort((a, b) => b.avgScore - a.avgScore);
                  return perfDims[0] ? getDimensionLabel(perfDims[0].dim.id) : 'N/A';
                })()}
              </p>
              <p className="text-sm text-[#5F8A50] mt-1">
                Avg: {(() => {
                  const perfDims = dimensionVariances.map(dv => {
                    const avg = evaluations.reduce((sum, e) => {
                      const scores = viewMode === '6d' ? e.scores6D : e.scores47D;
                      return sum + (scores ? (scores[dv.dim.id as keyof typeof scores] || 0) : 0);
                    }, 0) / evaluations.length;
                    return avg;
                  }).sort((a, b) => b - a);
                  return perfDims[0]?.toFixed(1) || '0';
                })()} pts
              </p>
            </div>
          </IOSCard>
          
          <IOSCard variant="flat" className="border-l-4 border-gray-500">
            <div className="p-4">
              <h5 className="text-sm font-medium text-gray-600 dark:text-gray-400 flex items-center">
                ⚖️ Most Consistent
              </h5>
              <p className="text-lg font-semibold mt-1">
                {dimensionVariances[dimensionVariances.length - 1] ? getDimensionLabel(dimensionVariances[dimensionVariances.length - 1].dim.id) : 'N/A'}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                σ = {dimensionVariances[dimensionVariances.length - 1]?.variance.toFixed(1) || '0'}
              </p>
            </div>
          </IOSCard>
          
          <IOSCard variant="flat" className="border-l-4 border-slate-600">
            <div className="p-4">
              <h5 className="text-sm font-medium text-slate-700 dark:text-slate-500 flex items-center">
                📈 Overview
              </h5>
              <p className="text-lg font-semibold mt-1">
                {dimensionVariances.length} dims
              </p>
              <p className="text-sm text-slate-600 mt-1">
                Avg σ: {(dimensionVariances.reduce((sum, dv) => sum + dv.variance, 0) / dimensionVariances.length).toFixed(1)}
              </p>
            </div>
          </IOSCard>
        </div>
        
        {/* Legend for line styles and colors - Mobile responsive */}
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 sm:p-4">
          <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center">
            🎨 Visual Legend
          </h5>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-4 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-4 h-0.5 bg-[#5F8A50]"></div>
              <span>High Variance + High Score</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-0.5 bg-red-500"></div>
              <span>High Variance + Low Score</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-0.5 bg-slate-600 opacity-80" style={{borderTop: '1px dashed'}}></div>
              <span>Medium Variance</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-0.5 bg-gray-400 opacity-60"></div>
              <span>Low Variance</span>
            </div>
          </div>
        </div>
        
        <div className="text-center">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Showing {topDims.length} dimensions with enhanced difference highlighting.
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
            Line thickness and color intensity indicate variance levels. 
            Green = High performance, Red = High variance + Low performance, Dashed = Medium variance.
          </p>
        </div>
      </div>
    );
  };
  
  // Render based on visualization type and view level
  const renderVisualization = () => {
    // For 47D mode with grouped view level, show dimension groups
    if (viewMode === '47d' && viewLevel === 'grouped' && evaluations.length > 0) {
      return (
        <DimensionGroupView
          scores47D={evaluations[0].scores47D}
          modelName={evaluations[0].modelName}
          expanded={expandedGroup}
          onExpandGroup={setExpandedGroup}
        />
      );
    }
    
    // For overview mode or 6D, show simplified visualization
    if (viewMode === '6d') {
      // Use radar chart for 6D mode
      const chartContent = (
        <ResponsiveContainer width="100%" height={500}>
          <RadarChart data={radarData.slice(0, 6)}>
            <PolarGrid gridType="polygon" />
            <PolarAngleAxis dataKey="dimension" />
            <PolarRadiusAxis angle={90} domain={[0, 100]} />
            <Tooltip />
            <Legend />

            {evaluations.map((evaluation, index) => {
              const modelKey = evaluation.modelName || `Model ${index + 1}`;
              return (
                <Radar
                  key={modelKey}
                  name={modelKey}
                  dataKey={modelKey}
                  stroke={colors[index % colors.length]}
                  fill={colors[index % colors.length]}
                  fillOpacity={0.3}
                  strokeWidth={2}
                />
              );
            })}
          </RadarChart>
        </ResponsiveContainer>
      );

      // Wrap with ZoomableChartWrapper on mobile for pinch-to-zoom
      return isMobile ? (
        <ZoomableChartWrapper showControls={true}>
          {chartContent}
        </ZoomableChartWrapper>
      ) : chartContent;
    }
    
    // For 47D mode with many dimensions, use bar chart for better readability
    if (viewMode === '47d' && filteredDimensions.length > 12) {
      // Responsive margin and label settings
      const yAxisWidth = isMobile ? 80 : 140;
      const maxLabelLength = isMobile ? 15 : 28;
      const barHeight = isMobile ? 20 : 25;

      // Calculate chart height with max limit for scrollable container
      const calculatedHeight = Math.max(400, filteredDimensions.length * barHeight);
      const maxHeight = isMobile ? 500 : 700;
      const chartHeight = Math.min(calculatedHeight, maxHeight);
      const needsScroll = calculatedHeight > maxHeight;

      // Prepare bar data for 47D visualization
      const barData47D = filteredDimensions.map((dim, index) => {
        // Store the raw dimension name/id for the Y-axis
        // The tickFormatter will handle the formatting
        const rawName = dim.name || dim.id;

        // Get the properly formatted name for tooltip display
        let properName = getDimensionLabel(dim.id);
        if (!properName || properName === dim.id) {
          properName = formatDimensionName(rawName);
        } else {
          properName = formatDimensionName(properName);
        }

        const dataPoint: ChartDataPoint = {
          dimension: rawName,  // Raw name for Y-axis (tickFormatter will format it)
          fullName: properName,  // Formatted name for tooltip
          originalIndex: index,
          dimensionId: dim.id
        };
        evaluations.forEach((evaluation) => {
          const scores = evaluation.scores47D;
          dataPoint[evaluation.modelName] = scores ? (scores[dim.id as keyof typeof scores] || 0) : 0;
        });
        return dataPoint;
      });

      const chartContent47D = (
        <ResponsiveContainer width="100%" height={needsScroll ? calculatedHeight : chartHeight}>
          <BarChart
            data={barData47D}
            layout="horizontal"
            margin={{ top: 5, right: isMobile ? 20 : 30, left: yAxisWidth - 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[0, 100]} />
            <YAxis
              dataKey="dimension"
              type="category"
              width={yAxisWidth}
              tick={(props: { x: number; y: number; payload?: { value?: string } }) => {
                const { x, y, payload } = props;
                if (!payload?.value) {
                  return <text x={x} y={y}></text>;
                }

                // Apply formatDimensionName to ensure proper spacing
                const formatted = formatDimensionName(payload.value);
                const truncateAt = maxLabelLength - 3;
                const displayText = formatted.length > maxLabelLength
                  ? formatted.substring(0, truncateAt) + '...'
                  : formatted;

                return (
                  <text
                    x={x}
                    y={y}
                    dy={4}
                    textAnchor="end"
                    fill={themeColors.grid.text}
                    fontSize={isMobile ? 9 : 10}
                    className="recharts-text recharts-cartesian-axis-tick-value"
                  >
                    {displayText}
                  </text>
                );
              }}
            />
            <Tooltip content={({ active, payload }) => {
              if (active && payload && payload.length) {
                return (
                  <div className="bg-white dark:bg-gray-800 p-2 border rounded shadow">
                    <p className="text-sm font-medium">{payload[0].payload.fullName}</p>
                    {payload.map((entry: BarChartTooltipEntry, index: number) => (
                      <p key={index} className="text-xs" style={{ color: entry.color }}>
                        {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(1) : entry.value ?? 'N/A'}
                      </p>
                    ))}
                  </div>
                );
              }
              return null;
            }} />
            <Legend />
            {evaluations.map((evaluation, index) => (
              <Bar
                key={evaluation.modelName}
                dataKey={evaluation.modelName}
                fill={colors[index % colors.length]}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      );

      // Wrap with scrollable container if needed
      const scrollableChart = needsScroll ? (
        <div
          className="max-h-[500px] md:max-h-[700px] overflow-y-auto overflow-x-hidden rounded-lg"
          style={{ scrollbarGutter: 'stable' }}
        >
          {chartContent47D}
        </div>
      ) : chartContent47D;

      return (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
            <span>Showing {filteredDimensions.length} dimensions for {evaluations.map(e => e.modelName).join(', ')}</span>
            {needsScroll && (
              <span className="text-xs text-gray-500 dark:text-gray-500 flex items-center gap-1">
                <span>↕</span> Scroll to see all dimensions
              </span>
            )}
          </div>
          {isMobile ? (
            <ZoomableChartWrapper showControls={true}>
              {scrollableChart}
            </ZoomableChartWrapper>
          ) : scrollableChart}
        </div>
      );
    }

    // Capture viewMode to avoid type narrowing issues
    const currentViewMode: ViewMode = viewMode as ViewMode;

    // Original detailed visualization logic for smaller dimension sets
    switch (visualizationType) {
      case 'radar':
        // Use radar only for smaller dimension sets (<=12)
        if (filteredDimensions.length <= 12) {
          return (
            <ResponsiveContainer width="100%" height={500}>
              <RadarChart data={radarData}>
                <PolarGrid gridType="polygon" />
                <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 10 }} />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Tooltip />
                <Legend />

              {evaluations.map((evaluation, index) => {
                const modelKey = evaluation.modelName || `Model ${index + 1}`;
                return (
                  <Radar
                    key={modelKey}
                    name={modelKey}
                    dataKey={modelKey}
                    stroke={colors[index % colors.length]}
                    fill={colors[index % colors.length]}
                    fillOpacity={0.3}
                    strokeWidth={2}
                  />
                );
              })}
            </RadarChart>
          </ResponsiveContainer>
          );
        }
        // For large dimension sets, render bar chart instead
        return (
          <ResponsiveContainer width="100%" height={500}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="model" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />

              {filteredDimensions.map((dim, index) => (
                <Bar
                  key={dim.id}
                  dataKey={dim.id}
                  name={getDimensionLabel(dim.id)}
                  fill={colors[index % colors.length]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        );

      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={500}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="model" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              
              {filteredDimensions.map((dim, index) => (
                <Bar
                  key={dim.id}
                  dataKey={dim.id}
                  name={getDimensionLabel(dim.id)}
                  fill={colors[index % colors.length]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        );
      
      case 'heatmap': {
        const heatmapDimSlice = filteredDimensions.slice(0, currentViewMode === '6d' ? 6 :
          filteredDimensions.length);
        
        return (
          <div>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart
                margin={{ top: 20, right: 20, bottom: 60, left: 100 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  type="number"
                  domain={[0, heatmapDimSlice.length - 1]}
                  ticks={heatmapDimSlice.map((_, i) => i)}
                  tickFormatter={(value) => 
                    heatmapDimSlice[value]?.name.substring(0, 8) || ''
                  }
                  angle={-45}
                  textAnchor="end"
                />
                <YAxis
                  type="number"
                  domain={[0, evaluations.length - 1]}
                  ticks={evaluations.map((_, i) => i)}
                  tickFormatter={(value) => 
                    evaluations[value]?.modelName || ''
                  }
                />
                <Tooltip content={<HeatmapTooltip />} />
                
                <Scatter data={heatmapData} fill={colors[0]}>
                  {heatmapData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={getHeatmapColor(entry.value)}
                      stroke="white"
                      strokeWidth={1}
                      style={{
                        width: 40,
                        height: 40,
                        cursor: 'pointer',
                      }}
                    />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
            
            {/* Color scale legend */}
            <div className="mt-4 flex items-center justify-center">
              <span className="text-sm mr-2">Low (0)</span>
              <div
                className="h-4 w-48 rounded"
                style={{
                  background: 'linear-gradient(to right, hsl(240, 70%, 50%), hsl(120, 70%, 50%), hsl(0, 70%, 50%))',
                }}
              />
              <span className="text-sm ml-2">High (100)</span>
            </div>
          </div>
        );
      }
      
      case 'parallel': {
        // For detailed view, show enhanced parallel coordinates
        if (viewLevel === 'detailed' && currentViewMode === '47d') {
          return renderDetailedParallelView();
        }

        // Original parallel view for overview/grouped modes
        const selectedDims = filteredDimensions.slice(0, currentViewMode === '6d' ? 6 :
          Math.min(filteredDimensions.length, 12)); // Limit to 12 for readability
        
        return (
          <div>
            <ResponsiveContainer width="100%" height={500}>
              <LineChart data={parallelData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="model"
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                
                {selectedDims.map((dim, index) => (
                  <Line
                    key={dim.id}
                    type="monotone"
                    dataKey={dim.id}
                    name={getDimensionLabel(dim.id)}
                    stroke={colors[index % colors.length]}
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
            
            <p className="text-sm text-gray-500 mt-2">
              Parallel coordinates showing {selectedDims.length} dimensions across models
            </p>
          </div>
        );
      }
      
      default:
        return <p>Unknown visualization type</p>;
    }
  };
  
  // Cultural perspective overlay
  const renderCulturalOverlay = () => {
    if (!evaluations.length) return null;
    
    const culturalScores = evaluations.map(e => ({
      model: e.modelName,
      score: e.culturalPerspectives && selectedCulturalPerspective 
        ? (e.culturalPerspectives[selectedCulturalPerspective as keyof typeof e.culturalPerspectives] || 0)
        : 0,
    }));
    
    return (
      <IOSCard variant="elevated" className="mt-4">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-medium">Cultural Perspective</h4>
          <select
            value={selectedCulturalPerspective}
            onChange={(e) => setSelectedCulturalPerspective(e.target.value)}
            className="text-sm px-3 py-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-slate-600 focus:border-transparent"
          >
            {Object.entries(CULTURAL_PERSPECTIVES).map(([key, perspective]) => (
              <option key={key} value={key}>
                {perspective.name}
              </option>
            ))}
          </select>
        </div>
        
        <ResponsiveContainer width="100%" height={150}>
          <BarChart data={culturalScores} layout="horizontal">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[0, 100]} />
            <YAxis dataKey="model" type="category" width={100} />
            <Tooltip />
            <Bar dataKey="score" fill={colors[3]} />
          </BarChart>
        </ResponsiveContainer>
      </IOSCard>
    );
  };
  
  if (!evaluations.length) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center text-gray-500 dark:text-gray-400">
          <p className="text-lg">No evaluation data available</p>
          <p className="text-sm mt-2">Select models and run evaluation to see visualizations</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Category selector for 47D mode - Mobile Optimized */}
      {viewMode === '47d' && (
        <div className="bg-white dark:bg-gray-900 rounded-lg p-3 sm:p-4">
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-3">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Categories:
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-400 sm:ml-auto">
              {filteredDimensions.length} dimensions
            </span>
          </div>
          
          {/* Mobile: Scrollable horizontal buttons */}
          <div className="block sm:hidden">
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
              <IOSButton
                variant={selectedCategory === 'all' ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setSelectedCategory('all')}
                className="whitespace-nowrap flex-shrink-0"
              >
                All ({dimensions.length})
              </IOSButton>
              {Object.entries(DIMENSION_CATEGORIES).map(([key, category]) => (
                <IOSButton
                  key={key}
                  variant={selectedCategory === key ? 'primary' : 'secondary'}
                  size="sm"
                  onClick={() => setSelectedCategory(key)}
                  className="whitespace-nowrap flex-shrink-0"
                  style={{
                    borderColor: selectedCategory === key ? category.color : undefined,
                    color: selectedCategory === key ? category.color : undefined
                  }}
                >
                  {category.name.split(' ')[0]} ({category.range[1] - category.range[0] + 1})
                </IOSButton>
              ))}
            </div>
          </div>
          
          {/* Desktop: Flexbox wrap */}
          <div className="hidden sm:flex flex-wrap gap-2">
            <IOSButton
              variant={selectedCategory === 'all' ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setSelectedCategory('all')}
            >
              All Dimensions ({dimensions.length})
            </IOSButton>
            {Object.entries(DIMENSION_CATEGORIES).map(([key, category]) => (
              <IOSButton
                key={key}
                variant={selectedCategory === key ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setSelectedCategory(key)}
                style={{
                  borderColor: selectedCategory === key ? category.color : undefined,
                  color: selectedCategory === key ? category.color : undefined
                }}
              >
                {category.name} ({category.range[1] - category.range[0] + 1})
              </IOSButton>
            ))}
          </div>
        </div>
      )}
      
      {/* Main visualization - Mobile responsive */}
      <div className="bg-white dark:bg-gray-900 rounded-lg p-3 sm:p-6">
        <div className="h-[350px] sm:h-[500px] lg:h-[600px]">
          {renderVisualization()}
        </div>
      </div>
      
      {/* Cultural perspective overlay */}
      {renderCulturalOverlay()}
      
      {/* Statistics summary - Mobile responsive grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {evaluations.map((evaluation, index) => {
          const avgScore = viewMode === '6d'
            ? (evaluation.scores6D ? Object.values(evaluation.scores6D).reduce((a, b) => a + b, 0) / 6 : 0)
            : (evaluation.scores47D ? Object.values(evaluation.scores47D).slice(0, 47).reduce((a, b) => a + b, 0) / 47 : 0);
          
          return (
            <IOSCard key={evaluation.modelId} variant="elevated" className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <div
                  className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: colors[index % colors.length] }}
                />
                <h5 className="font-medium text-sm truncate">{evaluation.modelName}</h5>
              </div>
              <p className="text-xl sm:text-2xl font-bold mt-1">{avgScore.toFixed(1)}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Average Score</p>
            </IOSCard>
          );
        })}
      </div>
    </div>
  );
};

export default VULCAVisualization;
