import React from 'react';
import { motion } from 'framer-motion';
import { iosAnimations } from '../utils/animations';

export interface IOSToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'green' | 'orange' | 'red';
  className?: string;
  label?: string;
  description?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const IOSToggle: React.FC<IOSToggleProps> = ({
  checked,
  onChange,
  disabled = false,
  size = 'md',
  color = 'green',
  className = '',
  label,
  description,
  leftIcon,
  rightIcon,
}) => {
  // Size configurations - iOS HIG 44px minimum touch target
  // Visual toggle stays compact, touch area expanded via wrapper
  const sizeConfig = {
    sm: {
      width: 'w-10',
      height: 'h-6',
      thumbSize: 'w-5 h-5',
      padding: 'p-0.5',
      translateX: 16,
      touchArea: 'min-h-[44px]', // Touch target expansion
    },
    md: {
      width: 'w-12',
      height: 'h-7',
      thumbSize: 'w-6 h-6',
      padding: 'p-0.5',
      translateX: 20,
      touchArea: 'min-h-[44px]', // Touch target expansion
    },
    lg: {
      width: 'w-14',
      height: 'h-8',
      thumbSize: 'w-7 h-7',
      padding: 'p-0.5',
      translateX: 24,
      touchArea: 'min-h-[44px]', // Touch target expansion
    },
  };

  // Color configurations - Art Professional palette
  const colorConfig = {
    primary: checked ? 'bg-slate-600' : 'bg-gray-300',
    green: checked ? 'bg-[#5F8A50]' : 'bg-gray-300',
    orange: checked ? 'bg-amber-600' : 'bg-gray-300',
    red: checked ? 'bg-[#C65D4D]' : 'bg-gray-300',
  };

  const config = sizeConfig[size];
  const bgColor = colorConfig[color];

  const handleToggle = () => {
    if (!disabled) {
      onChange(!checked);
    }
  };

  const toggleElement = (
    <motion.div
      className={`
        ${config.touchArea}
        inline-flex items-center justify-center
        cursor-pointer
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
      `}
      onClick={handleToggle}
      whileTap={disabled ? {} : { scale: 0.95 }}
      transition={iosAnimations.spring}
    >
      {/* Visual toggle */}
      <div
        className={`
          relative inline-flex items-center
          ${config.width} ${config.height}
          ${config.padding}
          rounded-full
          transition-colors duration-200
          ${bgColor}
        `}
      >
      {/* Toggle Background Gradient Effect */}
      <div className="absolute inset-0 rounded-full bg-gradient-to-br from-white/20 to-transparent pointer-events-none" />
      
      {/* Left Icon */}
      {leftIcon && (
        <div className="absolute left-1 top-1/2 transform -translate-y-1/2 pointer-events-none opacity-60">
          {leftIcon}
        </div>
      )}
      
      {/* Right Icon */}
      {rightIcon && (
        <div className="absolute right-1 top-1/2 transform -translate-y-1/2 pointer-events-none opacity-60">
          {rightIcon}
        </div>
      )}
      
      {/* Toggle Thumb */}
      <motion.div
        className={`
          ${config.thumbSize}
          ios-glass liquid-glass-container
          rounded-full
          shadow-lg
        `}
        animate={{
          x: checked ? config.translateX : 2,
        }}
        transition={{
          type: "spring",
          stiffness: 500,
          damping: 30,
          mass: 0.8
        }}
      >
        {/* Thumb inner shadow */}
        <div className="absolute inset-0 rounded-full shadow-inner bg-gradient-to-br from-gray-50/50 to-transparent" />
      </motion.div>
      </div>
    </motion.div>
  );

  // If no label, return just the toggle
  if (!label) {
    return toggleElement;
  }

  // Return toggle with label and description
  return (
    <div className={`flex items-start gap-3 ${className}`}>
      {toggleElement}
      <div className="flex-1">
        <label 
          className={`
            text-base font-medium text-gray-900 dark:text-white cursor-pointer
            ${disabled ? 'opacity-50' : ''}
          `}
          onClick={handleToggle}
        >
          {label}
        </label>
        {description && (
          <p className={`
            text-sm text-gray-500 dark:text-gray-400 mt-1
            ${disabled ? 'opacity-50' : ''}
          `}>
            {description}
          </p>
        )}
      </div>
    </div>
  );
};
