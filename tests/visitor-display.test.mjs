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
  vm.runInContext(source.replace(marker, 'globalThis.selection = { EXTERIORS, SMALL, nextPhoto }; return;\n' + marker), context);
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

test('initial, repeated and wraparound changes stay unique and reach every eligible photo in each pane', () => {
  const {EXTERIORS, SMALL, nextPhoto} = selection();
  let current = [1, 4, 39];
  const seen = [new Set(), new Set(), new Set()];
  for (let step = 0; step < 600; step++) {
    const pane = step % 3;
    const next = nextPhoto(current, pane);
    assert.ok(!current.includes(next), 'incoming excludes outgoing and both other panes');
    assert.ok((pane === 0 ? EXTERIORS : SMALL).includes(next));
    current[pane] = next;
    assert.equal(new Set(current).size, 3);
    seen[pane].add(next);
  }
  for (const pane of [0, 1, 2]) {
    const pool = pane === 0 ? EXTERIORS : SMALL;
    assert.deepEqual([...seen[pane]].sort((a,b) => a-b), [...pool].sort((a,b) => a-b));
  }
});
