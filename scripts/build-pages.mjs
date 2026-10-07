import assert from 'node:assert/strict';
import { copyFileSync, mkdirSync, readFileSync, realpathSync, statSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';

assert.ok(process.argv[2], 'Usage: node scripts/build-pages.mjs NEW_OUTPUT_DIRECTORY');
const root = realpathSync('.');
const files = readFileSync('scripts/publish-files.txt', 'utf8').trim().split('\n');
assert.ok(files[0], 'Empty publication allowlist');
assert.equal(new Set(files).size, files.length, 'Duplicate publication file');
for (const file of files) {
  assert.ok(file.split('/').every(part => /^[a-zA-Z0-9][a-zA-Z0-9._-]*$/.test(part)), `Invalid publication file: ${file}`);
  const source = join(root, file);
  assert.ok(realpathSync(source) === source && statSync(source).isFile(), `Invalid publication file: ${file}`);
}

// Refuse existing output so stale or private files can never enter the artifact.
const output = resolve(process.argv[2]);
mkdirSync(output);
for (const file of files) {
  const target = join(output, file);
  mkdirSync(dirname(target), { recursive: true });
  copyFileSync(join(root, file), target);
}
console.log(`Staged ${files.length} buyer files in ${output}`);
