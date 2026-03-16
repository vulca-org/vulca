// Art Professional Theme System
// 温暖、专业、艺术品味的视觉风格
// 参考: 博物馆、画廊、艺术期刊的视觉语言

export const themes = {
  dark: {
    // 背景层级系统 - 暖色调深色
    bg: {
      base: '#0F0D0B',      // 暖黑 - 页面底色
      surface: '#1A1614',   // 暖表面 - 卡片/面板背景
      elevated: '#211D1A',  // 暖提升 - 悬浮层/模态框
      overlay: '#2A2521',   // 暖覆盖 - dropdown/tooltip
      hover: '#342E28',     // 暖悬停态背景
      active: '#3E3731',    // 暖激活态背景
    },

    // 边框系统 - 暖色调
    border: {
      default: '#4A433C',   // 暖边框 (对比度 3.2:1)
      muted: '#342E28',     // 弱边框 - 分割线
      strong: '#6B6259',    // 强边框 - 焦点/选中
      subtle: '#251F1B',    // 极弱边框
    },

    // 文字层级系统
    text: {
      primary: '#F5F0EB',   // 奶油白 - 标题/重要内容
      secondary: '#A89E94', // 暖灰 - 正文
      tertiary: '#7A726A',  // 辅助 - 说明/提示
      muted: '#524B44',     // 禁用文字
      inverse: '#0F0D0B',   // 反色文字
    },

    // 语义色彩系统 - Art Professional
    semantic: {
      primary: '#94A3B8',   // 墨石灰 - 主色/主按钮
      accent: '#DDA574',    // 暖铜棕亮 - 强调
      green: '#87A878',     // 鼠尾草绿 - 成功
      yellow: '#D4A84B',    // 琥珀黄 - 警告
      red: '#C97064',       // 珊瑚红 - 错误
      bronze: '#C87F4A',    // 暖铜棕 - 特殊亮点
      terracotta: '#9B6B56',// 陶土色 - 次要强调
      sage: '#87A878',      // 鼠尾草绿
    },

    // 图表专用色板 - 暖色调
    chart: {
      primary: '#C87F4A',   // 暖铜棕
      secondary: '#9B6B56', // 陶土色
      tertiary: '#87A878',  // 鼠尾草绿
      quaternary: '#D4A84B',// 琥珀黄
      series: [
        '#C87F4A', '#9B6B56', '#87A878', '#D4A84B',
        '#94A3B8', '#C97064', '#B8A089', '#7A9B76'
      ]
    },

    // 特殊用途
    special: {
      gold: 'linear-gradient(135deg, #D4A84B 0%, #C87F4A 100%)',     // 金牌
      silver: 'linear-gradient(135deg, #94A3B8 0%, #64748B 100%)',   // 银牌
      bronze: 'linear-gradient(135deg, #C87F4A 0%, #9B6B56 100%)',   // 铜牌
      gradient: 'linear-gradient(135deg, #334155 0%, #C87F4A 100%)', // 品牌渐变 (墨石灰→暖铜棕)
    }
  },

  light: {
    // 浅色主题 - 画廊风格
    bg: {
      base: '#FAF7F2',      // 奶油白背景
      surface: '#FFFFFF',   // 纯白表面
      elevated: '#FFFFFF',
      overlay: '#FFFFFF',
      hover: '#F5F0E8',
      active: '#EDE6DB',
    },

    border: {
      default: '#C9C2B8',   // 暖灰边框
      muted: '#E5DFD5',
      strong: '#9B9387',
      subtle: '#F0EBE3',
    },

    text: {
      primary: '#1E1B18',   // 暖黑
      secondary: '#524B44', // 暖深灰
      tertiary: '#7A726A',  // 暖中灰
      muted: '#A89E94',     // 暖浅灰
      inverse: '#FAF7F2',
    },

    // Semantic colors — Art Professional Light
    semantic: {
      primary: '#334155',   // Ink Slate
      accent: '#C87F4A',    // Warm Bronze
      green: '#5F8A50',     // Sage Green
      yellow: '#B8923D',    // Amber Gold
      red: '#C65D4D',       // Coral Red (unified)
      bronze: '#C87F4A',    // Warm Bronze (unified)
      terracotta: '#7D5645',// Terracotta
      sage: '#5F8A50',      // Sage Green
    },

    chart: {
      primary: '#C87F4A',
      secondary: '#9B6B56',
      tertiary: '#5F8A50',
      quaternary: '#B8923D',
      series: [
        '#C87F4A', '#9B6B56', '#5F8A50', '#B8923D',
        '#334155', '#C65D4D', '#8F7860', '#4A7A46'
      ]
    },

    special: {
      gold: 'linear-gradient(135deg, #D4A84B 0%, #C87F4A 100%)',
      silver: 'linear-gradient(135deg, #94A3B8 0%, #64748B 100%)',
      bronze: 'linear-gradient(135deg, #C87F4A 0%, #9B6B56 100%)',
      gradient: 'linear-gradient(135deg, #334155 0%, #C87F4A 100%)',
    }
  }
};

// 导出类型定义
export type Theme = typeof themes.dark;
export type ThemeMode = keyof typeof themes;

// 获取当前主题
export const getTheme = (mode: ThemeMode): Theme => {
  return themes[mode];
};

// CSS 变量生成器
export const generateCSSVariables = (theme: Theme): string => {
  const cssVars: string[] = [];
  
  const processObject = (obj: Record<string, unknown>, prefix: string = '') => {
    Object.entries(obj).forEach(([key, value]) => {
      const varName = prefix ? `${prefix}-${key}` : key;
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        processObject(value as Record<string, unknown>, varName);
      } else if (!Array.isArray(value)) {
        cssVars.push(`--${varName}: ${value};`);
      }
    });
  };
  
  processObject(theme);
  return cssVars.join('\n  ');
};

// 主题类名映射
export const themeClasses = {
  // 背景类
  bgBase: 'bg-[var(--bg-base)]',
  bgSurface: 'bg-[var(--bg-surface)]',
  bgElevated: 'bg-[var(--bg-elevated)]',
  bgOverlay: 'bg-[var(--bg-overlay)]',
  
  // 文字类
  textPrimary: 'text-[var(--text-primary)]',
  textSecondary: 'text-[var(--text-secondary)]',
  textTertiary: 'text-[var(--text-tertiary)]',
  
  // 边框类
  borderDefault: 'border-[var(--border-default)]',
  borderMuted: 'border-[var(--border-muted)]',
  borderStrong: 'border-[var(--border-strong)]',
};
