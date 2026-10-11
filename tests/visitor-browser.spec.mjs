import { test, expect } from 'playwright/test';

const panes = '.visitor-panes > figure';
const ids = page => page.locator(panes).evaluateAll(nodes => nodes.map(n => Number(n.dataset.position)));
async function ready(page) {
  await page.goto('/?display=visitor');
  await expect(page.locator(panes)).toHaveCount(3);
}
async function tick(page) {
  const before = await ids(page);
  // Virtual time must not consume the seasonal hold budget while real images decode.
  await expect.poll(() => page.evaluate(current => {
    const state = window.seasonalClock?.state();
    return !state || (state.running && !state.holding && !state.stalled
      && current.every(id => state.joined.includes(id)));
  }, before)).toBe(true);
  await page.clock.runFor(8100);
  await expect.poll(() => ids(page)).not.toEqual(before);
  return ids(page);
}

test.beforeEach(async ({page, context, baseURL}) => {
  await context.route('**/*', route => new URL(route.request().url()).origin === baseURL ? route.continue() : route.abort());
  await page.setViewportSize({width:1180,height:820});
  await page.clock.install();
});

test('visitor composition fits flush landscape/portrait with noninteractive photos', async ({page}) => {
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
    const edges = await page.locator(panes).evaluateAll(nodes => nodes.map(n => {
      const r = n.getBoundingClientRect(); return {left:r.left,right:r.right,top:r.top,bottom:r.bottom};
    }));
    const [a,b,c] = edges;
    if (size.width > size.height) {
      expect(a.top).toBeCloseTo(b.top); expect(a.bottom).toBeCloseTo(c.bottom);
      expect(a.right).toBeCloseTo(b.left); expect(b.bottom).toBeCloseTo(c.top);
    } else {
      expect(a.left).toBeCloseTo(b.left); expect(a.right).toBeCloseTo(c.right);
      expect(a.bottom).toBeCloseTo(b.top); expect(b.right).toBeCloseTo(c.left);
    }
    for (const figure of await page.locator(panes).all()) {
      const box = await figure.boundingBox();
      expect(box.height).toBeGreaterThan(100);
      expect(box.y + box.height).toBeLessThan(size.height);
      expect(await figure.locator('.visitor-image > img').evaluate(img => getComputedStyle(img).objectFit)).toBe('cover');
    }
  }
  await expect(page.locator('#hero-motion svg.season-dial')).toBeVisible();
  await expect(page.locator(`${panes} a`)).toHaveCount(0);
  const next = await tick(page);
  expect(next[0]).not.toBe(1);
  await page.locator(panes).first().click();
  await expect(page.locator('#photo-viewer')).not.toBeVisible();
  await page.getByRole('link', {name:'View all 65 photos', exact:true}).click();
  await expect(page.locator('#all-photos')).toBeVisible();
  await page.keyboard.press('Escape');
  await page.evaluate(() => { document.activeElement.blur(); scrollTo(0, innerHeight * 2); });
  await page.clock.runFor(100);
  const offscreen = await ids(page);
  await page.clock.runFor(25000);
  expect(await ids(page)).toEqual(offscreen);
  expect(await page.evaluate(() => scrollY)).toBeGreaterThan(0);
  expect(await page.locator('.visitor-panes .season-stack').count()).toBe(0);
});

test('rotation stays unique with coherent metadata; pause, dialogs, hidden tab, pagehide and print stop it', async ({page}) => {
  await ready(page);
  for (let i = 0; i < 15; i++) {
    const before = await ids(page), after = await tick(page);
    expect(new Set(after).size).toBe(3);
    expect(after.filter((n,j) => n !== before[j])).toHaveLength(1);
    for (const figure of await page.locator(panes).all()) {
      const id = await figure.getAttribute('data-position');
      await expect(figure.locator('a')).toHaveCount(0);
      expect(await figure.locator('.visitor-image > img').getAttribute('alt')).toBe(await page.locator(`#photo-${id} img`).getAttribute('alt'));
    }
  }
  await page.getByRole('button', {name:'Pause animation',exact:true}).click();
  const paused = await ids(page);
  await page.clock.runFor(25000);
  expect(await ids(page)).toEqual(paused);
  await page.getByRole('button', {name:'Resume animation',exact:true}).click();
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
    const phase = await page.evaluate(() => seasonalClock.state().phase);
    await page.clock.runFor(25000);
    expect(await ids(page)).toEqual(before);
    expect(await page.evaluate(() => seasonalClock.state().phase)).toBe(phase);
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

test('rotation ticks allow delayed seasonal frames to settle between clock advances', async ({page,context}) => {
  await context.route('**/assets/seasons-next/03/*.webp', async route => {
    await new Promise(resolve => setTimeout(resolve, 250));
    await route.continue();
  });
  await ready(page);
  expect(await tick(page)).toEqual([3,4,39]);
  expect(await tick(page)).toEqual([3,17,39]);
  expect(await page.evaluate(() => seasonalClock.state().stalled)).toBe(false);
});

test('failed or stalled loads retain composition; resume retries and pause cancels pending change', async ({page,context}) => {
  await ready(page);
  const before = await ids(page);
  await context.route('**/assets/listing/03.webp', route => route.abort());
  await page.clock.runFor(8100);
  await expect(page.getByRole('button',{name:'Resume animation',exact:true})).toBeVisible();
  expect(await ids(page)).toEqual(before);
  await context.unroute('**/assets/listing/03.webp');
  await page.getByRole('button',{name:'Resume animation',exact:true}).click();
  await tick(page);
  let release;
  await context.route('**/assets/listing/17.webp', async route => { await new Promise(resolve => { release = resolve; }); await route.continue().catch(() => {}); });
  await page.clock.runFor(8100);
  await expect.poll(() => Boolean(release)).toBe(true);
  const pending = await ids(page);
  await page.getByRole('button',{name:'Pause animation',exact:true}).click();
  release();
  await page.clock.runFor(15000);
  expect(await ids(page)).toEqual(pending);
});

test('initial loading keeps hero inert and preserves control focus', async ({page,context}) => {
  let release;
  await context.route('**/assets/listing/04.webp', async route => { await new Promise(resolve => { release = resolve; }); await route.continue().catch(() => {}); });
  await page.goto('/?display=visitor', {waitUntil:'domcontentloaded'});
  await expect.poll(() => Boolean(release)).toBe(true);
  await expect(page.locator('#seasonal-hero')).toHaveAttribute('inert', '');
  await page.locator('#hero-motion').focus();
  release();
  await expect(page.locator(panes)).toHaveCount(3);
  await expect(page.locator('#hero-motion')).toBeFocused();
});

test('initial load failure and rotation timeout preserve valid originals', async ({page,context}) => {
  await context.route('**/assets/listing/04.webp', route => route.abort());
  await page.goto('/?display=visitor');
  await expect(page.getByRole('button',{name:'Resume animation',exact:true})).toBeVisible();
  await expect(page.locator('#seasonal-hero')).toBeVisible();
  await expect(page.locator(panes)).toHaveCount(0);
  await context.unroute('**/assets/listing/04.webp');
  await page.getByRole('button',{name:'Resume animation',exact:true}).click();
  await expect(page.locator(panes)).toHaveCount(3);
  let release;
  await context.route('**/assets/listing/03.webp', async route => { await new Promise(resolve => { release = resolve; }); await route.continue().catch(() => {}); });
  const before = await ids(page);
  await page.clock.runFor(8100);
  await expect.poll(() => Boolean(release)).toBe(true);
  await page.clock.runFor(10100);
  await expect(page.getByRole('button',{name:'Resume animation',exact:true})).toBeVisible();
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
  await page.getByRole('button', {name:'Resume animation', exact:true}).click();
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

test('visitor panes and compass share seasonal phase and one pause control', async ({page}) => {
  await ready(page);
  await expect.poll(() => page.locator('.visitor-panes .season-stack').count()).toBe(3);
  await expect(page.locator('#hero-motion svg.season-dial')).toBeVisible();
  await page.getByRole('button', {name:'Pause animation', exact:true}).click();
  const frozen = await page.evaluate(() => seasonalClock.state().phase);
  const before = await ids(page);
  await page.clock.runFor(25000);
  expect(await page.evaluate(() => seasonalClock.state().phase)).toBe(frozen);
  expect(await ids(page)).toEqual(before);
  await page.getByRole('button', {name:'Resume animation', exact:true}).click();
  await tick(page);
  await expect.poll(() => page.locator('.visitor-panes .season-stack').count()).toBe(3);
  const state = await page.evaluate(() => {
    const stacks = [...document.querySelectorAll('.visitor-panes .season-stack')];
    const hand = document.querySelector('.season-hand');
    return {phase: seasonalClock.state().phase, running: seasonalClock.state().running,
      starts: [...stacks.map(s => s.lastElementChild.getAnimations()[0]?.startTime), hand.getAnimations()[0]?.startTime],
      frames: stacks.map(s => [...s.querySelectorAll('img')].map(i => i.src))};
  });
  expect(state.running).toBe(true);
  expect(new Set(state.starts).size).toBe(1);
  expect(state.starts[0]).toEqual(expect.any(Number));
  const current = await ids(page);
  expect(await page.evaluate(() => seasonalClock.state().joined)).toEqual(current);
  state.frames.forEach((urls, i) => urls.forEach(url => expect(url).toMatch(new RegExp(`/(seasons-next/${String(current[i]).padStart(2,'0')}/|listing/${String(current[i]).padStart(2,'0')})`))));
});

test('seasonal failure pauses both motions and Resume recovers; missing manifest keeps original rotation', async ({page,context}) => {
  await context.route('**/assets/seasons-next/04/*.webp', route => route.abort());
  await ready(page);
  for (let i = 0; i < 14; i++) await page.clock.runFor(1000);
  await expect.poll(() => page.evaluate(() => seasonalClock.state().stalled)).toBe(true);
  const before = await ids(page);
  const phase = await page.evaluate(() => seasonalClock.state().phase);
  await page.clock.runFor(25000);
  expect(await ids(page)).toEqual(before);
  expect(await page.evaluate(() => seasonalClock.state().phase)).toBe(phase);
  await context.unroute('**/assets/seasons-next/04/*.webp');
  await page.getByRole('button', {name:'Resume animation', exact:true}).click();
  await expect.poll(() => page.locator('.visitor-panes .season-stack').count()).toBe(3);
  await tick(page);
  await context.route('**/assets/seasons-next/frames.json', route => route.abort());
  await ready(page);
  await expect(page.locator('#hero-motion svg')).toBeVisible();
  expect(await page.evaluate(() => Boolean(window.seasonalClock))).toBe(false);
  await tick(page);
});

test('visitor hero has no hover effect, tab stop or click target; narrative seasons resume below hero', async ({page}) => {
  await ready(page);
  const frame = page.locator('.visitor-image').first();
  await frame.hover();
  const styles = await frame.evaluate(node => {
    const s = getComputedStyle(node), after = getComputedStyle(node, '::after');
    return {cursor:s.cursor, transform:s.transform, border:s.borderTopWidth, after:after.content};
  });
  expect(styles).toEqual({cursor:'auto', transform:'none', border:'0px', after:'none'});
  await expect(page.locator('.visitor-panes a, .visitor-panes button, .visitor-panes [tabindex]')).toHaveCount(0);
  await page.evaluate(() => {
    const story = document.querySelector('.story');
    scrollTo(0, story.offsetTop + 100);
  });
  await page.clock.runFor(100);
  await expect.poll(() => page.locator('.story-photos .season-stack').count()).toBeGreaterThan(0);
  await expect.poll(() => page.evaluate(() => seasonalClock.state().running)).toBe(true);
});

test('pause works while seasonal manifest loads or is unavailable', async ({page,context}) => {
  let release;
  await context.route('**/assets/seasons-next/frames.json', async route => {
    await new Promise(resolve => { release = resolve; });
    await route.continue().catch(() => {});
  });
  await page.goto('/?display=visitor', {waitUntil:'domcontentloaded'});
  await expect(page.locator(panes)).toHaveCount(3);
  await expect.poll(() => Boolean(release)).toBe(true);
  await page.getByRole('button', {name:'Pause animation', exact:true}).click();
  const before = await ids(page);
  await page.clock.runFor(25000);
  expect(await ids(page)).toEqual(before);
  release();
  await expect.poll(() => page.evaluate(() => Boolean(window.seasonalClock))).toBe(true);
  await expect(page.getByRole('button', {name:'Resume animation', exact:true})).toBeVisible();
  await page.clock.runFor(25000);
  expect(await ids(page)).toEqual(before);
  await page.getByRole('button', {name:'Resume animation', exact:true}).click();
  await tick(page);
});
