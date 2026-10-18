import { test, expect } from 'playwright/test';

for (const width of [1440, 390]) for (const route of ['/', '/?variant=singlehero']) {
  test(`${route} image hover preserves keyboard focus at ${width}px`, async ({ page, context, baseURL }) => {
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
    await page.goto(route);
    if (route === '/') await expect(page.locator('.visitor-panes > figure')).toHaveCount(3);
    else {
      await expect(page.locator('#seasonal-hero .season-stack')).toBeVisible();
      await checkImage(page.locator('#seasonal-hero'));
    }
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

for (const width of [1440, 390]) {
  test(`following narrative pane stays fixed before scroll handlers run at ${width}px`, async ({ page, context, baseURL }) => {
    await context.route('**/*', route => new URL(route.request().url()).origin === baseURL
      ? route.continue() : route.abort());
    await page.setViewportSize({ width, height: 1040 });
    await page.goto('/');
    await expect(page.locator('.visitor-panes > figure')).toHaveCount(3);
    await expect(page.locator('.story.is-scrolling')).toHaveCount(7);
    const drift = await page.evaluate(async () => {
      await document.fonts.ready;
      const settle = () => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      await settle();
      const stories = [...document.querySelectorAll('.story')];
      const step = Math.max(240, innerHeight * .5);
      const results = [];
      for (const [i, story] of stories.slice(0, -1).entries()) {
        const css = getComputedStyle(story);
        const stage = story.querySelector(innerWidth > 800 ? '.story-stage' : '.story-photos');
        // A native carrier preserves normal-flow coordinates while its child sticks.
        const slot = story.closest('.story-slot');
        const top = slot ? slot.offsetTop + slot.offsetHeight - story.offsetHeight : story.offsetTop;
        const offset = parseFloat(css.paddingTop)
          + parseFloat(css.getPropertyValue('--border-lines')) * parseFloat(css.lineHeight)
          + (innerWidth > 800 ? 0 : story.querySelector('.story-copy').offsetHeight + 28);
        const start = top + offset - parseFloat(getComputedStyle(stage).top);
        const count = story.querySelectorAll('.story-photos figure').length;
        for (const direction of [1, -1]) {
          scrollTo(0, start + (direction > 0 ? .3 : count - .3) * step);
          await settle();
          const next = stories[i + 1];
          const before = next.getBoundingClientRect().top;
          scrollBy(0, direction * 120);
          // Deliberately read in the same task: rAF correction cannot hide lag.
          results.push({section: i + 1, direction, drift: next.getBoundingClientRect().top - before});
          await settle();
        }
      }
      return results;
    });
    expect(drift.filter(result => Math.abs(result.drift) > 1)).toEqual([]);
    // Overlapping carriers must not paint over the preceding section's color.
    for (const slot of await page.locator('.story-slot').all()) {
      await expect(slot).toHaveCSS('background-color', 'rgba(0, 0, 0, 0)');
    }
  });
}

test('seasonal startup measurement waits for pending frames', async ({ page, context, baseURL }) => {
  let release;
  const pending = new Promise(resolve => { release = resolve; });
  await context.route('**/*', async route => {
    const url = new URL(route.request().url());
    if (url.origin !== baseURL) return route.abort();
    if (url.pathname.includes('/fixtures/seasons/') && url.pathname.endsWith('.webp')) await pending;
    await route.continue();
  });
  try {
    await page.goto('/tests/seasonal-runtime.html');
    const results = page.locator('#results');
    await expect(results).toContainText('PASS: dial follows shared phase');
    expect(await page.frames()[1].evaluate(() => seasonalClock.state().running)).toBe(false);
    await expect(results).not.toContainText('FAIL: hero starts');
    release();
    await expect(results).toContainText('PASS: hero starts with a few frames');
  } finally {
    release();
  }
});

for (const fixture of ['narrative-scroll', 'print-layout', 'rendering-layout', 'gallery-viewer', 'resize-reading', 'seasonal-runtime', 'buyer-audit', 'buyer-harden', 'buyer-typography', 'property-details', 'listing-fallbacks']) {
  test(fixture, async ({ page, context, baseURL }, testInfo) => {
    // Buyer pages contain analytics tags; nothing may leave this isolated origin.
    await context.route('**/*', route => new URL(route.request().url()).origin === baseURL
      ? route.continue() : route.abort());
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(`/tests/${fixture}.html`);
    if (fixture === 'print-layout') {
      await expect(page.locator('#results')).toContainText('Ready: switch to print media');
      await page.emulateMedia({ media: 'print' });
    }
    try {
      await expect(page).toHaveTitle(/^(PASS|FAIL):/, { timeout: 170_000 });
      const results = await page.locator('#results').innerText();
      console.log(results);
      expect(results).toContain('PASS');
      expect(results).not.toMatch(/FAIL|Running…/);
      await expect(page).toHaveTitle(/^PASS:/);
      // The details fixture disables ResizeObserver; listing and visitor initialization both fail.
      expect(errors).toEqual(fixture === 'property-details' ? Array(2).fill('ResizeObserver is not a constructor') : []);
    } finally {
      await testInfo.attach('fixture-results', {
        body: await page.locator('#results').innerText(), contentType: 'text/plain',
      });
    }
  });
}
