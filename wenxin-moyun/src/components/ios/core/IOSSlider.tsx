import React, { useState, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { iosAnimations } from '../utils/animations';

export interface IOSSliderProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'green' | 'orange' | 'red';
  showValue?: boolean;
  className?: string;
  label?: string;
  formatValue?: (value: number) => string;
}

export const IOSSlider: React.FC<IOSSliderProps> = ({
  value,
  onChange,
  min = 0,
  max = 100,
  step = 1,
  disabled = false,
  size = 'md',
  color = 'primary',
  showValue = false,
  className = '',
  label,
  formatValue = (v) => v.toString(),
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const sliderRef = useRef<HTMLDivElement>(null);

  // Size configurations - iOS HIG 44px minimum touch target
  // Visual thumb stays small, but touch area is expanded via padding
  const sizeConfig = {
    sm: {
      height: 'h-1',
      thumbSize: 'w-5 h-5',
      thumbTouchArea: 'min-w-[44px] min-h-[44px]', // Touch target expansion
      trackHeight: 4,
    },
    md: {
      height: 'h-2',
      thumbSize: 'w-6 h-6',
      thumbTouchArea: 'min-w-[44px] min-h-[44px]', // Touch target expansion
      trackHeight: 8,
    },
    lg: {
      height: 'h-3',
      thumbSize: 'w-7 h-7',
      thumbTouchArea: 'min-w-[48px] min-h-[48px]', // Larger touch target for lg
      trackHeight: 12,
    },
  };

  // Color configurations - Art Professional palette
  const colorConfig = {
    primary: 'bg-slate-600',
    green: 'bg-[#5F8A50]',
    orange: 'bg-amber-600',
    red: 'bg-[#C65D4D]',
  };

  const config = sizeConfig[size];
  const trackColor = colorConfig[color];

  // Calculate percentage
  const percentage = ((value - min) / (max - min)) * 100;

  // Handle slider interaction
  const updateValue = useCallback((clientX: number) => {
    if (!sliderRef.current || disabled) return;

    const rect = sliderRef.current.getBoundingClientRect();
    const newPercentage = Math.max(0, Math.min(100, ((clientX - rect.left) / rect.width) * 100));
    const newValue = min + (newPercentage / 100) * (max - min);
    const steppedValue = Math.round(newValue / step) * step;
    
    onChange(Math.max(min, Math.min(max, steppedValue)));
  }, [min, max, step, onChange, disabled]);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (disabled) return;
    setIsDragging(true);
    updateValue(e.clientX);
  };

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isDragging && !disabled) {
      updateValue(e.clientX);
    }
  }, [isDragging, disabled, updateValue]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Add global mouse events when dragging
  React.useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  const sliderElement = (
    <div className={`relative ${className}`}>
      {/* Track */}
      <div
        ref={sliderRef}
        className={`
          relative
          ${config.height}
          bg-gray-200 dark:bg-gray-700
          rounded-full
          cursor-pointer
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
        onMouseDown={handleMouseDown}
      >
        {/* Active Track */}
        <motion.div
          className={`
            absolute top-0 left-0
            ${config.height}
            ${trackColor}
            rounded-full
            transition-all duration-200
          `}
          style={{ width: `${percentage}%` }}
        />
        
        {/* Track Highlight */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-white/20 to-transparent pointer-events-none" />
        
        {/* Thumb wrapper with expanded touch area - iOS HIG 44px minimum */}
        <motion.div
          className={`
            absolute top-1/2 transform -translate-y-1/2
            ${config.thumbTouchArea}
            flex items-center justify-center
            cursor-grab
            ${isDragging ? 'cursor-grabbing' : ''}
            ${disabled ? 'cursor-not-allowed' : ''}
          `}
          style={{
            left: `calc(${percentage}% - 22px)`, // Center the 44px touch area
          }}
          whileHover={disabled ? {} : { scale: 1.05 }}
          whileTap={disabled ? {} : { scale: 0.95 }}
          drag={disabled ? false : "x"}
          dragConstraints={sliderRef}
          dragElastic={0}
          onDrag={(_, info) => {
            if (!disabled && sliderRef.current) {
              const rect = sliderRef.current.getBoundingClientRect();
              const newPercentage = Math.max(0, Math.min(100, (info.point.x - rect.left) / rect.width * 100));
              const newValue = min + (newPercentage / 100) * (max - min);
              const steppedValue = Math.round(newValue / step) * step;
              onChange(Math.max(min, Math.min(max, steppedValue)));
            }
          }}
          transition={iosAnimations.spring}
        >
          {/* Visual thumb with Liquid Glass effect - Based on Figma iOS 26 */}
          <div
            className={`${config.thumbSize} rounded-full`}
            style={{
              // Liquid Glass effect from iOS 26
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%)',
              backdropFilter: 'blur(10px) saturate(180%)',
              WebkitBackdropFilter: 'blur(10px) saturate(180%)',
              boxShadow: `
                0 4px 12px rgba(0, 0, 0, 0.08),
                0 1px 3px rgba(0, 0, 0, 0.12),
                inset 0 1px 1px rgba(255, 255, 255, 0.8),
                inset 0 -1px 1px rgba(0, 0, 0, 0.04)
              `,
              border: '0.5px solid rgba(255, 255, 255, 0.3)'
            }}
          >
            {/* Liquid Glass inner reflection */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-br from-white/40 via-transparent to-transparent pointer-events-none" />
          </div>
        </motion.div>
      </div>
      
      {/* Value display */}
      {showValue && (
        <motion.div
          className="absolute -top-8 left-1/2 transform -translate-x-1/2 px-2 py-1 bg-gray-900 text-white text-xs rounded-md"
          style={{ left: `${percentage}%` }}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ 
            opacity: isDragging ? 1 : 0,
            scale: isDragging ? 1 : 0.8,
          }}
          transition={iosAnimations.spring}
        >
          {formatValue(value)}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-2 border-r-2 border-t-2 border-transparent border-t-gray-900" />
        </motion.div>
      )}
    </div>
  );

  // If no label, return just the slider
  if (!label) {
    return sliderElement;
  }

  // Return slider with label
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className={`
          text-base font-medium text-gray-900 dark:text-white
          ${disabled ? 'opacity-50' : ''}
        `}>
          {label}
        </label>
        <span className={`
          text-sm text-gray-500 dark:text-gray-400
          ${disabled ? 'opacity-50' : ''}
        `}>
          {formatValue(value)}
        </span>
      </div>
      {sliderElement}
    </div>
  );
};
