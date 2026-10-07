import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import test from 'node:test';

const dir = 'assets/walkthrough/';
const scene = JSON.parse(readFileSync(dir + 'scene.json', 'utf8'));
const page = readFileSync('walkthrough/index.html', 'utf8');
const script = readFileSync('walkthrough/walkthrough.js', 'utf8');

test('walkthrough assets referenced by the scene exist', () => {
  assert.ok(existsSync(dir + 'house.glb'));
  assert.ok(existsSync(dir + 'sky.jpg'));
  assert.ok(scene.pages.length > 0);
  assert.ok(existsSync(dir + 'lightmaps.json'));
  if (scene.baked !== false) {
    for (const p of scene.pages) assert.ok(existsSync(`${dir}lm_${p}.webp`), `lightmap ${p}`);
    for (const p of scene.photoPages || []) assert.ok(existsSync(`${dir}photo_${p}.webp`), `photo atlas ${p}`);
  }
  const textures = new Set(Object.values(scene.materials).map((m) => m.tex).filter(Boolean));
  for (const t of textures) assert.ok(existsSync(`${dir}tex/${t}.webp`), `texture ${t}`);
});

test('walkthrough collision data is usable', () => {
  assert.ok(scene.solids.length > 100);
  for (const s of scene.solids) assert.ok(s.length === 6 && s.every(Number.isFinite) && s[5] > s[4]);
  assert.ok(scene.floors.some((f) => f.ramp), 'stair ramp');
  assert.ok(scene.floors.some((f) => f.z > 2.5), 'upper floor');
  assert.equal(scene.terrain.h.length, scene.terrain.n ** 2);
});

test('walkthrough page loads only local code and offers a way back', () => {
  assert.ok(!/https?:\/\//.test(page.replace(/<meta[^>]*>/g, '')), 'no remote resources');
  assert.match(page, /"three": "\.\.\/vendor\/three-0\.186\.1\/three\.module\.js"/);
  for (const f of ['three.module.js', 'three.core.js', 'addons/loaders/GLTFLoader.js', 'addons/loaders/DRACOLoader.js',
    'addons/utils/BufferGeometryUtils.js', 'addons/utils/SkeletonUtils.js', 'draco/draco_decoder.wasm', 'draco/draco_wasm_wrapper.js', 'LICENSE']) {
    assert.ok(existsSync('vendor/three-0.186.1/' + f), f);
  }
  assert.match(page, /href="\.\.\/"/);
  assert.match(page, /approximate 3D model/i);
  assert.match(script, /requestPointerLock/);
});

// Flood-fill the collision plan at one storey with the player's radius (doors open).
function reachable(from, z, targets) {
  const R = 0.22, H = 1.74, STEP = 0.36, G = 0.08, ft = 0.3048;
  const segs = scene.solids.filter((s) => z + STEP < s[5] && z + H > s[4]);
  const free = (x, y) => segs.every(([ax, ay, bx, by]) => {
    const ex = bx - ax, ey = by - ay, L2 = ex * ex + ey * ey;
    const t = L2 ? Math.min(Math.max(((x - ax) * ex + (y - ay) * ey) / L2, 0), 1) : 0;
    return Math.hypot(x - ax - ex * t, y - ay - ey * t) >= R;
  });
  const key = (i, j) => i * 4096 + j;
  const cell = (v) => Math.round((v * ft) / G);
  const seen = new Set([key(cell(from[0]) + 1000, cell(from[1]) + 1000)]);
  const queue = [[cell(from[0]), cell(from[1])]];
  while (queue.length) {
    const [i, j] = queue.pop();
    for (const [di, dj] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const a = i + di, b = j + dj, k = key(a + 1000, b + 1000);
      if (seen.has(k) || a * G < -6 || a * G > 23 || b * G < -5 || b * G > 12) continue;
      if (!free(a * G, b * G)) continue;
      seen.add(k);
      queue.push([a, b]);
    }
  }
  return Object.fromEntries(Object.entries(targets).map(([n, [x, y]]) => [n, seen.has(key(cell(x) + 1000, cell(y) + 1000))]));
}

test('every room can be walked into', () => {
  const ft = 0.3048;
  const main = reachable([22.2, 2.0], 0, {
    'great room': [4.5, 8], 'kitchen sink aisle': [17, 23.6], 'kitchen range aisle': [20, 21.6], hall: [29, 15.6],
    'half bath': [28, 24], mudroom: [40.5, 24.6], 'mudroom past the bench': [36.5, 24.0], 'primary bedroom': [35, 8], 'primary bath': [41, 17.8],
    'screened porch': [31.3, 31], deck: [-4, 13], 'deck by the south slider': [-1.6, 22.6], 'front porch': [22.2, -3], 'side yard by the porch steps': [53, 31],
  });
  const upper = reachable([22.2, 14.9], 9.1 * ft, {
    loft: [39, 15], 'upstairs bath': [25.4, 21.8], 'upstairs bedroom': [58, 14], 'loft dormer': [36.7, 2.3],
  });
  for (const [name, ok] of Object.entries({ ...main, ...upper })) assert.ok(ok, `cannot reach ${name}`);
});

test('swinging doors are exported with their hinge and opening', () => {
  assert.ok(scene.doors.length >= 6);
  for (const d of scene.doors) assert.ok(d.name && d.hinge.length === 2 && d.seg.length === 4 && Math.abs(d.open) > 1);
});

test('the shell is closed: no ray from inside a room escapes except through glass or an open slider', () => {
  assert.ok(scene.checks.rays > 10000);
  assert.equal(scene.checks.escaped, 0, JSON.stringify(scene.checks.examples.slice(0, 5)));
});
