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
    'Explore 73 views of 323 Colonial Dr in Berkeley Springs, WV, including one labeled conceptual basement plan — not existing finished space.'],
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
      'og:url': origin + route, 'og:image': origin + 'assets/listing/01.webp',
      'og:image:type': 'image/webp', 'og:image:width': '1600', 'og:image:height': '1060',
      'og:image:alt': 'Exterior of 323 Colonial Dr in Berkeley Springs, West Virginia.',
    };
    for (const [property, content] of Object.entries(share)) {
      assert.equal(oneMeta(`meta[property="${property}"]`), content, property);
    }
    assert.doesNotMatch(description, /gigabit|finished basement|Active/);
    const bytes = readFileSync('assets/listing/01.webp');
    assert.equal(bytes.subarray(0, 4).toString(), 'RIFF');
    assert.equal(bytes.subarray(8, 12).toString(), 'WEBP');
    const photo = JSON.parse(readFileSync('assets/listing/manifest.json')).photos[0];
    const full = photo.derivatives.find(image => image.path === 'assets/listing/01.webp');
    assert.equal(photo.position, 1);
    assert.equal(full.width, Number(share['og:image:width']));
    assert.equal(full.height, Number(share['og:image:height']));
  });
}

test('publish allowlist contains exactly required buyer files, never repository/private records', () => {
  assert.ok(existsSync('scripts/publish-files.txt'), 'explicit publish allowlist missing');
  const files = readFileSync('scripts/publish-files.txt', 'utf8').trim().split('\n');
  const expected = ['index.html', 'gallery.html', 'listing.css', 'gallery.js', 'listing.js'];
  for (let n = 1; n <= 73; n++) {
    for (const suffix of ['', '-small']) expected.push(`assets/listing/${String(n).padStart(2, '0')}${suffix}.webp`);
  }
  assert.deepEqual([...files].sort(), expected.sort());
  const referenced = new Set(['index.html', 'gallery.html']);
  for (const [file] of pages) {
    const doc = parseDocument(readFileSync(file, 'utf8'));
    for (const node of selectAll('[href], [src], [srcset], meta[property="og:image"]', doc)) {
      const attrs = node.attribs;
      const values = [attrs.href, attrs.src, attrs.property === 'og:image' && attrs.content,
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
  assert.deepEqual([...referenced].sort(), [...files].sort(), 'no unused assets');
  for (const file of files) assert.ok(existsSync(file), file);
});
