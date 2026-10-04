import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { parseFrontmatter } from '../.pi/skills/impeccable/scripts/detector/design-system.mjs';

test('Impeccable HTML detector runs without degraded parser fallback', () => {
  const result = spawnSync(process.execPath, [
    '.pi/skills/impeccable/scripts/detect.mjs', '--json', 'index.html', 'gallery.html', 'listing.css',
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
  const design = parseFrontmatter(read('DESIGN.md'));
  const sidecar = JSON.parse(read('.impeccable/design.json'));
  assert.equal(sidecar.schemaVersion, 2);
  assert.deepEqual(Object.keys(sidecar.extensions.colorMeta).sort(), Object.keys(design.colors).sort());
  assert.deepEqual(Object.keys(sidecar.extensions.typographyMeta).sort(), Object.keys(design.typography).sort());
  assert.deepEqual(sidecar.extensions.breakpoints.map(item => item.value), ['1000px', '700px']);
  // Panel previews read each role independently; they cannot inherit from prose.
  for (const [name, role] of Object.entries(design.typography)) {
    assert.ok(role.fontFamily, `Missing preview font: ${name}`);
  }
  assert.equal(design.typography['story-title-mobile'].lineHeight, 1.15);
  assert.equal(design.typography['contact-title'].letterSpacing, '-0.02em');
  assert.equal(design.typography['property-mark-mobile'].lineHeight, 1.65);
  for (const component of sidecar.components) {
    assert.ok(design.components[component.refersTo], `Unknown component: ${component.refersTo}`);
  }
  assert.deepEqual(sidecar.extensions.shadows, []);
  assert.deepEqual(sidecar.extensions.motion, []);
  assert.doesNotMatch(JSON.stringify(sidecar), /Quilt|Woodland Survey|Planning Table|Palette Swatch/);
});
