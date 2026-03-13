/**
 * 本地测试数据配置
 * 用于Playwright E2E测试，不包含敏感信息
 */

export const testModels = [
  {
    id: 'test-gpt-4',
    name: 'GPT-4 (Test)',
    provider: 'OpenAI',
    type: 'llm',
    score: 85.5
  },
  {
    id: 'test-claude-3',
    name: 'Claude-3 (Test)',
    provider: 'Anthropic',
    type: 'llm',
    score: 83.2
  },
  {
    id: 'test-dall-e',
    name: 'DALL-E 3 (Test)',
    provider: 'OpenAI',
    type: 'image',
    score: null // Image models have null scores
  }
];

export const testUsers = [
  {
    username: 'testuser',
    email: 'test@example.com',
    // 不包含密码等敏感信息
  }
];

export const testEvaluations = [
  {
    id: 'eval-1',
    task: 'poem',
    prompt: '写一首关于春天的诗',
    modelId: 'test-gpt-4',
    status: 'completed'
  },
  {
    id: 'eval-2',
    task: 'story',
    prompt: '讲一个冒险故事',
    modelId: 'test-claude-3',
    status: 'processing'
  }
];

// 测试用的URL常量
export const testUrls = {
  homepage: '/',
  canvas: '/canvas',
  gallery: '/gallery',
  models: '/models',
  research: '/research',
  skills: '/skills',
  login: '/login',
};

// 测试用的CSS选择器
export const testSelectors = {
  navigation: {
    navbar: 'nav, [role="navigation"]',
    homeLink: 'a[href="/"], [href="#home"]',
    canvasLink: 'a[href*="canvas"]',
    galleryLink: 'a[href*="gallery"]',
    modelsLink: 'a[href*="models"]',
  },
  components: {
    iosButton: '[class*="ios-button"], button[class*="ios"]',
    iosCard: '[class*="ios-card"], [class*="card-ios"]',
    loadingSpinner: '[class*="loading"], [class*="spinner"]',
    errorMessage: '[class*="error"], [role="alert"]',
    successMessage: '[class*="success"], [class*="toast"]'
  },
  models: {
    modelList: '[class*="model-list"], table, [class*="leaderboard"]',
    modelCard: '[class*="model-card"], tr',
    scoreDisplay: '[class*="score"]',
    filterPanel: '[class*="filter"], [class*="tabs"]'
  },
};

// 测试用的等待时间配置
export const testTimeouts = {
  short: 1000,
  medium: 3000,
  long: 5000,
  veryLong: 10000
};

// 测试用的视口尺寸
export const testViewports = {
  mobile: { width: 375, height: 667 },
  mobileLarge: { width: 390, height: 844 },
  tablet: { width: 768, height: 1024 },
  desktop: { width: 1920, height: 1080 },
  desktopLarge: { width: 2560, height: 1440 }
};

// 性能测试阈值
export const performanceThresholds = {
  pageLoadTime: 3000, // 页面加载时间不超过3秒
  firstContentfulPaint: 1500, // 首次内容绘制不超过1.5秒
  interactionDelay: 100 // 交互延迟不超过100ms
};

// API测试端点（仅用于前端测试，不包含实际API密钥）
export const apiEndpoints = {
  models: '/api/v1/models',
  evaluations: '/api/v1/evaluations',
  prototypeRuns: '/api/v1/prototype/runs',
  gallery: '/api/v1/prototype/gallery',
};

// 测试用的表单数据
export const testFormData = {
  evaluation: {
    task: 'poem',
    prompt: '测试提示词',
    language: 'zh',
    model: 'test-model'
  },
};

// 可访问性测试配置
export const a11yConfig = {
  // 需要检查的可访问性标准
  standards: ['WCAG2A', 'WCAG2AA'],
  // 忽略的规则（如果有特殊情况）
  ignoreRules: []
};

// 浏览器兼容性测试配置
export const browserConfig = {
  // 需要测试的浏览器
  browsers: ['chromium', 'firefox', 'webkit'],
  // 移动端浏览器
  mobile: ['chrome-mobile', 'safari-mobile']
};
