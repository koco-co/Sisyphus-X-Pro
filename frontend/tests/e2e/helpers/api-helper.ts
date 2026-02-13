import { request, APIRequestContext } from '@playwright/test'

const API_BASE_URL = 'http://localhost:8000/api/v1'

export class ApiHelper {
  static async createTestUser(email: string, password: string) {
    const context = await request.newContext()
    await context.post(`${API_BASE_URL}/auth/register`, {
      data: { email, password, nickname: email.split('@')[0] },
    })
    await context.dispose()
  }

  static async deleteTestUser(email: string, token: string) {
    const context = await request.newContext({
      extraHTTPHeaders: {
        Authorization: `Bearer ${token}`,
      },
    })
    await context.delete(`${API_BASE_URL}/users/profile`)
    await context.dispose()
  }

  static async getUserToken(email: string, password: string): Promise<string> {
    const context = await request.newContext()
    const response = await context.post(`${API_BASE_URL}/auth/login`, {
      data: { email, password },
    })
    const data = await response.json()
    await context.dispose()
    return data.access_token || data.token
  }

  static async resetFailedAttempts(email: string) {
    // This would require admin endpoint - for now we'll create new users per test
  }
}
