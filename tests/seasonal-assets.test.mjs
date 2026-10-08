import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { copyFileSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import test from 'node:test';

const script = resolve('scripts/build-seasons-small.mjs');

test('every seasonal export matches its original tier dimensions', () => {
  const result = spawnSync(process.execPath, [script, '--check'], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stderr, '', 'dimension mismatches must not be warnings');
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
