import { test, expect } from '@playwright/test';

test('loads platform dashboard shell', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await expect(page.getByRole('heading', { name: 'Health Intelligence Platform' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Platform Capabilities' })).toBeVisible();
});
