import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { chartColors } from '../../config/chartTheme';

interface RangeBarProps {
  label: string;
  value: number;
  min: number;
  max: number;
  average?: number;
  benchmark?: number;
  showTrend?: boolean;
}

const RangeBar: React.FC<RangeBarProps> = ({
  label,
  value,
  min,
  max,
  average,
  benchmark,
  showTrend = false
}) => {
  const range = max - min;
  const valuePosition = ((value - min) / range) * 100;
  const averagePosition = average ? ((average - min) / range) * 100 : null;
  const benchmarkPosition = benchmark ? ((benchmark - min) / range) * 100 : null;

  const getTrendIcon = () => {
    if (!benchmark) return null;
    const diff = value - benchmark;
    if (Math.abs(diff) < 1) return <Minus className="w-4 h-4 text-neutral-500" />;
    if (diff > 0) return <TrendingUp className="w-4 h-4 text-cultural-sage-500" />;
    return <TrendingDown className="w-4 h-4 text-cultural-coral-500" />;
  };

  const getValueColor = () => {
    const ratio = (value - min) / range;
    if (ratio < 0.3) return chartColors.primary[4]; // error color
    if (ratio < 0.5) return chartColors.primary[3]; // warning color
    if (ratio < 0.8) return chartColors.primary[2]; // success color
    return chartColors.primary[0]; // primary color for excellent
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="mb-4"
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-body font-medium text-neutral-700">{label}</span>
        <div className="flex items-center gap-2">
          <span className="text-h3 font-bold" style={{ color: getValueColor() }}>
            {value.toFixed(1)}
          </span>
          {showTrend && getTrendIcon()}
        </div>
      </div>
      
      <div className="relative">
        {/* 背景区间条 */}
        <div className="h-8 bg-gradient-to-r from-accent-100 via-accent-200 to-accent-100 rounded-full relative overflow-hidden">
          {/* 最小值和最大值标记 */}
          <div className="absolute inset-0 flex items-center justify-between px-2 text-caption text-neutral-600">
            <span>{min}</span>
            <span>{max}</span>
          </div>
          
          {/* 平均值线 */}
          {averagePosition !== null && (
            <motion.div
              initial={{ scaleY: 0 }}
              animate={{ scaleY: 1 }}
              transition={{ delay: 0.3 }}
              className="absolute top-0 bottom-0 w-0.5 bg-neutral-600"
              style={{ left: `${averagePosition}%` }}
              title={`平均值: ${average}`}
            />
          )}
          
          {/* 基准值线 */}
          {benchmarkPosition !== null && (
            <motion.div
              initial={{ scaleY: 0 }}
              animate={{ scaleY: 1 }}
              transition={{ delay: 0.4 }}
              className="absolute top-0 bottom-0 w-1 bg-slate-400 opacity-60"
              style={{ left: `${benchmarkPosition}%` }}
              title={`基准值: ${benchmark}`}
            />
          )}
          
          {/* 当前值指示器 */}
          <motion.div
            initial={{ left: '0%' }}
            animate={{ left: `${valuePosition}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2"
          >
            <div 
              className="w-4 h-4 rounded-full shadow-lg border-2 border-white"
              style={{ backgroundColor: getValueColor() }}
            />
            <motion.div
              animate={{ scale: [1, 1.5, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="absolute inset-0 rounded-full opacity-30"
              style={{ backgroundColor: getValueColor() }}
            />
          </motion.div>
        </div>
        
        {/* 数值标签 */}
        <div className="flex justify-between mt-1 text-caption text-neutral-500">
          <span>最低</span>
          {average && <span className="ml-auto mr-2">平均: {average.toFixed(1)}</span>}
          <span>最高</span>
        </div>
      </div>
    </motion.div>
  );
};

export default RangeBar;
export { RangeBar };