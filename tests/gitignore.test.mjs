import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import test from 'node:test';

test('git ignores local output without hiding durable project state', () => {
  const ignored = [
    '.DS_Store', 'assets/.DS_Store', 'assets/nested/.DS_Store',
    '__pycache__/cache', 'tests/__pycache__/cache',
    'module.pyc', 'tests/module.pyc', 'tests/module.pyo',
    '.pi/artifacts/run/output.png', '.impeccable/critique/report.md',
    'node_modules/generated-package.json', '.cloudflare.snippet',
    '.dolt/data', 'local.db', '.beads-credential-key', '.beads/proxieddb/data',
  ];
  const durable = [
    '.beads/issues.jsonl', '.beads/interactions.jsonl', '.beads/config.yaml',
    '.pi/plans/new-plan.md', '.pi/skills/impeccable/SKILL.md',
    '.impeccable/design.json', '.impeccable/config.json',
    '.impeccable/build/spec.json', '.impeccable/mocks/new-design.png',
    '.impeccable/review/desktop.png', '.impeccable/surfaces/index-html.md',
    'nested/.pi/artifacts/source.png', 'nested/.impeccable/critique/source.md',
    'assets/new-image.png', 'images/new-image.webp',
    'index.html', 'listing.css', 'PRODUCT.md', 'test_design.py',
    'flake.nix', 'flake.lock', 'package.json', 'package-lock.json',
  ];
  const result = spawnSync('git', [
    '-c', 'core.excludesFile=/dev/null', 'check-ignore', '--no-index', '--stdin',
  ], {
    cwd: new URL('../', import.meta.url),
    input: [...ignored, ...durable].join('\n') + '\n',
    encoding: 'utf8',
  });
  assert.equal(result.error, undefined);
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(result.stdout.trimEnd().split('\n'), ignored);
});
