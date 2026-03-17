import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Info, RotateCcw } from 'lucide-react';
import { IOSSlider, IOSButton, IOSCard, IOSCardHeader, IOSCardContent, EmojiIcon } from '../ios';

interface Weight {
  name: string;
  key: string;
  value: number;
  color: string;
  description?: string;
}

interface WeightSliderProps {
  label: string;
  weights: Weight[];
  onChange: (weights: Weight[]) => void;
  showReset?: boolean;
  showTotal?: boolean;
}

export default function WeightSlider({
  label,
  weights,
  onChange,
  showReset = true,
  showTotal = true
}: WeightSliderProps) {
  const [localWeights, setLocalWeights] = useState(weights);
  const [hoveredWeight, setHoveredWeight] = useState<string | null>(null);

  useEffect(() => {
    setLocalWeights(weights);
  }, [weights]);

  const handleWeightChange = (key: string, value: number) => {
    const newWeights = localWeights.map(w => 
      w.key === key ? { ...w, value } : w
    );
    setLocalWeights(newWeights);
    onChange(newWeights);
  };

  const resetWeights = () => {
    const equalWeight = 100 / weights.length;
    const newWeights = localWeights.map(w => ({
      ...w,
      value: equalWeight
    }));
    setLocalWeights(newWeights);
    onChange(newWeights);
  };

  const normalizeWeights = () => {
    const total = localWeights.reduce((sum, w) => sum + w.value, 0);
    if (total === 0) return;
    
    const newWeights = localWeights.map(w => ({
      ...w,
      value: (w.value / total) * 100
    }));
    setLocalWeights(newWeights);
    onChange(newWeights);
  };

  const totalWeight = localWeights.reduce((sum, w) => sum + w.value, 0);
  const isNormalized = Math.abs(totalWeight - 100) < 0.01;

  return (
    <IOSCard variant="glass" padding="lg">
      <IOSCardHeader
        title={label}
        emoji={<EmojiIcon category="actions" name="edit" size="md" />}
        action={
          <div className="flex items-center gap-2">
            {showTotal && (
              <span className={`text-xs font-medium px-2 py-1 rounded ${
                isNormalized 
                  ? 'bg-[#5F8A50]/10 dark:bg-[#5F8A50]/10 text-[#5F8A50] dark:text-[#87A878]'
                  : 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-600 dark:text-yellow-400'
              }`}>
                Total: {totalWeight.toFixed(1)}%
              </span>
            )}
            {showReset && (
              <IOSButton
                onClick={resetWeights}
                variant="text"
                size="sm"
                title="Reset to Equal Weights"
              >
                <RotateCcw className="w-4 h-4" />
              </IOSButton>
            )}
          </div>
        }
      />
      <IOSCardContent>

        <div className="space-y-4">
          {localWeights.map((weight) => (
            <div 
              key={weight.key}
              className="space-y-2"
              onMouseEnter={() => setHoveredWeight(weight.key)}
              onMouseLeave={() => setHoveredWeight(null)}
            >
              <IOSSlider
                value={weight.value}
                onChange={(value) => handleWeightChange(weight.key, value)}
                min={0}
                max={100}
                step={5}
                label={weight.name}
                showValue={true}
                formatValue={(v) => `${v.toFixed(1)}%`}
                color="primary"
                size="md"
              />
              
              {weight.description && hoveredWeight === weight.key && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="text-xs text-gray-600 dark:text-gray-400 p-2 bg-gray-100 dark:bg-gray-800 rounded-lg"
                >
                  <Info className="w-3 h-3 text-gray-400 inline mr-1" />
                  {weight.description}
                </motion.div>
              )}

              {/* Quick preset buttons */}
              <div className="flex gap-1">
                {[0, 25, 50, 75, 100].map((val) => (
                  <IOSButton
                    key={val}
                    onClick={() => handleWeightChange(weight.key, val)}
                    variant={weight.value === val ? 'primary' : 'secondary'}
                    size="sm"
                    className="flex-1 text-xs"
                  >
                    {val}%
                  </IOSButton>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Normalize button */}
        {!isNormalized && showTotal && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="pt-2"
          >
            <IOSButton
              onClick={normalizeWeights}
              variant="primary"
              size="lg"
              className="w-full"
              glassMorphism
            >
              <EmojiIcon category="actions" name="refresh" size="sm" />
              Normalize to 100%
            </IOSButton>
          </motion.div>
        )}

        {/* Weight Distribution Chart */}
        <div className="mt-4 p-4 ios-glass rounded-lg">
          <div className="text-center mb-3">
            <EmojiIcon category="rating" name="chart" size="md" />
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mt-1">
              Weight Distribution
            </h4>
          </div>
          
          <div className="flex items-center justify-center">
            <div className="relative w-32 h-32">
              <svg viewBox="0 0 100 100" className="transform -rotate-90">
                {localWeights.reduce((acc, weight) => {
                  const startAngle = acc.angle;
                  const angle = (weight.value / 100) * 360;
                  const endAngle = startAngle + angle;
                  
                  const startRadians = (startAngle * Math.PI) / 180;
                  const endRadians = (endAngle * Math.PI) / 180;
                  
                  const largeArcFlag = angle > 180 ? 1 : 0;
                  
                  const x1 = 50 + 40 * Math.cos(startRadians);
                  const y1 = 50 + 40 * Math.sin(startRadians);
                  const x2 = 50 + 40 * Math.cos(endRadians);
                  const y2 = 50 + 40 * Math.sin(endRadians);
                  
                  acc.elements.push(
                    <path
                      key={weight.key}
                      d={`M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArcFlag} 1 ${x2} ${y2} Z`}
                      fill={weight.color}
                      opacity={hoveredWeight === weight.key ? 1 : 0.8}
                      onMouseEnter={() => setHoveredWeight(weight.key)}
                      onMouseLeave={() => setHoveredWeight(null)}
                      className="transition-opacity cursor-pointer"
                    />
                  );
                  
                  acc.angle = endAngle;
                  return acc;
                }, { angle: 0, elements: [] as React.JSX.Element[] }).elements}
                
                {/* Center circle */}
                <circle 
                  cx="50" 
                  cy="50" 
                  r="20" 
                  className="fill-white dark:fill-gray-800"
                />
              </svg>
              
              {/* Center text */}
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                  Weights
                </span>
              </div>
            </div>
          </div>

          {/* Legend */}
          <div className="mt-3 grid grid-cols-2 gap-2">
            {localWeights.map((weight) => (
              <div 
                key={weight.key}
                className="flex items-center gap-2 text-xs cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 p-1 rounded transition-colors"
                onMouseEnter={() => setHoveredWeight(weight.key)}
                onMouseLeave={() => setHoveredWeight(null)}
              >
                <div 
                  className="w-3 h-3 rounded-sm"
                  style={{ backgroundColor: weight.color }}
                />
                <span className="text-gray-600 dark:text-gray-400">
                  {weight.name}: {weight.value.toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </IOSCardContent>
    </IOSCard>
  );
}
