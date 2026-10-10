import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { chromium } from 'playwright';

const fixture = new URL('./armillary-variants.html', import.meta.url);
assert.ok(existsSync(fixture), 'Compact armillary comparison exists');
const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(fixture.href);
  assert.deepEqual(await page.locator('h2').allTextContents(), ['Floating meridians', 'Gimbal', 'Eclipse']);
  assert.equal(await page.locator('.instrument').count(), 6);
  assert.equal(await page.getByRole('button', { name: 'Play motion', exact: true }).count(), 1);
  const slider = page.getByLabel('Seasonal progression');
  for (const phase of [0, 25, 50, 75, 100]) {
    await slider.fill(String(phase));
    assert.equal(await page.locator('output').textContent(), ['Spring', 'Summer', 'Autumn', 'Winter', 'Spring'][phase / 25]);
    assert.ok((await slider.getAttribute('aria-valuetext')).includes('percent through cycle'));
    assert.equal(await page.locator('svg').evaluateAll(nodes => nodes.some(node => /NaN|undefined/.test(node.innerHTML))), false);
  }
  for (let phase = 0; phase <= 100; phase += 2) {
    await slider.fill(String(phase));
    const bounds = await page.locator('.instrument > g').evaluateAll(nodes => nodes.map(node => {
      const { x, y, width, height } = node.getBBox();
      return { x, y, width, height };
    }));
    for (const box of bounds) {
      assert.ok(box.x >= 2 && box.y >= 2 && box.x + box.width <= 198 && box.y + box.height <= 198, 'Drawing fits frame with stroke clearance');
      assert.ok(Math.max(box.width, box.height) >= 176, 'Drawing fills at least 88% of frame');
    }
  }
  await slider.fill('8');
  const before = await page.locator('.enlarged .instrument').evaluateAll(nodes => nodes.map(n => n.innerHTML));
  await page.getByRole('button', { name: 'Play motion', exact: true }).click();
  const moved = await page.evaluate(() => {
    for (let i = 0; i < 120; i++) {
      cancelAnimationFrame(frame);
      tick(lastTime + 16);
    }
    cancelAnimationFrame(frame);
    return Number(document.querySelector('input').value);
  });
  assert.ok(moved > 13 && moved < 15, 'Fractional motion accumulates at 60fps');
  const after = await page.locator('.enlarged .instrument').evaluateAll(nodes => nodes.map(n => n.innerHTML));
  before.forEach((markup, i) => assert.notEqual(markup, after[i], 'Each variant visibly changes with phase'));
  await page.getByRole('button', { name: 'Pause motion', exact: true }).click();
  assert.equal(await page.evaluate(() => playing), false);
  await page.getByRole('button', { name: 'Play motion', exact: true }).click();
  await slider.fill('99.9');
  assert.equal(await page.evaluate(() => playing), false, 'Scrubbing stops playback');
  await slider.focus();
  await page.keyboard.press('ArrowLeft');
  assert.equal(await slider.inputValue(), '99.8');
  await page.keyboard.press('Tab');
  assert.equal(await page.getByRole('button', { name: 'Play motion', exact: true }).evaluate(n => n === document.activeElement), true);
  await page.keyboard.press('Enter');
  await page.evaluate(() => {
    cancelAnimationFrame(frame);
    tick(lastTime + 360);
    stop();
  });
  assert.equal(await page.locator('output').textContent(), 'Spring', 'Playback wraps year');
  await page.getByRole('button', { name: 'Play motion', exact: true }).click();
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await page.waitForFunction(() => !playing);
  for (const width of [1440, 1024]) {
    await page.setViewportSize({ width, height: 1000 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, `No desktop overflow at ${width}px`);
    for (const sample of await page.locator('.actual .instrument').all()) {
      const box = await sample.boundingBox();
      assert.equal(box.width, 52);
      assert.equal(box.height, 52);
    }
  }
  assert.deepEqual(errors, []);
  console.log('PASS: three compact variants, six diagrams, full-cycle bounds, all seasons, fractional motion, pause/scrub/wrap, keyboard, reduced-motion change, 52px samples, 1440/1024px layouts; no runtime errors.');
} finally {
  await browser.close();
}
