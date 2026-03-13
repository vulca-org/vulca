import React, { useMemo } from 'react';
import type { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { shouldUseGlassEffect, detectDevicePerformance } from '@/utils/devicePerformance';

interface LiquidGlassProps {
  children: ReactNode;
  className?: string;
  variant?: 'light' | 'dark' | 'colored';
  color?: 'blue' | 'green' | 'orange' | 'purple' | 'pink';
  intensity?: 'subtle' | 'medium' | 'strong';
  animated?: boolean;
}

const LiquidGlass: React.FC<LiquidGlassProps> = ({
  children,
  className = '',
  variant = 'light',
  color = 'blue',
  intensity = 'medium',
  animated = false
}) => {
  // Color configurations
  const colorConfig = {
    blue: {
      light: 'from-slate-50/70 to-slate-100/70',
      dark: 'from-slate-900/20 to-slate-800/20',
      colored: 'from-slate-500/20 to-slate-400/20',
      border: 'border-slate-200/30 dark:border-slate-700/30',
      glow: 'shadow-slate-600/10'
    },
    green: {
      light: 'from-green-50/70 to-emerald-50/70',
      dark: 'from-green-900/20 to-emerald-900/20',
      colored: 'from-green-400/20 to-emerald-400/20',
      border: 'border-green-200/30 dark:border-green-700/30',
      glow: 'shadow-green-500/10'
    },
    orange: {
      light: 'from-orange-50/70 to-amber-50/70',
      dark: 'from-orange-900/20 to-amber-900/20',
      colored: 'from-orange-400/20 to-amber-400/20',
      border: 'border-orange-200/30 dark:border-orange-700/30',
      glow: 'shadow-orange-500/10'
    },
    purple: {
      light: 'from-amber-50/70 to-pink-50/70',
      dark: 'from-amber-900/20 to-pink-900/20',
      colored: 'from-amber-500/20 to-pink-400/20',
      border: 'border-[#C87F4A]/30 dark:border-[#C87F4A]/20',
      glow: 'shadow-amber-600/10'
    },
    pink: {
      light: 'from-pink-50/70 to-rose-50/70',
      dark: 'from-pink-900/20 to-rose-900/20',
      colored: 'from-pink-400/20 to-rose-400/20',
      border: 'border-pink-200/30 dark:border-pink-700/30',
      glow: 'shadow-pink-500/10'
    }
  };

  // 设备性能检测 - 低端设备禁用blur效果
  const useGlassEffect = useMemo(() => shouldUseGlassEffect(), []);
  const performanceLevel = useMemo(() => detectDevicePerformance(), []);

  // Intensity configurations - 根据设备性能调整
  const intensityConfig = useMemo(() => {
    // 低端设备: 完全禁用blur，使用纯色背景
    if (!useGlassEffect) {
      return {
        subtle: { blur: '', opacity: 'bg-opacity-90', shadow: 'shadow-sm' },
        medium: { blur: '', opacity: 'bg-opacity-90', shadow: 'shadow-md' },
        strong: { blur: '', opacity: 'bg-opacity-95', shadow: 'shadow-lg' },
      };
    }

    // 中等设备: 降低blur强度
    if (performanceLevel === 'medium') {
      return {
        subtle: { blur: 'backdrop-blur-[2px]', opacity: 'bg-opacity-40', shadow: 'shadow-sm' },
        medium: { blur: 'backdrop-blur-sm', opacity: 'bg-opacity-60', shadow: 'shadow-md' },
        strong: { blur: 'backdrop-blur-md', opacity: 'bg-opacity-75', shadow: 'shadow-lg' },
      };
    }

    // 高端设备: 完整效果
    return {
      subtle: { blur: 'backdrop-blur-sm', opacity: 'bg-opacity-30', shadow: 'shadow-sm' },
      medium: { blur: 'backdrop-blur-md', opacity: 'bg-opacity-50', shadow: 'shadow-md' },
      strong: { blur: 'backdrop-blur-lg', opacity: 'bg-opacity-70', shadow: 'shadow-lg' },
    };
  }, [useGlassEffect, performanceLevel]);

  const colors = colorConfig[color];
  const intensityStyles = intensityConfig[intensity];
  const bgGradient = variant === 'light' ? colors.light : variant === 'dark' ? colors.dark : colors.colored;

  const containerVariants = {
    initial: { opacity: 0, scale: 0.98 },
    animate: { 
      opacity: 1, 
      scale: 1,
      transition: {
        duration: 0.3,
        ease: "easeInOut" as const
      }
    },
    hover: animated ? {
      scale: 1.01,
      transition: {
        duration: 0.2,
        ease: "easeInOut" as const
      }
    } : {}
  };

  const shimmerVariants = {
    initial: { x: '-100%' },
    animate: {
      x: '200%',
      transition: {
        duration: 3,
        ease: "linear" as const,
        repeat: Infinity,
        repeatDelay: 5
      }
    }
  };

  return (
    <motion.div
      className={`
        relative overflow-hidden rounded-2xl
        bg-gradient-to-br ${bgGradient}
        ${intensityStyles.blur} ${intensityStyles.shadow}
        border ${colors.border}
        ${className}
      `}
      variants={containerVariants}
      initial="initial"
      animate="animate"
      whileHover="hover"
    >
      {/* Glass shimmer effect - 仅在高端设备和启用动画时显示 */}
      {animated && useGlassEffect && performanceLevel === 'high' && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12"
          variants={shimmerVariants}
          initial="initial"
          animate="animate"
        />
      )}

      {/* Noise texture for authenticity */}
      <div 
        className="absolute inset-0 opacity-[0.015] mix-blend-overlay"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='1'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Light refraction overlay */}
      <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/5 to-transparent pointer-events-none" />

      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
    </motion.div>
  );
};

// Specialized liquid glass card component
export const LiquidGlassCard: React.FC<{
  children: ReactNode;
  title?: string;
  subtitle?: string;
  icon?: ReactNode;
  className?: string;
  color?: 'blue' | 'green' | 'orange' | 'purple' | 'pink';
}> = ({ children, title, subtitle, icon, className = '', color = 'blue' }) => {
  return (
    <LiquidGlass
      variant="light"
      color={color}
      intensity="medium"
      animated
      className={`p-6 ${className}`}
    >
      {(title || subtitle || icon) && (
        <div className="flex items-start justify-between mb-4">
          <div>
            {title && (
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {subtitle}
              </p>
            )}
          </div>
          {icon && (
            <div className="ml-4">
              {icon}
            </div>
          )}
        </div>
      )}
      {children}
    </LiquidGlass>
  );
};

// Liquid glass button component
export const LiquidGlassButton: React.FC<{
  children: ReactNode;
  onClick?: () => void;
  color?: 'blue' | 'green' | 'orange' | 'purple' | 'pink';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}> = ({ children, onClick, color = 'blue', size = 'md', className = '' }) => {
  const sizeConfig = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  return (
    <motion.button
      onClick={onClick}
      className={`relative ${className}`}
      whileTap={{ scale: 0.98 }}
    >
      <LiquidGlass
        variant="colored"
        color={color}
        intensity="strong"
        animated
        className={`${sizeConfig[size]} font-medium text-white`}
      >
        {children}
      </LiquidGlass>
    </motion.button>
  );
};

export default LiquidGlass;