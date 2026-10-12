import { test, expect } from 'playwright/test';

// Focused browser/AX regressions, not a screen-reader or WCAG certification.
test.beforeEach(async ({ context, baseURL }) => {
  await context.route('**/*', route => new URL(route.request().url()).origin === baseURL
    ? route.continue() : route.abort());
});

for (const route of ['/', '/gallery.html']) {
  test(`${route} keyboard order, names, focus and modal isolation`, async ({ page, context }) => {
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.goto(route);
    for (const name of ['Skip to content', '323 Colonial Dr', 'Call Dandridge office at (304) 885-1547', 'Questions & tours through Dandridge Realty Group']) {
      await page.keyboard.press('Tab');
      const link = page.getByRole('link', { name, exact: true });
      await expect(link).toBeFocused();
      expect(await link.evaluate(el => {
        const s = getComputedStyle(el), r = el.getBoundingClientRect();
        return el.matches(':focus-visible') && s.outlineStyle === 'solid' && parseFloat(s.outlineWidth) >= 3
          && r.top >= 0 && r.bottom <= innerHeight;
      })).toBe(true);
    }
    await page.getByRole('link', { name: 'Skip to content', exact: true }).focus();
    await page.keyboard.press('Enter');
    await page.keyboard.press('Tab');
    expect(await page.evaluate(() => !!document.activeElement.closest('main'))).toBe(true);
    const ax = await context.newCDPSession(page);
    const tree = await ax.send('Accessibility.getFullAXTree');
    for (const role of ['banner', 'main', 'contentinfo']) {
      expect(tree.nodes.filter(n => !n.ignored && n.role?.value === role)).toHaveLength(1);
    }
    expect(await page.locator('html').getAttribute('lang')).toBe('en');
    await expect(page.getByRole('heading', { level: 1 })).toHaveCount(1);
    expect(await page.locator('img:not([alt])').count()).toBe(0);

    if (route === '/') {
      const details = page.getByRole('link', { name: 'Property details', exact: true });
      await details.focus();
      await page.keyboard.press('Enter');
      const dialog = page.getByRole('dialog', { name: 'Property details', exact: true });
      await expect(dialog).toBeVisible();
      await expect(dialog.getByRole('button', { name: 'Close details' })).toBeFocused();
      for (const key of ['Tab', 'Shift+Tab']) {
        await page.keyboard.press(key);
        // Native dialog may send focus to browser chrome, but never to background controls.
        expect(await page.evaluate(() => document.activeElement === document.body || !!document.activeElement.closest('dialog[open]'))).toBe(true);
      }
      await page.evaluate(() => { window.closedDialog = new Promise(resolve => document.querySelector('#property-details').addEventListener('close', resolve, { once: true })); });
      await page.keyboard.press('Escape');
      await page.evaluate(() => window.closedDialog.then(() => true));
      await expect(details).toBeFocused();
      await page.keyboard.press('Enter');
      await page.evaluate(() => { window.closedDialog = new Promise(resolve => document.querySelector('#property-details').addEventListener('close', resolve, { once: true })); });
      await page.getByRole('button', { name: 'Close details' }).press('Enter');
      await page.evaluate(() => window.closedDialog.then(() => true));
      await expect(details).toBeFocused();
      await page.getByRole('link', { name: 'View all 65 photos' }).focus();
      await page.keyboard.press('Enter');
      await expect(page.getByRole('button', { name: 'Close photos' })).toBeFocused();
      await page.keyboard.press('Tab');
    } else {
      await page.locator('[data-gallery-image]').first().focus();
    }
    const opener = page.locator('[data-gallery-image]').first();
    await expect(opener).toBeFocused();
    await page.keyboard.press('Enter');
    const viewer = page.getByRole('dialog', { name: 'Photo 1 of 65', exact: true });
    await expect(viewer).toBeVisible();
    await expect(viewer.getByRole('button', { name: 'Close', exact: true })).toBeFocused();
    const modalTree = await ax.send('Accessibility.getFullAXTree');
    expect(modalTree.nodes.some(n => !n.ignored && n.role?.value === 'link' && n.name?.value.startsWith('Call Dandridge'))).toBe(false);
    for (const name of ['Previous', 'Open full-size image', 'Next']) {
      await page.keyboard.press('Tab');
      await expect(page.getByRole(name === 'Open full-size image' ? 'link' : 'button', { name, exact: true })).toBeFocused();
    }
    await page.keyboard.press('Shift+Tab');
    await expect(page.getByRole('link', { name: 'Open full-size image' })).toBeFocused();
    await page.keyboard.press('ArrowRight');
    await expect(page.getByRole('dialog', { name: 'Photo 2 of 65', exact: true })).toBeVisible();
    await expect(page.locator('#viewer-title')).toHaveAttribute('aria-live', 'polite');
    const updatedTree = await ax.send('Accessibility.getFullAXTree');
    expect(updatedTree.nodes.some(n => !n.ignored && n.name?.value === 'Photo 2 of 65'
      && n.properties?.some(p => p.name === 'live' && p.value.value === 'polite'))).toBe(true);
    await expect(page.locator('#viewer-image')).toHaveAttribute('alt', /Soaring great room/);
    await page.keyboard.press('Escape');
    await expect(opener).toBeFocused();
    if (route === '/') {
      await expect(page.getByRole('dialog', { name: 'All 65 photos', exact: true })).toBeVisible();
      await page.keyboard.press('Escape');
      await expect(page.getByRole('link', { name: 'View all 65 photos' })).toBeFocused();
    }
  });
}

for (const [width, height, touch, enlarge] of [[1440, 1000, false, false], [390, 844, true, false], [320, 740, true, false], [320, 256, true, false], [844, 390, true, false], [320, 740, true, true]]) {
  test(`compact target geometry ${width}x${height} touch=${touch} text200=${enlarge}`, async ({ browser, baseURL }, testInfo) => {
    const context = await browser.newContext({ viewport: { width, height }, hasTouch: touch, baseURL });
    await context.route('**/*', route => new URL(route.request().url()).origin === baseURL ? route.continue() : route.abort());
    const page = await context.newPage();
    try {
      await page.goto('/');
      await expect(page.locator('#hero-motion')).toBeVisible();
      expect(await page.evaluate(() => matchMedia('(pointer: coarse)').matches)).toBe(touch);
      if (enlarge) await page.evaluate(() => {
        const nodes = [...document.querySelectorAll('body *')];
        const sizes = nodes.map(el => getComputedStyle(el).fontSize);
        nodes.forEach((el, i) => { el.style.fontSize = `${parseFloat(sizes[i]) * 2}px`; });
      });
      await expect.poll(() => page.evaluate(() => {
        const root = document.documentElement;
        return ['.masthead', '.listing-summary'].every((selector, i) =>
          Math.abs(document.querySelector(selector).getBoundingClientRect().height - parseFloat(root.style.getPropertyValue(i ? '--summary-height' : '--header-height'))) < 1);
      })).toBe(true);
      const targets = page.locator('.contact-actions a, .price a, [data-all-photos]');
      const measurements = [];
      for (const target of await targets.all()) {
        await target.focus();
        await expect(target).toBeInViewport();
        await expect.poll(() => target.evaluate(el => { const r = el.getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight; })).toBe(true);
        const result = await target.evaluate(el => {
          const r = el.getBoundingClientRect();
          const points = [[r.left + 1, r.top + 1], [r.right - 1, r.bottom - 1], [r.left + r.width / 2, r.top + r.height / 2]];
          return { name: el.textContent, width: r.width, height: r.height,
            hits: points.map(([x, y]) => ({ x, y, own: el.contains(document.elementFromPoint(x, y)), hit: document.elementFromPoint(x, y)?.outerHTML.slice(0, 120) })),
            pseudo: getComputedStyle(el, '::after').content };
        });
        expect(result.width).toBeGreaterThanOrEqual(24);
        expect(result.height).toBeGreaterThanOrEqual(touch && width <= 800 && height > 500 && ['Property details', 'View all 65 photos'].includes(result.name) ? 44 : 24);
        expect(result.hits.every(point => point.own), JSON.stringify(result)).toBe(true);
        expect(result.pseudo).toBe('none');
        measurements.push(result);
      }
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
      if (enlarge) {
        await expect(page.locator('.masthead')).toHaveCSS('position', 'static');
        await expect(page.locator('.listing-summary')).toHaveCSS('position', 'static');
        await expect(page.locator('html')).toHaveCSS('scroll-padding-top', '24px');
      }
      if (touch) {
        await page.locator('.price a').tap();
        await expect(page.getByRole('dialog', { name: 'Property details', exact: true })).toBeVisible();
        await page.getByRole('button', { name: 'Close details' }).tap();
        await expect(page.locator('.price a')).toBeFocused();
      }
      // Measure centered 44px invisible expansion against actual adjacent text, without shipping it.
      const proposal = await page.evaluate(() => {
        const anchors = [...document.querySelectorAll('.contact-actions a, .price a, [data-all-photos]')];
        const texts = [...document.querySelectorAll('.header-contact p, .listing-status, .price > span:first-child')];
        return anchors.map(a => {
          const r = a.getBoundingClientRect(), top = r.top - Math.max(0, 44 - r.height) / 2, bottom = Math.max(r.bottom, top + 44);
          return { name: a.textContent, textCollisions: texts.filter(el => {
            const range = document.createRange(); range.selectNodeContents(el);
            return [...range.getClientRects()].some(t => t.left < r.right && t.right > r.left && t.top < bottom && t.bottom > top);
          }).map(el => el.textContent) };
        });
      });
      const baseline = await page.locator('.masthead, .listing-summary').evaluateAll(els => els.map(el => el.getBoundingClientRect().height));
      await page.addStyleTag({ content: '.contact-actions a, .price a, .summary-actions .text-link { min-height: 44px; }' });
      const padded = await page.locator('.masthead, .listing-summary').evaluateAll(els => els.map(el => el.getBoundingClientRect().height));
      await testInfo.attach('target-comparison', { body: JSON.stringify({ measurements, proposal, baseline, padded }, null, 2), contentType: 'application/json' });
      if (enlarge) {
        await page.setViewportSize({ width: 1440, height: 1000 });
        await expect(page.locator('.masthead')).toHaveCSS('position', 'sticky');
        await expect(page.locator('.listing-summary')).toHaveCSS('position', 'sticky');
      }
    } finally { await context.close(); }
  });
}

test('rendered text colors retain AA contrast on actual solid fields', async ({ page }, testInfo) => {
  await page.goto('/');
  const pairs = await page.evaluate(() => {
    const luminance = color => {
      const rgb = color.match(/[\d.]+/g).slice(0, 3).map(Number).map(c => c / 255)
        .map(c => c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4);
      return rgb[0] * .2126 + rgb[1] * .7152 + rgb[2] * .0722;
    };
    return [...document.querySelectorAll('.contact-actions a, .price a, .listing-status, .story-copy .listing-copy, .site-footer, .analytics-notice')].map(el => {
      let field = el;
      while (getComputedStyle(field).backgroundColor === 'rgba(0, 0, 0, 0)') field = field.parentElement;
      const fg = luminance(getComputedStyle(el).color), bg = luminance(getComputedStyle(field).backgroundColor);
      return { text: el.textContent.slice(0, 40), ratio: (Math.max(fg, bg) + .05) / (Math.min(fg, bg) + .05) };
    });
  });
  for (const pair of pairs) expect(pair.ratio, pair.text).toBeGreaterThanOrEqual(4.5);
  await testInfo.attach('contrast', { body: JSON.stringify(pairs, null, 2), contentType: 'application/json' });
});
