import React, { useState, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { iosAnimations } from '../utils/animations';

export interface IOSRangeSliderProps {
  value: [number, number];
  onChange: (value: [number, number]) => void;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'green' | 'orange' | 'red';
  showValues?: boolean;
  className?: string;
  label?: string;
  formatValue?: (value: number) => string;
  unit?: string;
}

export const IOSRangeSlider: React.FC<IOSRangeSliderProps> = ({
  value,
  onChange,
  min = 0,
  max = 100,
  step = 1,
  disabled = false,
  size = 'md',
  color = 'primary',
  showValues = false,
  className = '',
  label,
  formatValue = (v) => v.toString(),
  unit = '',
}) => {
  const [isDragging, setIsDragging] = useState<'min' | 'max' | null>(null);
  const sliderRef = useRef<HTMLDivElement>(null);

  // Size configurations - iOS HIG 44px minimum touch target
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

  // Calculate percentages
  const minPercentage = ((value[0] - min) / (max - min)) * 100;
  const maxPercentage = ((value[1] - min) / (max - min)) * 100;

  // Handle slider interaction
  const updateValue = useCallback((clientX: number, thumb: 'min' | 'max') => {
    if (!sliderRef.current || disabled) return;

    const rect = sliderRef.current.getBoundingClientRect();
    const newPercentage = Math.max(0, Math.min(100, ((clientX - rect.left) / rect.width) * 100));
    const newValue = min + (newPercentage / 100) * (max - min);
    const steppedValue = Math.round(newValue / step) * step;
    
    const clampedValue = Math.max(min, Math.min(max, steppedValue));

    if (thumb === 'min') {
      // Ensure min doesn't go above max
      const newMin = Math.min(clampedValue, value[1]);
      onChange([newMin, value[1]]);
    } else {
      // Ensure max doesn't go below min
      const newMax = Math.max(clampedValue, value[0]);
      onChange([value[0], newMax]);
    }
  }, [min, max, step, onChange, disabled, value]);

  const handleMouseDown = (e: React.MouseEvent, thumb: 'min' | 'max') => {
    if (disabled) return;
    e.preventDefault();
    setIsDragging(thumb);
    updateValue(e.clientX, thumb);
  };

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isDragging && !disabled) {
      updateValue(e.clientX, isDragging);
    }
  }, [isDragging, disabled, updateValue]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(null);
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

  const handleTrackClick = (e: React.MouseEvent) => {
    if (disabled || isDragging) return;
    
    const rect = sliderRef.current?.getBoundingClientRect();
    if (!rect) return;
    
    const clickPercentage = ((e.clientX - rect.left) / rect.width) * 100;
    const clickValue = min + (clickPercentage / 100) * (max - min);
    
    // Determine which thumb is closer
    const distanceToMin = Math.abs(clickValue - value[0]);
    const distanceToMax = Math.abs(clickValue - value[1]);
    
    const closerThumb = distanceToMin <= distanceToMax ? 'min' : 'max';
    updateValue(e.clientX, closerThumb);
  };

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
        onClick={handleTrackClick}
      >
        {/* Active Track */}
        <motion.div
          className={`
            absolute top-0
            ${config.height}
            ${trackColor}
            rounded-full
            transition-all duration-200
          `}
          style={{ 
            left: `${minPercentage}%`,
            width: `${maxPercentage - minPercentage}%`
          }}
        />
        
        {/* Track Highlight */}
        <div 
          className="absolute inset-y-0 rounded-full bg-gradient-to-r from-white/20 to-transparent pointer-events-none"
          style={{ 
            left: `${minPercentage}%`,
            width: `${maxPercentage - minPercentage}%`
          }}
        />
        
        {/* Min Thumb - with expanded touch area */}
        <motion.div
          className={`
            absolute top-1/2 transform -translate-y-1/2
            ${config.thumbTouchArea}
            flex items-center justify-center
            cursor-grab
            z-10
            ${isDragging === 'min' ? 'cursor-grabbing' : ''}
            ${disabled ? 'cursor-not-allowed' : ''}
          `}
          style={{
            left: `calc(${minPercentage}% - 22px)` // Center the 44px touch area
          }}
          whileHover={disabled ? {} : { scale: 1.05 }}
          whileTap={disabled ? {} : { scale: 0.95 }}
          onMouseDown={(e) => handleMouseDown(e, 'min')}
          transition={iosAnimations.spring}
        >
          {/* Visual thumb */}
          <div className={`${config.thumbSize} bg-white rounded-full shadow-lg relative`}>
            {/* Thumb inner highlight */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-br from-white to-gray-50 shadow-inner" />
            {/* Thumb border */}
            <div className="absolute inset-0 rounded-full border border-gray-200/50" />
          </div>
        </motion.div>

        {/* Max Thumb - with expanded touch area */}
        <motion.div
          className={`
            absolute top-1/2 transform -translate-y-1/2
            ${config.thumbTouchArea}
            flex items-center justify-center
            cursor-grab
            z-10
            ${isDragging === 'max' ? 'cursor-grabbing' : ''}
            ${disabled ? 'cursor-not-allowed' : ''}
          `}
          style={{
            left: `calc(${maxPercentage}% - 22px)` // Center the 44px touch area
          }}
          whileHover={disabled ? {} : { scale: 1.05 }}
          whileTap={disabled ? {} : { scale: 0.95 }}
          onMouseDown={(e) => handleMouseDown(e, 'max')}
          transition={iosAnimations.spring}
        >
          {/* Visual thumb */}
          <div className={`${config.thumbSize} bg-white rounded-full shadow-lg relative`}>
            {/* Thumb inner highlight */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-br from-white to-gray-50 shadow-inner" />
            {/* Thumb border */}
            <div className="absolute inset-0 rounded-full border border-gray-200/50" />
          </div>
        </motion.div>
      </div>
      
      {/* Value displays */}
      {showValues && (
        <>
          {/* Min value */}
          <motion.div
            className="absolute -top-8 px-2 py-1 bg-gray-900 text-white text-xs rounded-md z-20"
            style={{ left: `${minPercentage}%`, transform: 'translateX(-50%)' }}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ 
              opacity: isDragging === 'min' ? 1 : 0,
              scale: isDragging === 'min' ? 1 : 0.8,
            }}
            transition={iosAnimations.spring}
          >
            {formatValue(value[0])}{unit}
            <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-2 border-r-2 border-t-2 border-transparent border-t-gray-900" />
          </motion.div>

          {/* Max value */}
          <motion.div
            className="absolute -top-8 px-2 py-1 bg-gray-900 text-white text-xs rounded-md z-20"
            style={{ left: `${maxPercentage}%`, transform: 'translateX(-50%)' }}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ 
              opacity: isDragging === 'max' ? 1 : 0,
              scale: isDragging === 'max' ? 1 : 0.8,
            }}
            transition={iosAnimations.spring}
          >
            {formatValue(value[1])}{unit}
            <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-2 border-r-2 border-t-2 border-transparent border-t-gray-900" />
          </motion.div>
        </>
      )}
    </div>
  );

  // If no label, return just the slider
  if (!label) {
    return sliderElement;
  }

  // Return slider with label and value range
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
          {formatValue(value[0])}{unit} - {formatValue(value[1])}{unit}
        </span>
      </div>
      {sliderElement}
    </div>
  );
};
