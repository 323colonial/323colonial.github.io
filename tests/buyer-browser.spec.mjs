import { test, expect } from 'playwright/test';

for (const fixture of ['rendering-layout', 'gallery-viewer', 'resize-reading', 'seasonal-runtime']) {
  test(fixture, async ({ page, context, baseURL }, testInfo) => {
    // Buyer pages contain analytics tags; nothing may leave this isolated origin.
    await context.route('**/*', route => new URL(route.request().url()).origin === baseURL
      ? route.continue() : route.abort());
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(`/tests/${fixture}.html`);
    try {
      await expect(page).toHaveTitle(/^(PASS|FAIL):/, { timeout: 170_000 });
      const results = await page.locator('#results').innerText();
      console.log(results);
      expect(results).toContain('PASS');
      expect(results).not.toMatch(/FAIL|Running…/);
      await expect(page).toHaveTitle(/^PASS:/);
      expect(errors).toEqual([]);
    } finally {
      await testInfo.attach('fixture-results', {
        body: await page.locator('#results').innerText(), contentType: 'text/plain',
      });
    }
  });
}
