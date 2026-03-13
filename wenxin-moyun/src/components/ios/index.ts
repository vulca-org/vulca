/**
 * iOS Component Library
 * Unified export for all iOS-style components
 */

// Core Components
export { IOSButton } from './core/IOSButton';
export type { IOSButtonProps } from './core/IOSButton';

export { 
  IOSCard, 
  IOSCardHeader, 
  IOSCardContent, 
  IOSCardFooter,
  IOSCardGrid 
} from './core/IOSCard';

export { 
  EmojiIcon,
  StatusEmoji,
  RankEmoji,
  TypeEmoji 
} from './core/EmojiIcon';

export { IOSToggle } from './core/IOSToggle';
export type { IOSToggleProps } from './core/IOSToggle';

export { IOSSlider } from './core/IOSSlider';
export type { IOSSliderProps } from './core/IOSSlider';

export { IOSRangeSlider } from './core/IOSRangeSlider';
export type { IOSRangeSliderProps } from './core/IOSRangeSlider';

export { IOSFilterPanel } from './core/IOSFilterPanel';
export type { 
  IOSFilterPanelProps, 
  IOSFilterConfig, 
  IOSFilterValues 
} from './core/IOSFilterPanel';

export { IOSAlert } from './core/IOSAlert';
export type { IOSAlertProps, IOSAlertAction } from './core/IOSAlert';

export { IOSTabBar } from './core/IOSTabBar';
export type { IOSTabBarProps, TabBarItem } from './core/IOSTabBar';

export { IOSSegmentedControl } from './core/IOSSegmentedControl';
export type { IOSSegmentedControlProps, SegmentItem } from './core/IOSSegmentedControl';

export { IOSSheet } from './core/IOSSheet';
export { useIOSSheet } from './core/useIOSSheet';
export type { IOSSheetProps } from './core/IOSSheet';


// Utils
export { 
  iosColors, 
  iosShadows, 
  iosRadius, 
  iosTypography, 
  iosTransitions, 
  iosSpacing,
  liquidGlass
} from './utils/iosTheme';

export { 
  iosAnimations, 
  hapticFeedback 
} from './utils/animations';

export {
  coreEmojis,
  getEmoji,
} from './utils/emojiMap';

// Type exports
export type {
  CoreEmojiCategory,
  EmojiKey,
} from './utils/emojiMap';

/**
 * Adapter exports for seamless migration
 * These allow existing code to work with new iOS components
 */

// Export iOS components with generic names for backward compatibility
export { IOSCard as Card } from './core/IOSCard';
