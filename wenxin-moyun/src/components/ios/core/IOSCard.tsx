import React from 'react';
import { motion } from 'framer-motion';

interface IOSCardProps {
  children: React.ReactNode;
  variant?: 'flat' | 'elevated' | 'glass' | 'bordered';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  radius?: 'sm' | 'md' | 'lg' | 'xl';
  interactive?: boolean;
  onClick?: () => void;
  className?: string;
  animate?: boolean;
  delay?: number;
}

export const IOSCard: React.FC<IOSCardProps> = ({
  children,
  variant = 'elevated',
  padding = 'md',
  radius = 'lg',
  interactive = false,
  onClick,
  className = '',
  animate = true,
  delay = 0,
}) => {
  // Padding classes
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };
  
  // Radius classes
  const radiusClasses = {
    sm: 'rounded-md',
    md: 'rounded-lg',
    lg: 'rounded-xl',
    xl: 'rounded-2xl',
  };
  
  // Variant-specific styles - Art Professional
  const getVariantClasses = () => {
    switch (variant) {
      case 'flat':
        return `
          bg-white dark:bg-[#1A1614]
          ${interactive ? 'hover:bg-gray-50 dark:hover:bg-[#211D1A]' : ''}
        `;

      case 'elevated':
        return `
          bg-white dark:bg-[#1A1614]
          shadow-sm hover:shadow-md
          border border-gray-100 dark:border-[#342E28]
          ${interactive ? 'hover:shadow-lg transform hover:-translate-y-0.5' : ''}
        `;

      case 'glass':
        return `
          bg-white/80 dark:bg-[#1A1614]/80
          backdrop-blur-xl
          border border-gray-200/50 dark:border-[#4A433C]/50
          shadow-sm
          ${interactive ? 'hover:bg-white/90 dark:hover:bg-[#1A1614]/90' : ''}
        `;

      case 'bordered':
        return `
          bg-white dark:bg-[#0F0D0B]
          border border-gray-200 dark:border-[#4A433C]
          ${interactive ? 'hover:border-gray-300 dark:hover:border-[#6B6259]' : ''}
        `;

      default:
        return '';
    }
  };
  
  // Combine classes
  const cardClasses = `
    ${paddingClasses[padding]}
    ${radiusClasses[radius]}
    ${getVariantClasses()}
    ${interactive ? 'cursor-pointer' : ''}
    transition-all duration-200
    ${className}
  `.replace(/\s+/g, ' ').trim();
  
  // Animation variants
  const animationVariants = animate ? {
    initial: { opacity: 0, y: 20 },
    animate: { 
      opacity: 1, 
      y: 0,
      transition: {
        delay: delay * 0.1,
        duration: 0.4,
        ease: 'easeOut' as const,
      }
    },
    whileHover: interactive ? {
      scale: 1.02,
      transition: { duration: 0.2 }
    } : {},
    whileTap: interactive ? {
      scale: 0.98,
      transition: { duration: 0.1 }
    } : {},
  } : {};
  
  const CardComponent = animate ? motion.div : 'div';
  
  return (
    <CardComponent
      className={cardClasses}
      onClick={interactive ? onClick : undefined}
      {...(animate ? animationVariants : {})}
    >
      {/* Glass morphism shine effect */}
      {variant === 'glass' && (
        <div className="absolute inset-0 rounded-inherit bg-gradient-to-br from-white/10 to-transparent pointer-events-none" />
      )}
      
      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
    </CardComponent>
  );
};

// Specialized card components
export const IOSCardHeader: React.FC<{
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  emoji?: React.ReactNode;
  className?: string;
}> = ({ title, subtitle, action, emoji, className = '' }) => {
  return (
    <div className={`flex items-start justify-between mb-3 ${className}`}>
      <div className="flex items-start gap-3">
        {emoji && (
          <div className="flex-shrink-0">
            {emoji}
          </div>
        )}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {title}
          </h3>
          {subtitle && (
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
              {subtitle}
            </p>
          )}
        </div>
      </div>
      {action && (
        <div className="flex-shrink-0">
          {action}
        </div>
      )}
    </div>
  );
};

export const IOSCardContent: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => {
  return (
    <div className={`text-gray-600 dark:text-gray-300 ${className}`}>
      {children}
    </div>
  );
};

export const IOSCardFooter: React.FC<{
  children: React.ReactNode;
  divider?: boolean;
  className?: string;
}> = ({ children, divider = true, className = '' }) => {
  return (
    <div className={`
      ${divider ? 'border-t border-gray-200 dark:border-gray-700 pt-3 mt-4' : 'mt-3'}
      ${className}
    `}>
      {children}
    </div>
  );
};

// Card Grid Layout Helper - 增强响应式支持
export const IOSCardGrid: React.FC<{
  children: React.ReactNode;
  columns?: 1 | 2 | 3 | 4;
  gap?: 'sm' | 'md' | 'lg';
  className?: string;
}> = ({ children, columns = 3, gap = 'md', className = '' }) => {
  // 响应式列数 - 添加 xs 断点支持 (475px)
  const columnClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 xs:grid-cols-2',
    3: 'grid-cols-1 xs:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
  };

  // 响应式间距 - 移动端更紧凑
  const gapClasses = {
    sm: 'gap-2 xs:gap-3 md:gap-3',
    md: 'gap-3 xs:gap-4 md:gap-5',
    lg: 'gap-4 xs:gap-5 md:gap-6',
  };

  return (
    <div className={`grid ${columnClasses[columns]} ${gapClasses[gap]} ${className}`}>
      {children}
    </div>
  );
};
