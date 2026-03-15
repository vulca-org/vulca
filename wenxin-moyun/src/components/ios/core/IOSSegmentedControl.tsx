import React from 'react';
import { motion } from 'framer-motion';
import { liquidGlass } from '../utils/iosTheme';
import { iosAnimations } from '../utils/animations';
import { EmojiIcon } from './EmojiIcon';

export interface SegmentItem {
  id: string;
  label: string;
  emoji?: string;
  icon?: React.ReactNode;
  disabled?: boolean;
  value?: string | number;
}

export interface IOSSegmentedControlProps {
  segments: string[] | SegmentItem[];
  selectedIndex: number;
  onChange: (index: number, segment: string | SegmentItem) => void;
  size?: 'compact' | 'regular' | 'large';
  style?: 'plain' | 'bordered' | 'filled';
  disabled?: boolean;
  className?: string;
}

export const IOSSegmentedControl: React.FC<IOSSegmentedControlProps> = ({
  segments,
  selectedIndex,
  onChange,
  size = 'regular',
  style = 'filled',
  disabled = false,
  className = '',
}) => {
  // Normalize segments to SegmentItem array
  const normalizedSegments: SegmentItem[] = segments.map((segment, index) => {
    if (typeof segment === 'string') {
      return {
        id: `segment-${index}`,
        label: segment,
        value: segment
      };
    }
    return segment;
  });

  // Size configurations - iOS HIG 44px minimum touch target
  const sizeConfig = {
    compact: {
      height: 'h-11',       // 44px (原 h-7 28px)
      padding: 'px-3',
      text: 'text-xs',
      gap: 'gap-1'
    },
    regular: {
      height: 'h-11',       // 44px (原 h-8 32px)
      padding: 'px-4',
      text: 'text-sm',
      gap: 'gap-2'
    },
    large: {
      height: 'h-12',       // 48px (原 h-10 40px)
      padding: 'px-5',
      text: 'text-base',
      gap: 'gap-3'
    }
  };

  // Style configurations - Art Professional palette
  const styleConfig = {
    plain: {
      container: 'bg-transparent',
      selected: 'bg-slate-700 text-white',
      unselected: 'text-slate-600 hover:bg-slate-50 dark:hover:bg-slate-900/20'
    },
    bordered: {
      container: `${liquidGlass.borders.regular} bg-transparent`,
      selected: 'bg-slate-700 text-white',
      unselected: 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
    },
    filled: {
      container: `${liquidGlass.opacity.regular} ${liquidGlass.borders.subtle}`,
      selected: 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm',
      unselected: 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
    }
  };

  const config = sizeConfig[size];
  const styleConf = styleConfig[style];

  return (
    <div
      className={`
        relative inline-flex items-center
        ${config.height}
        rounded-lg
        ${styleConf.container}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        transition-all duration-200
        ${className}
      `}
      style={{
        backdropFilter: style === 'filled' ? 'blur(10px) saturate(150%)' : undefined,
        WebkitBackdropFilter: style === 'filled' ? 'blur(10px) saturate(150%)' : undefined
      }}
    >
      {/* Background indicator for selected segment */}
      {style === 'filled' && (
        <motion.div
          className="absolute inset-y-0.5 z-0 px-0.5"
          initial={false}
          animate={{
            x: `${selectedIndex * 100}%`,
          }}
          transition={{
            ...iosAnimations.spring,
            duration: 0.3,
          }}
          style={{
            width: `${100 / normalizedSegments.length}%`,
          }}
        >
          <div className="w-full h-full rounded-md bg-white dark:bg-gray-800 shadow-sm" />
        </motion.div>
      )}

      {/* Segments */}
      {normalizedSegments.map((segment, index) => {
        const isSelected = index === selectedIndex;
        const isDisabled = disabled || segment.disabled;

        return (
          <motion.button
            key={segment.id}
            disabled={isDisabled}
            className={`
              relative z-10 flex items-center justify-center
              flex-1 ${config.height} ${config.padding}
              rounded-md
              font-medium ${config.text}
              transition-colors duration-200
              focus:outline-none focus:ring-2 focus:ring-slate-500/20
              ${isDisabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}
              ${isSelected ? styleConf.selected : styleConf.unselected}
            `}
            onClick={() => !isDisabled && onChange(index, segment)}
            whileHover={!isDisabled ? { scale: 1.02 } : {}}
            whileTap={!isDisabled ? { scale: 0.98 } : {}}
            transition={iosAnimations.spring}
          >
            <div className={`flex items-center justify-center ${config.gap}`}>
              {/* Icon/Emoji */}
              {segment.emoji && (
                <EmojiIcon 
                  category="navigation" 
                  name={segment.emoji}
                  size={size === 'compact' ? 'xs' : 'sm'} 
                />
              )}
              {segment.icon && !segment.emoji && (
                <span className={size === 'compact' ? 'text-xs' : 'text-sm'}>
                  {segment.icon}
                </span>
              )}
              
              {/* Label */}
              <span className="leading-tight whitespace-nowrap">
                {segment.label}
              </span>
            </div>
          </motion.button>
        );
      })}
    </div>
  );
};

export default IOSSegmentedControl;
