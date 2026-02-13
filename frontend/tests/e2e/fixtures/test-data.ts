/**
 * E2E 测试数据 fixtures
 */

export const testUrls = {
  login: '/login',
  register: '/register',
  dashboard: '/',
  githubOAuth: /github\.com/,
  googleOAuth: /accounts\.google\.com|google\.com/,
}

export const testUsers = {
  valid: {
    email: `test-${Date.now()}@example.com`,
    password: 'Test123456!',
    name: 'Test User',
  },
  invalid: {
    email: 'nonexistent@example.com',
    password: 'WrongPassword123!',
  },
  weak: {
    password: '123', // 太弱
  },
  invalidEmail: {
    email: 'invalid-email', // 无效格式
  },
  lockout: {
    email: `lockout-test-${Date.now()}@example.com`,
    password: 'LockoutTest123!',
  },
}

export const testCredentials = {
  correct: {
    email: () => `test-${Date.now()}@example.com`,
    password: 'CorrectPass123!',
  },
  wrong: {
    email: () => `test-${Date.now()}@example.com`,
    password: 'WrongPass123!',
  },
}

export const errorMessages = {
  invalidCredentials: /密码|凭据|邮箱.*不存在/,
  emailExists: /已存在|已注册|邮箱/,
  weakPassword: /密码|强度|长度/,
  invalidEmail: /邮箱|格式/,
  accountLocked: /锁定|lock/,
}

export const successMessages = {
  loginSuccess: /成功|欢迎/,
  registerSuccess: /注册成功|创建账户/,
}

export const waitTimes = {
  short: 500,
  medium: 1000,
  long: 2000,
  extraLong: 5000,
}

export const localStorageKeys = {
  token: 'token',
  accessToken: 'access_token',
  refreshToken: 'refresh_token',
  user: 'user',
}

export const apiEndpoints = {
  login: '/api/auth/login',
  register: '/api/auth/register',
  logout: '/api/auth/logout',
  github: '/api/auth/github',
  google: '/api/auth/google',
}

export const browserConfig = {
  headless: true,
  slowMo: 0,
  timeout: 30000,
}

export const retryConfig = {
  retries: 0,
  workers: 1,
}
