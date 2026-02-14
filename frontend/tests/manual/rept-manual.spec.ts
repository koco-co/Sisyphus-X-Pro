import { test, expect } from '@playwright/test';

test.describe('REPT 模块手动验证', () => {
  test('验证 REPT 模块前端页面', async ({ page }) => {
    console.log('=== REPT 模块手动验证测试 ===\n');
    
    // Step 1: 导航到应用首页
    console.log('Step 1: 访问应用首页');
    await page.goto('http://localhost:3000/');
    await page.waitForLoadState('networkidle');
    console.log('✓ 首页加载成功');
    
    // Step 2: 检查是否需要登录
    const currentUrl = page.url();
    console.log(`当前 URL: ${currentUrl}`);
    
    if (currentUrl.includes('/login')) {
      console.log('需要登录，跳转到注册页面');
      
      // 创建测试用户
      const testUser = {
        email: `rept-test-${Date.now()}@example.com`,
        password: 'Test123456!',
        nickname: 'REPT Tester'
      };
      
      await page.click('button:has-text("注册")');
      await page.fill('input[type="email"]', testUser.email);
      await page.fill('input#password', testUser.password);
      await page.fill('input#nickname', testUser.nickname);
      await page.fill('input#confirmPassword', testUser.password);
      await page.click('button[type="submit"]');
      
      await page.waitForURL('**/', { timeout: 5000 });
      console.log('✓ 用户注册并登录成功');
    }
    
    // Step 3: 导航到测试报告页面
    console.log('\nStep 2: 导航到测试报告页面');
    await page.click('text=测试报告', { timeout: 5000 });
    await page.waitForURL('**/reports', { timeout: 5000 });
    console.log('✓ 成功导航到报告页面');
    
    // Step 4: 验证页面元素
    console.log('\nStep 3: 验证页面元素');
    
    const h1Text = await page.locator('h1').textContent();
    console.log(`页面标题: ${h1Text}`);
    
    const hasTable = await page.locator('table').count() > 0;
    console.log(hasTable ? '✓ 报告表格存在' : '✗ 报告表格不存在');
    
    const hasSearch = await page.locator('input[placeholder*="搜索"]').count() > 0;
    console.log(hasSearch ? '✓ 搜索框存在' : '✗ 搜索框不存在');
    
    const hasFilter = await page.locator('button:has-text("状态")').count() > 0;
    console.log(hasFilter ? '✓ 状态筛选器存在' : '✗ 状态筛选器不存在');
    
    // Step 5: 检查报告列表
    console.log('\nStep 4: 检查报告列表');
    const tableRows = await page.locator('table tbody tr').count();
    console.log(`报告数量: ${tableRows}`);
    
    if (tableRows > 0) {
      console.log('✓ 报告列表组件正常');
      
      // 检查表头
      const headers = await page.locator('table thead th').allTextContents();
      console.log('表头列:', headers);
      
      // 获取第一行数据
      const firstRow = page.locator('table tbody tr').first();
      await firstRow.hover();
      
      // 检查操作菜单
      const actionButtons = await firstRow.locator('button').count();
      console.log(`操作按钮数量: ${actionButtons}`);
    } else {
      console.log('⚠️  当前无测试报告（这是正常的）');
      console.log('建议: 执行测试计划后再次检查');
    }
    
    // 验证通过
    expect(hasTable).toBeTruthy();
    expect(h1Text).toContain('测试报告');
  });
});
