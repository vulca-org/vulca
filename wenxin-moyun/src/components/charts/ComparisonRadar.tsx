import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend } from 'recharts';
import { motion } from 'framer-motion';
import type { Model } from '../../types/types';

interface ComparisonRadarProps {
  models: Model[];
  title?: string;
}

// Art Professional Color System
const COLORS = [
  '#334155', // Ink Slate
  '#C65D4D', // Coral Red
  '#5F8A50', // Sage Green
  '#B8923D', // Amber Gold
  '#C87F4A', // Warm Bronze
  '#6B8E7A'  // Patina Green
];

export default function ComparisonRadar({ models, title = "Model Comparison" }: ComparisonRadarProps) {
  // 准备雷达图数据
  const radarData = [
    { dimension: 'Rhythm', fullMark: 100 },
    { dimension: 'Composition', fullMark: 100 },
    { dimension: 'Narrative', fullMark: 100 },
    { dimension: 'Emotion', fullMark: 100 },
    { dimension: 'Creativity', fullMark: 100 },
    { dimension: 'Cultural', fullMark: 100 },
  ];

  // 为每个模型添加数据
  const data = radarData.map(item => {
    const point: Record<string, string | number> = { dimension: item.dimension };
    models.forEach((model, index) => {
      switch (item.dimension) {
        case 'Rhythm':
          point[`model${index}`] = model.metrics.rhythm;
          break;
        case 'Composition':
          point[`model${index}`] = model.metrics.composition;
          break;
        case 'Narrative':
          point[`model${index}`] = model.metrics.narrative;
          break;
        case 'Emotion':
          point[`model${index}`] = model.metrics.emotion;
          break;
        case 'Creativity':
          point[`model${index}`] = model.metrics.creativity;
          break;
        case 'Cultural':
          point[`model${index}`] = model.metrics.cultural;
          break;
      }
    });
    return point;
  });

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, rotateX: -10 }}
      animate={{ opacity: 1, scale: 1, rotateX: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg"
    >
      <h3 className="text-h3 text-gray-900 dark:text-gray-100 mb-6">
        {title}
      </h3>

      <ResponsiveContainer width="100%" height={400}>
        <RadarChart data={data}>
          <PolarGrid 
            gridType="polygon"
            radialLines={true}
            stroke="rgba(142,142,147,0.3)"
            strokeWidth={1.5}
            className="animate-gentle-float"
          />
          <PolarAngleAxis 
            dataKey="dimension"
            tick={{
              fill: '#334155',
              fontSize: 13,
              fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif'
            }}
            className="font-medium"
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tickCount={6}
            tick={{ 
              fill: 'rgba(142,142,147,0.7)', 
              fontSize: 11,
              fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif'
            }}
          />
          
          {models.map((model, index) => (
            <Radar
              key={model.id}
              name={model.name}
              dataKey={`model${index}`}
              stroke={COLORS[index]}
              fill={COLORS[index]}
              fillOpacity={0.15}
              strokeWidth={2}
              dot={{ 
                r: 5, 
                fill: COLORS[index], 
                strokeWidth: 2, 
                stroke: '#FFFFFF'
              }}
            />
          ))}
          
          <Legend
            wrapperStyle={{
              paddingTop: '24px',
              fontSize: '14px',
              fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif',
              fontWeight: '500'
            }}
            iconType="circle"
          />
        </RadarChart>
      </ResponsiveContainer>

      {/* 模型卡片 */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
        {models.map((model, index) => (
          <motion.div
            key={model.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
          >
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: COLORS[index] }}
            />
            <img
              src={model.avatar}
              alt={model.name}
              className="w-10 h-10 rounded-lg"
            />
            <div className="flex-1">
              <h4 className="font-medium text-gray-800 dark:text-gray-200">
                {model.name}
              </h4>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {model.organization} · Overall: {model.overallScore}
              </p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* 维度说明 */}
      <div className="mt-6 p-4 bg-slate-50 dark:bg-slate-900/20 rounded-lg">
        <h4 className="text-sm font-medium text-slate-900 dark:text-slate-400 mb-2">
          Evaluation Dimensions
        </h4>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs text-slate-700 dark:text-slate-500">
          <div>• Rhythm: Poetry & meter mastery</div>
          <div>• Composition: Visual art ability</div>
          <div>• Narrative: Story construction</div>
          <div>• Emotion: Emotional expression</div>
          <div>• Creativity: Innovation level</div>
          <div>• Cultural: Cultural understanding</div>
        </div>
      </div>
    </motion.div>
  );
}
