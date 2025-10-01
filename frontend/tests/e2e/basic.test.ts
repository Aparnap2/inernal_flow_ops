import { test, expect } from '@playwright/test';

test('homepage has title and links', async ({ page }) => {
  await page.goto('/');

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/Vite React Template/);

  // Create a locator for the main content
  const mainContent = page.locator('main');
  
  // Expect main content to be visible
  await expect(mainContent).toBeVisible();
  
  // Check for navigation links
  await expect(page.getByRole('link', { name: 'Dashboard' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'AGUI' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Runs' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Approvals' })).toBeVisible();
});

test('dashboard page loads correctly', async ({ page }) => {
  await page.goto('/dashboard');

  // Check if dashboard content is present
  await expect(page.locator('h1, h2')).toContainText(/Dashboard|Overview/);
});

test('AGUI page loads correctly', async ({ page }) => {
  await page.goto('/agui');

  // Check if AGUI content is present
  await expect(page.locator('h1, h2')).toContainText(/AGUI|Agentic UI/);
});