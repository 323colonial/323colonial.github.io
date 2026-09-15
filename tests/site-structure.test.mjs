import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import test from 'node:test';

const publicPages = ['index.html', 'gallery.html', 'floorplans.html'];
const ownerPages = ['brochure.html', 'sale-prep.html'];
const pages = [...publicPages, ...ownerPages];
const html = Object.fromEntries(pages.map((file) => [file, existsSync(file) ? readFileSync(file, 'utf8') : '']));

for (const file of publicPages) {
  test(`${file} exposes buyer navigation and showing contact`, () => {
    assert.match(html[file], /aria-label="Buyer navigation"/);
    assert.match(html[file], /mailto:realtor@stevenhay\.com/);
    assert.match(html[file], /href="styles\.css"/);
    assert.match(html[file], /<a class="skip-link" href="#main-content">Skip to content<\/a>/);
    assert.match(html[file], /<main[^>]*id="main-content"/);
    assert.doesNotMatch(html[file], /<style\b/i);
  });
}

test('home keeps feature words separated when mobile line breaks hide', () => {
  const page = html['index.html'];
  assert.match(page, /Cathedral<br>\s+glass/);
  assert.match(page, /Fieldstone<br>\s+chimney/);
  assert.match(page, /Screened<br>\s+porch/);
});

test('home introduces bedroom and bath facts before features', () => {
  const intro = html['index.html'].split('<aside class="hero-summary">')[1].split('<ul')[0];
  assert.match(intro, /2 bedrooms · 2 full baths · 1 half bath/);
});

test('public sitemap contains three destinations, not owner records', () => {
  for (const file of publicPages) {
    const nav = html[file].match(/<nav[^>]*aria-label="Buyer navigation"[^>]*>([\s\S]*?)<\/nav>/)?.[1] || '';
    const links = [...nav.matchAll(/<a\b([^>]*)>([^<]+)<\/a>/g)];
    assert.deepEqual(links.map((link) => link[2]), ['The house', 'Gallery', 'Floor plans'], file);
    assert.deepEqual(links.map((link) => link[1].match(/href="([^"]+)"/)[1]), publicPages, file);
    assert.equal(links.filter((link) => link[1].includes('aria-current="page"')).length, 1, file);
    assert.match(links[publicPages.indexOf(file)][1], /aria-current="page"/);
    assert.doesNotMatch(html[file], /brochure\.html|sale-prep\.html|Planning records|Working notes|Paint takeoff|Budgeting|product (?:TBD|not selected)|Planned-work visualisation/i);
  }
});

test('home describes finished rooms and outdoor living without adding bedrooms', () => {
  const page = html['index.html'];
  for (const fact of [/red oak/i, /granite/i, /Venetian Bronze/, /antiqued.brass/i, /Debonair/, /Oyster Bay/, /Sea Salt/, /Dark Walnut/, /hot tub[\s\S]*open dark sky/i, /unfinished walk-out basement/i]) assert.match(page, fact);
  assert.doesNotMatch(page.replace(/<[^>]*>/g, ''), /will be|planned|sale-prep|honestly shown|overflow sleeping/i);
  const afterOutdoors = page.slice(page.indexOf('id="outdoors"')).split('</section>')[1];
  assert.match(afterOutdoors, /class="showing-band"/);
  assert.match(afterOutdoors, />Request a showing<\/a>/);
});

test('home restores paint swatches in a compact room detail', () => {
  const rooms = html['index.html'].split('id="rooms"')[1].split('</section>')[0];
  const detail = rooms.match(/<details class="paint-palette" id="paint-colors">([\s\S]*?)<\/details>/)?.[1];
  assert.ok(detail, 'collapsed paint detail missing from room section');
  assert.match(detail, /<summary>Paint colors &amp; finishes<\/summary>/);
  assert.match(detail, /Sherwin-Williams/);
  assert.match(detail, /Screen swatches are approximate; verify physical chips in daylight/);
  const swatches = [...detail.matchAll(/<div class="swatch swatch--[^\"]+">([\s\S]*?)<\/p><\/div>/g)];
  assert.equal(swatches.length, 6);
  for (const [index, name, code, room] of [
    [0, 'Alabaster', 'SW 7008', 'Hallway'],
    [1, 'Debonair', 'SW 9139', 'Main-floor bedroom'],
    [2, 'Sea Salt', 'SW 6204', 'Both full baths'],
    [3, 'Oyster Bay', 'SW 6206', 'Upstairs bedroom and walk-in'],
    [4, 'Pewter Green', 'SW 6208', 'Front, back and garage doors'],
    [5, 'Dark Walnut', 'Solid stain', 'Deck floor'],
  ]) {
    for (const text of [name, code, room]) assert.ok(swatches[index][1].includes(text), text);
    assert.match(swatches[index][1], /class="swatch-color" aria-hidden="true"/);
  }
});

test('public photographs retain provenance and every edited image has attached disclosure', () => {
  for (const file of publicPages) {
    assert.match(html[file], /Prior-listing photo/i);
    assert.match(html[file], /Bright MLS/);
    for (const figure of html[file].matchAll(/<figure\b[\s\S]*?<\/figure>/g)) {
      const src = figure[0].match(/<img[^>]*src="([^"]+)"/)?.[1];
      if (!src || /(?:photo-|plan-)/.test(src) || src === 'assets/plates/room-photo.png') continue;
      assert.match(figure[0], /<span class="status-label">Digitally simulated image<\/span>/, `${file}: ${src}`);
    }
  }
  assert.match(html['index.html'], /assets\/plates\/exterior-photo\.png/);
  assert.match(html['gallery.html'], /images\/primary-debonair\.webp/);
  assert.match(html['gallery.html'], /images\/deck-hottub-v3\.png/);
  assert.match(html['gallery.html'], /colours and staging are approximate/i);
});

test('owner records remain separate and preserve purchasing caveats', () => {
  for (const file of ownerPages) {
    assert.match(html[file], /<meta name="robots" content="noindex, nofollow">/);
    assert.match(html[file], /aria-label="Owner records"/);
    assert.doesNotMatch(html[file], /aria-label="Buyer navigation"/);
    assert.match(html[file], /manufacturer and product (?:are )?not selected/i);
  }
});

test('floor-plan route leads with current photography before drawings', () => {
  const page = html['floorplans.html'];
  const currentPhoto = page.search(/images\/photo-[^"']+\.jpg/);
  const firstPlan = page.search(/images\/plan-[^"']+\.png/);
  assert.ok(currentPhoto >= 0, 'current-property photograph missing');
  assert.ok(firstPlan > currentPhoto, 'reference drawings must follow current-property photography');
});

test('floor-plan introduction links directly to both named sheets', () => {
  const plans = html['floorplans.html'];
  const intro = plans.match(/<header class="record-intro record-intro--plans">([\s\S]*?)<\/header>/)?.[1] || '';
  assert.match(intro, /<nav[^>]*aria-label="Floor-plan sheets"/);
  for (const [id, label] of [['main-floor', 'Main floor'], ['second-floor', 'Second floor']]) {
    assert.match(intro, new RegExp(`<a[^>]*href="#${id}"[^>]*>${label}</a>`));
    assert.match(plans, new RegExp(`<section[^>]*id="${id}"[^>]*aria-labelledby="${id}-heading"`));
  }
});

test('public floorplans use marketing crops and approximate areas', () => {
  const plans = html['floorplans.html'];
  assert.match(plans, /images\/plan-main-marketing\.png/);
  assert.match(plans, /images\/plan-second-marketing\.png/);
  assert.match(plans, /approximate square footage/i);
  assert.match(readFileSync('styles.css', 'utf8'), /\.plan-sheet img \{[^}]*height: auto/);
  for (const name of ['main', 'second']) {
    const path = `images/plan-${name}-marketing.png`;
    const png = readFileSync(path);
    assert.equal(png.subarray(1, 4).toString(), 'PNG');
    assert.ok(png.readUInt32BE(16) > png.readUInt32BE(20), 'plan must remain landscape');
    assert.match(plans, new RegExp(`href="${path}"`), 'full-size plan must be accessible');
  }
  assert.doesNotMatch(plans, /Sheet A-|verify every dimension|Orientation and pricing only/i);
  assert.equal((html['index.html'].match(/images\/plan-main-marketing\.png/g) || []).length, 2);
  for (const file of ['index.html', 'floorplans.html']) {
    assert.doesNotMatch(html[file], /(?:images\/plan-A-[45]|assets\/plates\/plan-image)\.png/);
  }
});

test('planning routes disclose reference and estimate status', () => {
  assert.match(html['brochure.html'], /Planning record/i);
  assert.match(html['brochure.html'], /Planned-work visualisation/i);
  assert.match(html['floorplans.html'], /reference plan/i);
  assert.match(html['floorplans.html'], /not (?:field-measured|for construction or permit)/i);
  assert.match(html['sale-prep.html'], /Planning record/i);
  assert.match(html['sale-prep.html'], /budgeting (?:range|estimate)/i);
});

test('approved paint palette uses matching planned images, not superseded renders', () => {
  const brochure = html['brochure.html'];
  for (const [name, code, room] of [
    ['Alabaster', '7008', 'hallway'],
    ['Debonair', '9139', 'primary bedroom'],
    ['Sea Salt', '6204', 'primary and upstairs baths'],
    ['Oyster Bay', '6206', 'upstairs bedroom'],
    ['Pewter Green', '6208', 'front/back and garage doors'],
  ]) {
    assert.ok(brochure.includes(`<strong>${name}</strong><span>SW ${code} · ${room}`), `${name} swatch assignment`);
    assert.ok(html['sale-prep.html'].includes(`SW ${code} ${name}`), `${name} sale-prep record`);
  }
  for (const file of ownerPages) {
    assert.match(html[file], /Dark Walnut solid stain/);
    assert.match(html[file], /manufacturer and product (?:are )?not selected/i);
    assert.match(html[file], /older visualisations/i);
    assert.doesNotMatch(html[file], /Acacia Haze/);
  }
  for (const [image, colour] of [
    ['approach-pewter-green.webp', 'SW 6208 Pewter Green'],
    ['entry-pewter-green.webp', 'SW 6208 Pewter Green'],
    ['primary-debonair.webp', 'SW 9139 Debonair'],
    ['mainbath-2-seasalt.png', 'SW 6204 Sea Salt'],
    ['bedroom-oyster-bay.webp', 'SW 6206 Oyster Bay'],
    ['upbath-sea-salt.webp', 'SW 6204 Sea Salt'],
  ]) {
    const figure = brochure.split('<figure').find((part) => part.split('</figure>')[0].includes(`images/${image}`))?.split('</figure>')[0] || '';
    assert.ok(figure.includes(colour), `${image}: approved colour caption missing`);
    assert.match(figure, /Planned-work visualisation/);
    assert.doesNotMatch(figure, /older palette|Older visualisation|not (?:Debonair|Oyster Bay|Sea Salt)/);
    assert.ok(readFileSync(`images/${image}`).length > 10000, `${image}: image missing or empty`);
  }
  assert.match(html['sale-prep.html'], /images\/approach-pewter-green\.webp/);
  for (const page of Object.values(html)) {
    assert.doesNotMatch(page, /images\/(?:master-r6-vancourtland-king|bed2-r7-pewter-king|upbath-6-pewter|approach-green-trees|entry-green-door)\.png/);
  }
  for (const file of ['brochure.html', 'sale-prep.html']) {
    const current = html[file].search(/images\/photo-/);
    const planned = html[file].indexOf('class="status-label">Planned-work visualisation');
    assert.ok(current >= 0 && planned > current, `${file}: real photography must precede planned images`);
  }
  const takeoff = brochure.slice(brochure.indexOf('id="takeoff-heading"'));
  assert.doesNotMatch(takeoff, /Van Courtland|Revere Pewter|White Dove/);
  assert.match(html['sale-prep.html'], /Historical budget/);
  assert.match(html['sale-prep.html'], /excludes hallway and bedroom repainting/);
  const css = readFileSync('styles.css', 'utf8');
  assert.match(css, /\.swatch--debonair .swatch-color \{ background: #90a0a6; \}/);
  assert.match(css, /\.swatch--oyster-bay .swatch-color \{ background: #aeb3a9; \}/);
  assert.match(brochure, /Screen swatches are approximate/);
});

test('colour edits retain source provenance and immutable property evidence', () => {
  const record = JSON.parse(readFileSync('images/planned-colours.json', 'utf8'));
  const digest = (path) => createHash('sha256').update(readFileSync(path)).digest('hex');
  for (const edit of record.edits) {
    assert.equal(digest(edit.source), edit.source_sha256, `${edit.source}: source changed`);
    assert.equal(digest(edit.target), edit.sha256, `${edit.target}: inspected output changed`);
    assert.notEqual(edit.sha256, edit.source_sha256, 'old render merely renamed');
    const image = readFileSync(edit.target);
    assert.equal(image.subarray(8, 12).toString(), 'WEBP');
    assert.ok(image.length < 400000, `${edit.target}: exceeds 400 KB budget`);
  }
  for (const [path, hash] of Object.entries(record.preserved_evidence_sha256)) {
    assert.equal(digest(path), hash, `${path}: property evidence changed`);
  }
});

test('product record names prospective buyers as primary', () => {
  const product = readFileSync('PRODUCT.md', 'utf8');
  assert.match(product, /Prospective buyers? (?:are|is) primary/i);
  assert.doesNotMatch(product, /Owner is primary user/i);
});
