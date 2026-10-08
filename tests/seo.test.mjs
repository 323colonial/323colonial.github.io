import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import test from 'node:test';
import { parseDocument } from 'htmlparser2';
import { selectAll, selectOne } from 'css-select';
import { textContent } from 'domutils';

const origin = 'https://323colonial.github.io/';
const pages = [
  ['index.html', '', '323 Colonial Dr · Berkeley Springs, WV · $499,000',
    'Explore 323 Colonial Dr in Berkeley Springs, WV: a 2-bedroom mountain home with 2 full baths, 1 half bath, a screened porch and an open deck.'],
  ['gallery.html', 'gallery.html', 'Photos · 323 Colonial Dr · Berkeley Springs, WV',
    'Explore 65 views of 323 Colonial Dr in Berkeley Springs, WV, including one labeled conceptual basement plan — not existing finished space.'],
];

for (const [file, route, title, description] of pages) {
  test(`${file}: canonical and home links use approved origin and routes`, () => {
    const doc = parseDocument(readFileSync(file, 'utf8'));
    const canonical = selectAll('link[rel="canonical"]', doc);
    assert.equal(canonical.length, 1);
    assert.equal(canonical[0].parent.name, 'head');
    assert.equal(canonical[0].attribs.href, origin + route);
    assert.equal(selectOne('.property-identity a', doc).attribs.href, '/');
    assert.equal(selectAll('a[href="index.html"], a[href="/index.html"]', doc).length, 0);
  });

  test(`${file}: unique search copy and consistent exterior share metadata`, () => {
    const doc = parseDocument(readFileSync(file, 'utf8'));
    const head = selectOne('head', doc);
    assert.equal(selectAll('title', doc).length, 1);
    assert.equal(textContent(selectOne('title', head)), title);
    const oneMeta = selector => {
      const tags = selectAll(selector, doc);
      assert.equal(tags.length, 1, selector);
      assert.equal(tags[0].parent, head, `${selector} belongs in head`);
      return tags[0].attribs.content;
    };
    assert.equal(oneMeta('meta[name="description"]'), description);
    const share = {
      'og:title': title, 'og:description': description, 'og:type': 'website',
      'og:url': origin + route, 'og:image': origin + 'assets/email/323-colonial-hero-small.gif',
      'og:image:type': 'image/gif', 'og:image:width': '300', 'og:image:height': '199',
      'og:image:alt': 'Exterior of 323 Colonial Dr in Berkeley Springs, West Virginia.',
    };
    for (const [property, content] of Object.entries(share)) {
      assert.equal(oneMeta(`meta[property="${property}"]`), content, property);
    }
    assert.doesNotMatch(description, /gigabit|finished basement|Active/);
    const bytes = readFileSync(new URL(share['og:image']).pathname.slice(1));
    assert.equal(bytes.subarray(0, 6).toString(), 'GIF89a');
    assert.equal(bytes.readUInt16LE(6), Number(share['og:image:width']));
    assert.equal(bytes.readUInt16LE(8), Number(share['og:image:height']));
  });
}

test('publish allowlist contains exactly required buyer files, never repository/private records', () => {
  assert.ok(existsSync('scripts/publish-files.txt'), 'explicit publish allowlist missing');
  const files = readFileSync('scripts/publish-files.txt', 'utf8').trim().split('\n');
  const modules = ['analytics-core.mjs', 'vendor/posthog-1.438.1.mjs', 'vendor/posthog-LICENSE'];
  const emailAssets = ['assets/email/323-colonial-hero-small.gif'];
  // Seasonal inventory is derived from the manifest the homepage names, never a hand list:
  // every generated frame of every tier, for photos that are in the hero or narrative.
  const home = parseDocument(readFileSync('index.html', 'utf8'));
  const manifestPath = selectOne('script[data-manifest]', home).attribs['data-manifest'];
  assert.equal(manifestPath, 'assets/seasons-next/frames.json');
  const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
  assert.deepEqual(manifest.tiers, ['large', 'small']);
  const animated = new Set(selectAll('.hero-photo figure, .story-photos figure', home).map(figure => figure.attribs['data-position']));
  const seasons = [];
  for (const [position, photo] of Object.entries(manifest.photos)) {
    if (!animated.has(position)) continue; // The runtime skips photos the page does not sequence.
    const id = position.padStart(2, '0');
    for (const key of photo.keys) {
      assert.ok(manifest.knots.includes(key) && key < manifest.steps, `photo ${position}: key ${key} is off the timing table`);
      if ((photo.original || []).includes(key)) continue; // Served by assets/listing, listed below.
      const name = String(Math.floor(key)).padStart(2, '0') + (key % 1 ? 'h' : '');
      for (const tier of manifest.tiers) seasons.push(`assets/seasons-next/${id}/${name}${tier === 'small' ? '-small' : ''}.webp`);
    }
  }
  assert.ok(seasons.length > 0);
  const expected = ['index.html', 'gallery.html', 'listing.css', 'gallery.js', 'listing.js', 'seasonal-hero.js', 'analytics.mjs', ...modules, manifestPath, ...seasons, ...emailAssets];
  const analytics = readFileSync('analytics.mjs', 'utf8');
  assert.ok(analytics.includes("from './analytics-core.mjs'"));
  assert.ok(analytics.includes("import('./vendor/posthog-1.438.1.mjs')"));
  assert.match(readFileSync('vendor/posthog-LICENSE', 'utf8'), /MIT License/);
  for (let n = 1; n <= 73; n++) {
    if ([40, 62, 63, 68, 69, 70, 71, 72].includes(n)) continue; // colonial-rp8: pruned from the site
    for (const suffix of ['', '-small']) expected.push(`assets/listing/${String(n).padStart(2, '0')}${suffix}.webp`);
  }
  assert.deepEqual([...files].sort(), expected.sort());
  // Frames are reached through the manifest, which the homepage script tag names.
  const referenced = new Set(['index.html', 'gallery.html', ...modules, ...seasons, ...emailAssets]);
  for (const [file] of pages) {
    const doc = parseDocument(readFileSync(file, 'utf8'));
    for (const node of selectAll('[href], [src], [srcset], [data-manifest], meta[property="og:image"]', doc)) {
      const attrs = node.attribs;
      const values = [attrs.href, attrs.src, attrs['data-manifest'], attrs.property === 'og:image' && attrs.content,
        ...(attrs.srcset || '').split(',').map(candidate => candidate.trim().split(/\s+/)[0])];
      for (const value of values.filter(Boolean)) {
        const url = new URL(value, origin + file);
        if (url.origin !== new URL(origin).origin) continue;
        const path = decodeURIComponent(url.pathname.slice(1)) || 'index.html';
        assert.ok(files.includes(path), `${file}: ${path} absent from allowlist`);
        referenced.add(path);
      }
    }
  }
  assert.deepEqual([...referenced].sort(), [...files].sort(), 'only page assets and explicitly approved email assets');
  for (const file of files) assert.ok(existsSync(file), file);
});
