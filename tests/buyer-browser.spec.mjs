import { test, expect } from 'playwright/test';

for (const width of [1440, 390]) {
  test(`image hover preserves keyboard focus at ${width}px`, async ({ page, context, baseURL }) => {
    await context.route('**/*', route => new URL(route.request().url()).origin === baseURL
      ? route.continue() : route.abort());
    await page.setViewportSize({ width, height: 1040 });
    async function checkImage(link) {
      await link.hover();
      expect(await link.evaluate(element => getComputedStyle(element, '::after').content)).toBe('none');
      await page.keyboard.press('Tab');
      await link.focus();
      await expect(link).toBeFocused();
      expect(await link.evaluate(element => {
        const css = getComputedStyle(element);
        return [element.matches(':focus-visible'), css.outlineStyle, css.outlineWidth, css.outlineOffset];
      })).toEqual([true, 'solid', '3px', '4px']);
    }
    await page.goto('/');
    await expect(page.locator('.hero-photo .season-stack')).toBeVisible();
    await checkImage(page.locator('#seasonal-hero'));
    await checkImage(page.locator('.story .media-record > a').first());
    await page.locator('[data-all-photos]').click();
    await checkImage(page.locator('#all-photos [data-gallery-image]').first());
    await page.keyboard.press('Enter');
    await expect(page.locator('#photo-viewer')).toBeVisible();
    await page.locator('#viewer-image').hover();
    await expect(page.locator('#viewer-image')).toHaveCSS('border-top-width', '0px');
    await page.keyboard.press('Escape');
    await expect(page.locator('#all-photos [data-gallery-image]').first()).toBeFocused();
    await page.goto('/gallery.html');
    await checkImage(page.locator('[data-gallery-image]').first());
    await page.keyboard.press('Enter');
    await expect(page.locator('#photo-viewer')).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(page.locator('[data-gallery-image]').first()).toBeFocused();
  });
}

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
