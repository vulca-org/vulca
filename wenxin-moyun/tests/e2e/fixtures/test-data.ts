export const TEST_USERS = {
  valid: {
    username: 'demo',
    password: 'demo123',
    displayName: 'Demo User'
  },
  admin: {
    username: 'admin',
    password: 'admin123',
    displayName: 'Admin User'
  },
  guest: {
    id: 'test-guest-001',
    dailyLimit: 3
  },
  invalid: {
    username: 'invalid_user',
    password: 'wrong_password'
  }
};

export const TEST_MODELS = {
  model1: {
    id: 'gpt-4',
    name: 'GPT-4',
    description: '最新的GPT-4模型，具有强大的创作能力'
  },
  model2: {
    id: 'claude-3',
    name: 'Claude 3',
    description: 'Anthropic的Claude 3模型'
  },
  model3: {
    id: 'wenxin-4',
    name: '文心一言 4.0',
    description: '百度文心大模型'
  }
};

export const TEST_EVALUATION_TASKS = {
  poetry: {
    type: 'poem',
    prompt: '春江花月夜',
    expectedDimensions: ['rhythm', 'composition', 'emotion', 'creativity', 'cultural']
  },
  painting: {
    type: 'painting',
    prompt: '山水画创作',
    expectedDimensions: ['composition', 'creativity', 'cultural', 'narrative']
  },
  story: {
    type: 'story',
    prompt: '编写一个关于AI的故事',
    expectedDimensions: ['narrative', 'emotion', 'creativity']
  }
};

export const TEST_TIMEOUTS = {
  short: 5000,
  medium: 10000,
  long: 30000,
  evaluation: 60000
};

export const TEST_URLS = {
  home: '/',
  login: '/login',
  canvas: '/canvas',
  gallery: '/gallery',
  models: '/models',
  research: '/research',
  skills: '/skills',
  admin: '/admin',
};
