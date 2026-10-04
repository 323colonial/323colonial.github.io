import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import test from 'node:test';

test('Impeccable HTML detector runs without degraded parser fallback', () => {
  const result = spawnSync(process.execPath, [
    '.pi/skills/impeccable/scripts/detect.mjs', '--json', 'index.html',
  ], { cwd: new URL('../', import.meta.url), encoding: 'utf8' });
  assert.equal(result.error, undefined);
  // Exit 2 reports design findings; exit 1 reports a detector error.
  assert.ok([0, 2].includes(result.status), result.stderr);
  assert.doesNotMatch(result.stderr, /DEGRADED|Falling back to regex/);
  assert.ok(Array.isArray(JSON.parse(result.stdout)));
});
