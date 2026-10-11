import { test, expect } from 'playwright/test';

const panes = '.visitor-panes > figure';
const ids = page => page.locator(panes).evaluateAll(nodes => nodes.map(n => Number(n.dataset.position)));
async function ready(page) {
  await page.goto('/?display=visitor');
  await expect(page.locator(panes)).toHaveCount(3);
}
async function tick(page) {
  const before = await ids(page);
  await page.clock.runFor(8100);
  await expect.poll(() => ids(page)).not.toEqual(before);
  return ids(page);
}

test.beforeEach(async ({page, context, baseURL}) => {
  await context.route('**/*', route => new URL(route.request().url()).origin === baseURL ? route.continue() : route.abort());
  await page.setViewportSize({width:1180,height:820});
  await page.clock.install();
});

test('visitor composition fits landscape/portrait, scrolls, resizes and opens current photos', async ({page}) => {
  await ready(page);
  expect(await ids(page)).toEqual([1,4,39]);
  for (const size of [{width:1180,height:820},{width:820,height:1180},{width:1024,height:768},{width:768,height:1024}]) {
    await page.setViewportSize(size);
    await page.clock.runFor(100);
    await expect.poll(() => page.evaluate(() => {
      const hero = document.querySelector('.hero-photo').getBoundingClientRect();
      const facts = document.querySelector('.listing-summary').getBoundingClientRect();
      return Math.abs(facts.bottom - innerHeight) < 2 && hero.top >= 0 && hero.height > 200 && document.documentElement.scrollWidth <= innerWidth;
    })).toBe(true);
    for (const figure of await page.locator(panes).all()) {
      const box = await figure.boundingBox();
      expect(box.height).toBeGreaterThan(100);
      expect(box.y + box.height).toBeLessThan(size.height);
      expect(await figure.locator('img').evaluate(img => getComputedStyle(img).objectFit)).toBe('contain');
    }
  }
  const next = await tick(page);
  expect(next[0]).not.toBe(1);
  await page.locator(`${panes} a`).first().click();
  await expect(page.locator('#photo-viewer')).toBeVisible();
  await expect(page.locator('#full-size')).toHaveAttribute('href', `assets/listing/${String(next[0]).padStart(2,'0')}.webp`);
  await page.keyboard.press('Escape');
  await expect(page.locator(`${panes} a`).first()).toBeFocused();
  const frozen = await ids(page);
  await page.clock.runFor(25000);
  expect(await ids(page)).toEqual(frozen);
  await page.locator('#hero-motion').click();
  await expect(page.locator('#hero-motion')).toHaveText('Pause photos');
  await page.evaluate(() => { document.activeElement.blur(); scrollTo(0, innerHeight * 2); });
  await page.clock.runFor(100);
  const offscreen = await ids(page);
  await page.clock.runFor(25000);
  expect(await ids(page)).toEqual(offscreen);
  expect(await page.evaluate(() => scrollY)).toBeGreaterThan(0);
  expect(await page.locator('.season-stack').count()).toBe(0);
});

test('rotation stays unique with coherent metadata; pause, dialogs, hidden tab, pagehide and print stop it', async ({page}) => {
  await ready(page);
  for (let i = 0; i < 15; i++) {
    const before = await ids(page), after = await tick(page);
    expect(new Set(after).size).toBe(3);
    expect(after.filter((n,j) => n !== before[j])).toHaveLength(1);
    for (const figure of await page.locator(panes).all()) {
      const id = await figure.getAttribute('data-position');
      await expect(figure.locator('a')).toHaveAttribute('href', `gallery.html#photo-${id}`);
      await expect(figure.locator('a')).toHaveAttribute('data-photo', id);
      expect(await figure.locator('img').getAttribute('alt')).toBe(await page.locator(`#photo-${id} img`).getAttribute('alt'));
    }
  }
  await page.getByRole('button', {name:'Pause photos',exact:true}).click();
  const paused = await ids(page);
  await page.clock.runFor(25000);
  expect(await ids(page)).toEqual(paused);
  await page.getByRole('button', {name:'Resume photos',exact:true}).click();
  await tick(page);
  for (const action of ['dialog', 'hidden', 'pagehide', 'print']) {
    if (action === 'dialog') await page.getByRole('link',{name:'Property details',exact:true}).click();
    if (action === 'hidden') await page.evaluate(() => { Object.defineProperty(document,'hidden',{configurable:true,value:true}); document.dispatchEvent(new Event('visibilitychange')); });
    if (action === 'pagehide') await page.evaluate(() => dispatchEvent(new Event('pagehide')));
    if (action === 'print') {
      await page.emulateMedia({media:'print'});
      await expect(page.locator('#hero-motion')).toHaveAttribute('hidden', '');
    }
    const before = await ids(page);
    await page.clock.runFor(25000);
    expect(await ids(page)).toEqual(before);
    if (action === 'dialog') await page.keyboard.press('Escape');
    if (action === 'hidden') await page.evaluate(() => { Object.defineProperty(document,'hidden',{configurable:true,value:false}); document.dispatchEvent(new Event('visibilitychange')); });
    if (action === 'pagehide') await page.evaluate(() => dispatchEvent(new Event('pageshow')));
    if (action === 'print') {
      await page.emulateMedia({media:'screen'});
      await expect(page.locator('#hero-motion')).not.toHaveAttribute('hidden', '');
    }
    await tick(page);
  }
});

test('failed or stalled loads retain composition; resume retries and pause cancels pending change', async ({page,context}) => {
  await ready(page);
  const before = await ids(page);
  await context.route('**/assets/listing/03.webp', route => route.abort());
  await page.clock.runFor(8100);
  await expect(page.getByRole('button',{name:'Resume photos',exact:true})).toBeVisible();
  expect(await ids(page)).toEqual(before);
  await context.unroute('**/assets/listing/03.webp');
  await page.getByRole('button',{name:'Resume photos',exact:true}).click();
  await tick(page);
  let release;
  await context.route('**/assets/listing/17.webp', async route => { await new Promise(resolve => { release = resolve; }); await route.continue().catch(() => {}); });
  await page.clock.runFor(8100);
  await expect.poll(() => Boolean(release)).toBe(true);
  const pending = await ids(page);
  await page.getByRole('button',{name:'Pause photos',exact:true}).click();
  release();
  await page.clock.runFor(15000);
  expect(await ids(page)).toEqual(pending);
});

test('initial loading preserves original hero focus until explicit resume', async ({page,context}) => {
  let release;
  await context.route('**/assets/listing/04.webp', async route => { await new Promise(resolve => { release = resolve; }); await route.continue().catch(() => {}); });
  await page.goto('/?display=visitor', {waitUntil:'domcontentloaded'});
  await expect.poll(() => Boolean(release)).toBe(true);
  await page.locator('#seasonal-hero').focus();
  release();
  await expect(page.getByRole('button',{name:'Resume photos',exact:true})).toBeVisible();
  await expect(page.locator('#seasonal-hero')).toBeFocused();
  await expect(page.locator('#seasonal-hero')).toBeVisible();
  await expect(page.locator(panes)).toHaveCount(0);
  await context.unroute('**/assets/listing/04.webp');
  await page.getByRole('button',{name:'Resume photos',exact:true}).click();
  await expect(page.locator(panes)).toHaveCount(3);
});

test('initial load failure and rotation timeout preserve valid originals', async ({page,context}) => {
  await context.route('**/assets/listing/04.webp', route => route.abort());
  await page.goto('/?display=visitor');
  await expect(page.getByRole('button',{name:'Resume photos',exact:true})).toBeVisible();
  await expect(page.locator('#seasonal-hero')).toBeVisible();
  await expect(page.locator(panes)).toHaveCount(0);
  await context.unroute('**/assets/listing/04.webp');
  await page.getByRole('button',{name:'Resume photos',exact:true}).click();
  await expect(page.locator(panes)).toHaveCount(3);
  let release;
  await context.route('**/assets/listing/03.webp', async route => { await new Promise(resolve => { release = resolve; }); await route.continue().catch(() => {}); });
  const before = await ids(page);
  await page.clock.runFor(8100);
  await expect.poll(() => Boolean(release)).toBe(true);
  await page.clock.runFor(10100);
  await expect(page.getByRole('button',{name:'Resume photos',exact:true})).toBeVisible();
  release();
  expect(await ids(page)).toEqual(before);
});

test('reduced motion and save-data are static; no-JS and normal mode retain original links', async ({page,context}) => {
  await page.emulateMedia({reducedMotion:'reduce'});
  await ready(page);
  const original = await ids(page);
  await page.clock.runFor(25000);
  expect(await ids(page)).toEqual(original);
  await expect(page.locator('#hero-motion')).toBeHidden();
  await page.emulateMedia({reducedMotion:'no-preference'});
  await expect(page.locator('#hero-motion')).toBeVisible();
  await tick(page);
  await page.goto('/');
  await expect(page.locator('.visitor-panes')).toHaveCount(0);
  await expect(page.locator('#seasonal-hero')).toHaveAttribute('data-photo','1');
  const nojs = await context.browser().newContext({javaScriptEnabled:false});
  const fallback = await nojs.newPage();
  await fallback.goto('http://127.0.0.1:18765/?display=visitor');
  await expect(fallback.locator('#seasonal-hero')).toHaveAttribute('href','gallery.html#photo-1');
  await expect(fallback.locator('.visitor-panes')).toHaveCount(0);
  await nojs.close();
  await page.addInitScript(() => Object.defineProperty(navigator, 'connection', {value:{saveData:true}}));
  await ready(page);
  await page.clock.runFor(25000);
  expect(await ids(page)).toEqual(original);
  await expect(page.locator('#hero-motion')).toBeHidden();
});
