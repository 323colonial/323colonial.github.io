import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, readFileSync, readdirSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import test from 'node:test';

const script = resolve('scripts/build-pages.mjs');

test('Pages artifact contains only allowlisted files, byte for byte', t => {
  const root = mkdtempSync(join(tmpdir(), 'colonial-pages-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const output = join(root, 'site');
  const result = spawnSync(process.execPath, [script, output], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  const expected = readFileSync('scripts/publish-files.txt', 'utf8').trim().split('\n').sort();
  const actual = readdirSync(output, { recursive: true, withFileTypes: true })
    .filter(entry => entry.isFile()).map(entry => join(entry.parentPath, entry.name).slice(output.length + 1)).sort();
  assert.deepEqual(actual, expected);
  for (const file of expected) assert.deepEqual(readFileSync(join(output, file)), readFileSync(file), file);
  const rerun = spawnSync(process.execPath, [script, output], { encoding: 'utf8' });
  assert.notEqual(rerun.status, 0, 'must not reuse output containing stale files');
});

test('Pages staging rejects unsafe, duplicate, missing, directory and symlink entries', t => {
  const root = mkdtempSync(join(tmpdir(), 'colonial-pages-invalid-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(join(root, 'scripts'));
  writeFileSync(join(root, 'index.html'), 'buyer page');
  symlinkSync('index.html', join(root, 'linked.html'));
  symlinkSync('scripts', join(root, 'linked-directory'));
  const invalid = ['../outside', '/etc/passwd', '.git/config', 'assets/../index.html',
    'index.html\nindex.html', 'missing.html', 'scripts', 'linked.html', 'linked-directory/publish-files.txt', ''];
  for (const [index, entry] of invalid.entries()) {
    writeFileSync(join(root, 'scripts/publish-files.txt'), entry + '\n');
    const result = spawnSync(process.execPath, [script, join(root, `output-${index}`)], { cwd: root, encoding: 'utf8' });
    assert.notEqual(result.status, 0, `must reject ${JSON.stringify(entry)}`);
    assert.match(result.stderr, /Invalid publication file|Duplicate publication file|ENOENT|Empty publication allowlist/);
  }
});
