import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { chmodSync, copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import test from 'node:test';

const script = resolve('scripts/build-seasons-small.mjs');

test('every seasonal export matches its original tier dimensions', () => {
  const result = spawnSync(process.execPath, [script, '--check'], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stderr, '', 'dimension mismatches must not be warnings');
});

test('photo73 uses four cleaned seasonal anchors without replacing its gallery original', () => {
  const manifest = JSON.parse(readFileSync('assets/seasons-next/frames.json', 'utf8'));
  assert.deepEqual(manifest.photos['73'], { keys: [0, 3, 6, 9], original: [] });
  const published = readFileSync('scripts/publish-files.txt', 'utf8').trim().split('\n');
  for (const suffix of ['', '-small']) {
    const original = `assets/listing/73${suffix}.webp`;
    assert.ok(published.includes(original));
    for (const key of ['00', '03', '06', '09']) {
      const frame = `assets/seasons-next/73/${key}${suffix}.webp`;
      assert.ok(published.includes(frame), frame);
      assert.ok(existsSync(frame), frame);
    }
    assert.notDeepEqual(readFileSync(`assets/seasons-next/73/00${suffix}.webp`), readFileSync(original));
    assert.ok(!published.includes(`assets/seasons-next/73/08${suffix}.webp`));
  }
});

test('seasonal checker rejects a wrong-size large frame even with a valid small tier', t => {
  const root = mkdtempSync(join(tmpdir(), 'colonial-seasonal-size-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(join(root, 'assets/listing'), { recursive: true });
  mkdirSync(join(root, 'assets/seasons-next/02'), { recursive: true });
  for (const suffix of ['', '-small']) {
    copyFileSync(`assets/listing/02${suffix}.webp`, join(root, `assets/listing/02${suffix}.webp`));
    copyFileSync('assets/listing/02-small.webp', join(root, `assets/seasons-next/02/03${suffix}.webp`));
  }
  writeFileSync(join(root, 'assets/seasons-next/frames.json'), JSON.stringify({
    steps: 12, knots: [0, 3, 6, 9, 12], tiers: ['large', 'small'], photos: { 2: { keys: [3] } },
  }));
  const result = spawnSync(process.execPath, [script, '--check'], { cwd: root, encoding: 'utf8' });
  assert.equal(result.status, 1, result.stderr);
  assert.match(result.stderr, /error: assets\/seasons-next\/02\/03\.webp: 720x479, original is 1280x851/);
});


test('default build replaces a stale same-dimension small tier; check is structural only', t => {
  const root = mkdtempSync(join(tmpdir(), 'colonial-seasonal-replacement-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(join(root, 'assets/listing'), { recursive: true });
  mkdirSync(join(root, 'assets/seasons-next/02'), { recursive: true });
  mkdirSync(join(root, 'bin'));
  // Minimal dimension-readable VP8L headers; encoder double copies payload to isolate freshness policy
  // from ImageMagick provisioning. Real encoder recipe stays covered by local smoke QA.
  const webp = value => {
    const image = Buffer.alloc(32, value);
    image.write('RIFF', 0); image.write('WEBPVP8L', 8); image.writeUInt32LE(0, 21);
    return image;
  };
  const original = webp(1), replacement = webp(2);
  for (const file of ['assets/listing/02.webp', 'assets/listing/02-small.webp',
    'assets/seasons-next/02/03.webp', 'assets/seasons-next/02/03-small.webp']) writeFileSync(join(root, file), original);
  writeFileSync(join(root, 'assets/seasons-next/frames.json'), JSON.stringify({
    steps: 12, knots: [0, 3, 6, 9, 12], tiers: ['large', 'small'], photos: { 2: { keys: [3] } },
  }));
  const encoder = join(root, 'bin/magick');
  writeFileSync(encoder, `#!${process.execPath}\nrequire('node:fs').copyFileSync(process.argv[2], process.argv.at(-1));\n`);
  chmodSync(encoder, 0o755);
  const options = { cwd: root, encoding: 'utf8', env: { ...process.env, PATH: `${join(root, 'bin')}:${process.env.PATH}` } };
  const run = (...args) => spawnSync(process.execPath, [script, ...args], options);
  const large = join(root, 'assets/seasons-next/02/03.webp'), small = join(root, 'assets/seasons-next/02/03-small.webp');
  writeFileSync(large, replacement);
  const check = run('--check');
  assert.equal(check.status, 0, check.stderr);
  assert.deepEqual(readFileSync(small), original, '--check must not modify pixels or claim freshness');
  const build = run();
  assert.equal(build.status, 0, build.stderr);
  assert.deepEqual(readFileSync(small), replacement, 'same dimensions do not prove fresh pixels');
  assert.equal(run('--check').status, 0);
  assert.deepEqual(readFileSync(large), replacement, 'large source untouched');
});
