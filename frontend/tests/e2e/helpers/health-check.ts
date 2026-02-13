#!/usr/bin/env node

/**
 * E2E 测试健康检查脚本
 * 确保后端服务运行并可访问
 */

const http = require('http')

const BACKEND_URL = 'http://localhost:8000'
const HEALTH_ENDPOINT = '/health'
const TIMEOUT = 5000

function checkBackendHealth() {
  return new Promise((resolve, reject) => {
    const url = new URL(HEALTH_ENDPOINT, BACKEND_URL)

    const req = http.get(url, {
      timeout: TIMEOUT,
    }, (res) => {
      let data = ''

      res.on('data', (chunk) => {
        data += chunk
      })

      res.on('end', () => {
        if (res.statusCode === 200) {
          console.log('✅ Backend is healthy')
          resolve(true)
        } else {
          console.error(`❌ Backend returned status ${res.statusCode}`)
          reject(new Error(`Backend health check failed: ${res.statusCode}`))
        }
      })
    })

    req.on('error', (err) => {
      console.error('❌ Backend connection failed:', err.message)
      reject(err)
    })

    req.on('timeout', () => {
      req.destroy()
      console.error('❌ Backend connection timeout')
      reject(new Error('Backend connection timeout'))
    })
  })
}

async function main() {
  console.log('🔍 Checking E2E test prerequisites...')

  try {
    await checkBackendHealth()
    console.log('✅ All prerequisites met')
    process.exit(0)
  } catch (error) {
    console.error('\n❌ Prerequisites check failed')
    console.error('\nPlease ensure:')
    console.error('1. Backend is running on http://localhost:8000')
    console.error('2. Database is accessible')
    console.error('3. Run: cd backend && uvicorn app.main:app --reload')
    process.exit(1)
  }
}

main()
