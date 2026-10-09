import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { parse } from 'yaml';

test('Impeccable HTML detector runs without degraded parser fallback', () => {
  const result = spawnSync('.pi/skills/impeccable/scripts/impeccable', [
    'detect', '--json', 'index.html', 'gallery.html', 'listing.css',
  ], { cwd: new URL('../', import.meta.url), encoding: 'utf8' });
  assert.equal(result.error, undefined);
  // Exit 2 reports design findings; exit 1 reports a detector error.
  assert.ok([0, 2].includes(result.status), result.stderr);
  assert.doesNotMatch(result.stderr, /DEGRADED|Falling back to regex/);
  const findings = JSON.parse(result.stdout);
  assert.ok(Array.isArray(findings));
  assert.deepEqual(findings.filter(item => item.antipattern.startsWith('design-system-')), []);
});

test('Impeccable sidecar describes current listing tokens and breakpoints', () => {
  const read = path => readFileSync(new URL(`../${path}`, import.meta.url), 'utf8');
  const frontmatter = read('DESIGN.md').match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
  assert.ok(frontmatter, 'DESIGN.md must have YAML frontmatter');
  const design = parse(frontmatter[1]);
  const sidecar = JSON.parse(read('.impeccable/design.json'));
  assert.equal(sidecar.schemaVersion, 2);
  assert.deepEqual(Object.keys(sidecar.extensions.colorMeta).sort(), Object.keys(design.colors).sort());
  assert.deepEqual(Object.keys(sidecar.extensions.typographyMeta).sort(), Object.keys(design.typography).sort());
  assert.deepEqual(sidecar.extensions.breakpoints.map(item => item.value), [
    '1100px', '1000px', '800px', '700px', '360px', 'max-height: 500px',
  ]);
  // Panel previews read each role independently; they cannot inherit from prose.
  for (const [name, role] of Object.entries(design.typography)) {
    assert.ok(role.fontFamily, `Missing preview font: ${name}`);
  }
  assert.equal(design.typography.narrative.lineHeight, 1.65);
  assert.equal(design.typography.metadata.fontSize, '12px');
  assert.equal(design.typography['property-mark-mobile'].lineHeight, 1.15);
  assert.equal(design.colors.mahogany, '#593a32');
  assert.equal(design.colors['greek-villa'], '#f0ece2');
  assert.equal(design.colors['pewter-green'], undefined);
  for (const component of sidecar.components) {
    assert.ok(design.components[component.refersTo], `Unknown component: ${component.refersTo}`);
  }
  assert.deepEqual(sidecar.extensions.shadows, []);
  assert.equal(sidecar.extensions.motion[0].name, 'native-scroll-photo-step');
  assert.doesNotMatch(JSON.stringify(sidecar), /Quilt|Woodland Survey|Planning Table|Palette Swatch/);
});
