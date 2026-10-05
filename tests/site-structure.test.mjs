import assert from 'node:assert/strict';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import test from 'node:test';

test('only buyer pages remain at the site root', () => {
  assert.deepEqual(readdirSync('.').filter(file => file.endsWith('.html')).sort(), ['gallery.html', 'index.html']);
  for (const file of ['brochure.html', 'floorplans.html', 'sale-prep.html', 'styles.css', 'tests/table-contrast.html']) {
    assert.equal(existsSync(file), false, `${file}: retired route or dependency returned`);
  }
});

test('durable finish specification survives removal of owner pages', () => {
  const product = readFileSync('PRODUCT.md', 'utf8');
  for (const [name, code, finish] of [
    ['Alabaster', '7008', 'Emerald Interior Matte'],
    ['Debonair', '9139', 'Emerald Interior Matte'],
    ['Sea Salt', '6204', 'Duration Home Satin'],
    ['Oyster Bay', '6206', 'Emerald Interior Matte'],
    ['Pewter Green', '6208', 'Emerald Urethane Trim Enamel Satin'],
    ['Traditional Mahogany', '3080', 'SuperDeck Exterior Waterborne Solid Color Deck Stain'],
  ]) {
    const row = product.split('\n').find(line => line.startsWith('|') && line.includes(name)) || '';
    for (const text of [name, `SW ${code}`, finish]) assert.ok(row.includes(text), `${name}: durable ${text}`);
  }
  assert.match(product, /Sherwin-Williams/);
  assert.match(product, /814 S Loudoun St, Winchester, VA 22601-4597/);
  assert.match(product, /Confirm product compatibility/);
  assert.doesNotMatch(product, /\bgal(?:lon)?s?\b|\bqt\b|Paint takeoff/i);
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
