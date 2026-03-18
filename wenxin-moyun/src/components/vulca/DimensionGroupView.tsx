import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip
} from 'recharts';
import type { VULCAScore47D, DimensionGroup } from '../../types/vulca';
import { IOSCard, IOSCardHeader, IOSCardContent } from '../ios';

interface DimensionGroupViewProps {
  scores47D: VULCAScore47D;
  modelName: string;
  groups?: DimensionGroup[];
  expanded?: string | null;
  onExpandGroup?: (groupId: string | null) => void;
}

// Default dimension groups - 8 groups for 47 dimensions
const defaultGroups: DimensionGroup[] = [
  {
    id: 'technical',
    name: 'Technical Skills',
    dimensions: ['dim_0', 'dim_1', 'dim_2', 'dim_3', 'dim_4', 'dim_5'],
    color: '#334155',
    icon: 'gear'
  },
  {
    id: 'creative',
    name: 'Creative Expression',
    dimensions: ['dim_6', 'dim_7', 'dim_8', 'dim_9', 'dim_10', 'dim_11'],
    color: '#B8923D',
    icon: 'palette'
  },
  {
    id: 'emotional',
    name: 'Emotional Depth',
    dimensions: ['dim_12', 'dim_13', 'dim_14', 'dim_15', 'dim_16'],
    color: '#C65D4D',
    icon: 'heart'
  },
  {
    id: 'contextual',
    name: 'Contextual Understanding',
    dimensions: ['dim_17', 'dim_18', 'dim_19', 'dim_20', 'dim_21', 'dim_22'],
    color: '#5F8A50',
    icon: 'globe'
  },
  {
    id: 'innovation',
    name: 'Innovation & Originality',
    dimensions: ['dim_23', 'dim_24', 'dim_25', 'dim_26', 'dim_27', 'dim_28'],
    color: '#C87F4A',
    icon: 'lightbulb'
  },
  {
    id: 'cultural',
    name: 'Cultural Relevance',
    dimensions: ['dim_29', 'dim_30', 'dim_31', 'dim_32', 'dim_33'],
    color: '#9B6B56',
    icon: 'world'
  },
  {
    id: 'impact',
    name: 'Impact & Influence',
    dimensions: ['dim_34', 'dim_35', 'dim_36', 'dim_37', 'dim_38', 'dim_39'],
    color: '#8F7860',
    icon: 'trending'
  },
  {
    id: 'synthesis',
    name: 'Synthesis & Integration',
    dimensions: ['dim_40', 'dim_41', 'dim_42', 'dim_43', 'dim_44', 'dim_45', 'dim_46'],
    color: '#6B8E7A',
    icon: 'merge'
  }
];

const DimensionGroupView: React.FC<DimensionGroupViewProps> = ({
  scores47D,
  modelName,
  groups = defaultGroups,
  expanded,
  onExpandGroup
}) => {
  const [localExpanded, setLocalExpanded] = useState<string | null>(null);
  const expandedGroup = expanded !== undefined ? expanded : localExpanded;
  const handleExpand = onExpandGroup || setLocalExpanded;
  
  // Generate test data if no scores provided
  const effectiveScores47D = useMemo(() => {
    if (scores47D && Object.keys(scores47D).length > 0) {
      return scores47D;
    }
    // Generate test data for demonstration
    const testScores: VULCAScore47D = {};
    for (let i = 0; i < 47; i++) {
      testScores[`dim_${i}`] = Math.random() * 100;
    }
    return testScores;
  }, [scores47D]);
  
  // Use effective scores
  const scores = effectiveScores47D;

  // Calculate average score for each group
  const calculateGroupAverage = (group: DimensionGroup): number => {
    const groupScores = group.dimensions
      .map(dim => scores[dim] || 0)
      .filter(score => score > 0);
    return groupScores.length > 0 
      ? groupScores.reduce((a, b) => a + b, 0) / groupScores.length 
      : 0;
  };

  // Prepare data for mini charts
  const prepareGroupData = (group: DimensionGroup) => {
    return group.dimensions.map((dim, idx) => ({
      dimension: `D${idx + 1}`,
      fullName: dim,
      value: scores[dim] || 0
    }));
  };

  // Get emoji icon name - temporary simplified version
  const getEmojiIcon = (iconName: string | undefined): string => {
    const iconMap: Record<string, string> = {
      gear: '⚙️',
      palette: '🎨',
      heart: '❤️',
      globe: '🌍',
      lightbulb: '💡',
      world: '🌎',
      trending: '📈',
      merge: '🔀'
    };
    return iconMap[iconName || ''] || '⭐';
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 sm:gap-4 md:gap-5">
      <AnimatePresence>
        {groups.map((group, index) => {
          const isExpanded = expandedGroup === group.id;
          const avgScore = calculateGroupAverage(group);
          const groupData = prepareGroupData(group);

          return (
            <motion.div
              key={group.id}
              layout
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{
                opacity: 1,
                scale: 1,
                y: 0,
                // Mobile: expanded cards take full width, Desktop: span 2 columns
                gridColumn: isExpanded ? (window.innerWidth < 768 ? 'span 1' : 'span 2') : 'span 1'
              }}
              exit={{ opacity: 0, scale: 0.9, y: -10 }}
              transition={{
                duration: 0.4,
                delay: index * 0.05, // Staggered animation
                type: 'spring',
                stiffness: 300,
                damping: 25
              }}
              className={isExpanded ? 'sm:col-span-2 lg:col-span-2' : ''}
            >
              <IOSCard
                variant="elevated"
                interactive
                animate
                className="h-full cursor-pointer"
                onClick={() => handleExpand(isExpanded ? null : group.id)}
              >
                <IOSCardHeader
                  title={group.name}
                  subtitle={`${group.dimensions.length} dimensions`}
                  emoji={
                    <div style={{ color: group.color, fontSize: '24px' }}>
                      {getEmojiIcon(group.icon)}
                    </div>
                  }
                  action={
                    <div className="text-2xl font-bold" style={{ color: group.color }}>
                      {avgScore.toFixed(1)}
                    </div>
                  }
                />
                <IOSCardContent>
                  <AnimatePresence mode="wait">
                    {!isExpanded ? (
                      // Collapsed view - mini bar chart (increased height for better visibility)
                      <motion.div
                        key="collapsed"
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                        className="h-36 md:h-40"
                      >
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={groupData} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
                            <Bar
                              dataKey="value"
                              fill={group.color}
                              radius={[4, 4, 0, 0]}
                            />
                            <YAxis hide domain={[0, 100]} />
                            <XAxis
                              dataKey="dimension"
                              tick={{ fontSize: 10 }}
                              interval={0}
                            />
                          </BarChart>
                        </ResponsiveContainer>
                      </motion.div>
                    ) : (
                      // Expanded view - detailed radar chart
                      <motion.div
                        key="expanded"
                        initial={{ opacity: 0, height: 0, y: -10 }}
                        animate={{ opacity: 1, height: 'auto', y: 0 }}
                        exit={{ opacity: 0, height: 0, y: -10 }}
                        transition={{
                          duration: 0.4,
                          type: 'spring',
                          stiffness: 200,
                          damping: 20
                        }}
                        className="space-y-4"
                      >
                        <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                            <RadarChart data={groupData}>
                              <PolarGrid 
                                stroke="rgba(0,0,0,0.1)" 
                                strokeDasharray="3 3"
                              />
                              <PolarAngleAxis 
                                dataKey="dimension" 
                                tick={{ fontSize: 12 }}
                              />
                              <PolarRadiusAxis 
                                domain={[0, 100]} 
                                tick={{ fontSize: 10 }}
                              />
                              <Radar
                                name={modelName}
                                dataKey="value"
                                stroke={group.color}
                                fill={group.color}
                                fillOpacity={0.3}
                                strokeWidth={2}
                              />
                              <Tooltip
                                formatter={(value) => [`${Number(value).toFixed(1)}`, 'Score']}
                                labelFormatter={(label) => `Dimension: ${label}`}
                              />
                            </RadarChart>
                          </ResponsiveContainer>
                        </div>
                        
                        {/* Detailed dimension list - Mobile optimized */}
                        <div className="space-y-2">
                          {groupData.map((item) => (
                            <div 
                              key={item.fullName}
                              className="flex flex-col sm:flex-row sm:justify-between sm:items-center p-2 bg-gray-50 dark:bg-gray-800 rounded-lg gap-1 sm:gap-2"
                            >
                              <span className="text-sm font-medium truncate">{item.fullName}</span>
                              <div className="flex items-center gap-2">
                                <div className="flex-1 sm:w-20 lg:w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                  <div 
                                    className="h-full rounded-full transition-all duration-300"
                                    style={{ 
                                      width: `${item.value}%`,
                                      backgroundColor: group.color 
                                    }}
                                  />
                                </div>
                                <span className="text-sm font-bold flex-shrink-0" style={{ color: group.color }}>
                                  {item.value.toFixed(1)}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </IOSCardContent>
              </IOSCard>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
};

export default DimensionGroupView;
