import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { chromium } from 'playwright';

const fixture = new URL('./seasonal-instruments.html', import.meta.url);
assert.ok(existsSync(fixture), 'Three-instrument comparison exists');
const browser = await chromium.launch();
try {
  const page = await browser.newPage({ reducedMotion: 'reduce' });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(fixture.href);
  assert.equal(await page.locator('.instrument').count(), 6);
  assert.equal(await page.getByRole('button', { name: 'Play motion' }).count(), 1);
  for (const phase of [0, 25, 50, 75, 100]) {
    await page.getByLabel('Seasonal progression').fill(String(phase));
    assert.equal(await page.locator('output').textContent(), ['Spring', 'Summer', 'Autumn', 'Winter', 'Spring'][phase / 25]);
    assert.equal(await page.locator('svg').evaluateAll(nodes => nodes.some(node => /NaN|undefined/.test(node.innerHTML))), false);
  }
  await page.getByLabel('Seasonal progression').fill('8');
  await page.getByRole('button', { name: 'Play motion' }).click();
  assert.equal(await page.getByRole('button', { name: 'Pause motion' }).count(), 1);
  const moved = await page.evaluate(() => {
    for (let i = 0; i < 120; i++) {
      cancelAnimationFrame(frame);
      tick(lastTime + 16);
    }
    cancelAnimationFrame(frame);
    return Number(document.querySelector('input').value);
  });
  assert.ok(moved > 13 && moved < 15, 'Motion accumulates fractional steps at 60fps');
  await page.getByRole('button', { name: 'Pause motion' }).click();
  for (const width of [1440, 390, 320]) {
    await page.setViewportSize({ width, height: 1000 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, `No overflow at ${width}px`);
    for (const sample of await page.locator('.actual .instrument').all()) {
      assert.equal((await sample.boundingBox()).width, 52);
    }
  }
  assert.deepEqual(errors, []);
  console.log('PASS: six diagrams, all seasonal positions, play/pause, reduced-motion default, 52px samples, 1440/390/320px layouts; no runtime errors.');
} finally {
  await browser.close();
}
