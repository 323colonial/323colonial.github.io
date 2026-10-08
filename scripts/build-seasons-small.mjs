// Makes the 720w tier of every seasonal frame listed in assets/seasons-next/frames.json,
// beside its large frame as NN/KK-small.webp. Same recipe as the listing derivatives
// (ImageMagick, WebP quality 78), forced to the box of the photo's own small original so
// the layers register with it. Also checks the manifest against the files on disk.
//
//   node scripts/build-seasons-small.mjs [--check] [--force]
//
// --check writes nothing and fails if a frame is missing or off the timing table.
// --force remakes small frames that already exist (after a large frame is replaced).
import { spawnSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync } from 'node:fs';

const root = 'assets/seasons-next';
const check = process.argv.includes('--check'), force = process.argv.includes('--force');
const manifest = JSON.parse(readFileSync(`${root}/frames.json`, 'utf8'));

// WebP header only; enough to compare a frame with its original derivative.
function size(file) {
  const b = readFileSync(file), kind = b.toString('latin1', 12, 16);
  if (kind === 'VP8 ') return [b.readUInt16LE(26) & 0x3fff, b.readUInt16LE(28) & 0x3fff];
  if (kind === 'VP8L') { const n = b.readUInt32LE(21); return [(n & 0x3fff) + 1, ((n >> 14) & 0x3fff) + 1]; }
  if (kind === 'VP8X') return [b.readUIntLE(24, 3) + 1, b.readUIntLE(27, 3) + 1];
  throw new Error(`Not a WebP image: ${file}`);
}
const name = key => String(Math.floor(key)).padStart(2, '0') + (key % 1 ? 'h' : '');

const problems = [], warnings = [], expected = new Set(['frames.json']);
let made = 0, kept = 0;
for (const [position, photo] of Object.entries(manifest.photos)) {
  const id = position.padStart(2, '0'), own = photo.original || [];
  const [width, height] = size(`assets/listing/${id}.webp`), [sw, sh] = size(`assets/listing/${id}-small.webp`);
  for (const key of photo.keys) {
    if (!manifest.knots.includes(key) || key >= manifest.steps) problems.push(`${id}: key ${key} is not on the timing table`);
    if (own.includes(key)) continue; // Served by the untouched original; never copied here.
    const large = `${root}/${id}/${name(key)}.webp`, small = `${root}/${id}/${name(key)}-small.webp`;
    expected.add(`${id}/${name(key)}.webp`).add(`${id}/${name(key)}-small.webp`);
    if (!existsSync(large)) { problems.push(`${large} is missing`); continue; }
    const [w, h] = size(large);
    if (w !== width || h !== height) warnings.push(`${large}: ${w}x${h}, original is ${width}x${height}`);
    if (existsSync(small) && size(small).join() === [sw, sh].join() && !(force && !check)) { kept++; continue; }
    if (check) { problems.push(`${small} is missing or the wrong size`); continue; }
    const run = spawnSync('magick', [large, '-resize', `${sw}x${sh}!`, '-strip', '-quality', '78', small]);
    if (run.status !== 0) { console.error(String(run.stderr || run.error)); process.exit(1); }
    made++;
  }
}
for (const entry of readdirSync(root, { recursive: true, withFileTypes: true })) {
  if (!entry.isFile()) continue;
  const path = `${entry.parentPath}/${entry.name}`.slice(root.length + 1);
  if (!expected.has(path)) problems.push(`${root}/${path} is not in frames.json`);
}
if (!manifest.tiers?.includes('small')) problems.push('frames.json must list "tiers": ["large", "small"] for the runtime to use this tier');

console.log(`${Object.keys(manifest.photos).length} photos, ${(expected.size - 1) / 2} frames per tier: ${made} small frames made, ${kept} already current`);
warnings.forEach(warning => console.warn(`warning: ${warning}`));
problems.forEach(problem => console.error(`error: ${problem}`));
process.exit(problems.length ? 1 : 0);
