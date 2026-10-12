import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';
import { parseDocument } from 'htmlparser2';
import { selectAll } from 'css-select';

function selection() {
  assert.ok(existsSync('visitor-display.js'), 'visitor display runtime missing');
  const source = readFileSync('visitor-display.js', 'utf8');
  const marker = "  const hero = document.querySelector('.hero-photo');";
  assert.ok(source.includes(marker));
  const context = vm.createContext({ URLSearchParams, location: {search: '?display=visitor'} });
  vm.runInContext(source.replace(marker, 'globalThis.selection = { EXTERIORS, SMALL, nextPhoto, movement: typeof movement === "function" ? movement : null }; return;\n' + marker), context);
  return context.selection;
}

test('reviewed pools contain only included distinct originals, never seasonal derivatives', () => {
  const {EXTERIORS, SMALL} = selection();
  assert.deepEqual([...EXTERIORS].sort((a,b) => a-b), [1,3,6,9,11,26,28,39,41,64]);
  assert.deepEqual([...SMALL].sort((a,b) => a-b), [1,3,4,6,8,9,10,11,16,17,25,26,27,28,29,32,33,39,41,43,50,51,52,53,64,65,66,67]);
  const catalog = selectAll('#all-photos figure', parseDocument(readFileSync('index.html', 'utf8')));
  const photos = JSON.parse(readFileSync('assets/listing/manifest.json', 'utf8')).photos;
  const hashes = new Set();
  for (const id of SMALL) {
    assert.ok(catalog.some(f => Number(f.attribs['data-position']) === id));
    const photo = photos.find(p => p.position === id);
    const hash = photo.derivatives[0].sha256;
    assert.ok(!hashes.has(hash), `duplicate original ${id}`);
    hashes.add(hash);
  }
});

test('six-step movement repeats with unique originals and full pool coverage', () => {
  const {EXTERIORS, SMALL, nextPhoto, movement} = selection();
  assert.equal(typeof movement, 'function', 'movement sequence must exist');
  let current = [1, 4, 39];
  const seen = current.map(id => new Set([id]));
  for (let step = 0; step < 600; step++) {
    const move = movement(step % 6, 1200, 600);
    assert.equal(move.pane, [1, 1, 0, 1, 1, 0][step % 6]);
    assert.equal(move.x, [0, 0, -800, 0, 0, 800][step % 6]);
    assert.equal(move.y, move.pane ? 300 : 0);
    const next = nextPhoto(current, move.pane);
    assert.ok(!current.includes(next), 'incoming excludes every currently visible original');
    current = move.pane ? [current[0], next, current[1]] : [next, current[1], current[2]];
    assert.equal(new Set(current).size, 3);
    current.forEach((id, pane) => seen[pane].add(id));
  }
  for (const pane of [0, 1, 2]) {
    const pool = pane === 0 ? EXTERIORS : SMALL;
    assert.deepEqual([...seen[pane]].sort((a,b) => a-b), [...pool].sort((a,b) => a-b));
  }
});

test('all six transitions share linear speed normalized to mean travel distance', () => {
  const {movement} = selection();
  assert.equal(typeof movement, 'function', 'normalized movement timing must exist');
  for (const [width, height] of [[1200, 600], [820, 900], [390, 650]]) {
    const moves = Array.from({length:6}, (_, step) => movement(step, width, height));
    const averageDistance = (4 * height / 2 + 2 * width * 2 / 3) / 6;
    for (const move of moves) {
      assert.ok(Math.abs(Math.hypot(move.x, move.y) / move.duration - averageDistance / 1000) < 1e-9);
    }
    assert.ok(Math.abs(moves.reduce((sum, move) => sum + move.duration, 0) / 6 - 1000) < 1e-9);
    if (width * 2 / 3 > height / 2) assert.ok(moves[2].duration > moves[0].duration);
  }
});
