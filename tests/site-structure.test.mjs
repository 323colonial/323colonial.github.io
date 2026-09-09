import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const pages = ['index.html', 'brochure.html', 'floorplans.html', 'sale-prep.html'];
const html = Object.fromEntries(pages.map((file) => [file, readFileSync(file, 'utf8')]));

for (const file of pages) {
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

test('home leads with current photography and separates planned visuals', () => {
  const page = html['index.html'];
  const current = page.indexOf('id="current-condition"');
  const planned = page.indexOf('id="planned-visuals"');
  assert.ok(current >= 0, 'current-condition section missing');
  assert.ok(planned > current, 'planned visuals must follow current condition');
  assert.match(page.slice(planned), /Planned-work visualisation/i);
});

test('floor-plan route leads with current photography before drawings', () => {
  const page = html['floorplans.html'];
  const currentPhoto = page.search(/images\/photo-[^"']+\.jpg/);
  const firstPlan = page.search(/images\/plan-[^"']+\.png/);
  assert.ok(currentPhoto >= 0, 'current-property photograph missing');
  assert.ok(firstPlan > currentPhoto, 'reference drawings must follow current-property photography');
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

test('product record names prospective buyers as primary', () => {
  const product = readFileSync('PRODUCT.md', 'utf8');
  assert.match(product, /Prospective buyers? (?:are|is) primary/i);
  assert.doesNotMatch(product, /Owner is primary user/i);
});
