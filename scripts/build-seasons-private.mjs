// Private only: snapshots seasonal frames into a git-ignored folder and writes
// the delivery manifest the seasonal runtime reads. Nothing here is published;
// scripts/publish-files.txt never lists the output.
//
//   node scripts/build-seasons-private.mjs <frames-dir> [--out <dir>] [--no-small]
//
// <frames-dir> holds one folder per catalog position (two digits) with frames
// named by step on the 12-step year: 00..11, half steps as 04h..09h.
// Folders with any other name (01r, 26x, ...) are trials and are ignored.
import { spawnSync } from 'node:child_process';
import { copyFileSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';

// Owner timing table (colonial-66v): 18 hero frames, 2 seconds each, 36 second year.
// Knots are positions on the 12-step year; durations are seconds between neighbors.
const STEPS = 12;
const KNOTS = [0, 1, 2, 3, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 11, 12];
const DURATIONS = KNOTS.slice(1).map(() => 2);
const ANCHORS = { 'late-summer': 0, fall: 3, winter: 6, spring: 9 };

const args = process.argv.slice(2);
const flag = name => args.includes(name);
const option = name => args.includes(name) ? args[args.indexOf(name) + 1] : undefined;
const source = args[0] && !args[0].startsWith('--') ? resolve(args[0]) : null;
const out = resolve(option('--out') || '.pi/artifacts/seasons-private');
if (!source || !existsSync(source)) {
  console.error('Usage: node scripts/build-seasons-private.mjs <frames-dir> [--out <dir>] [--no-small]');
  process.exit(1);
}

// WebP header only; enough to compare a frame with its original derivative.
function size(file) {
  const b = readFileSync(file), kind = b.toString('latin1', 12, 16);
  if (kind === 'VP8 ') return [b.readUInt16LE(26) & 0x3fff, b.readUInt16LE(28) & 0x3fff];
  if (kind === 'VP8L') { const n = b.readUInt32LE(21); return [(n & 0x3fff) + 1, ((n >> 14) & 0x3fff) + 1]; }
  if (kind === 'VP8X') return [b.readUIntLE(24, 3) + 1, b.readUIntLE(27, 3) + 1];
  throw new Error(`Not a WebP image: ${file}`);
}
const name = key => String(Math.floor(key)).padStart(2, '0') + (key % 1 ? 'h' : '');

// Only replace a folder this script wrote; never delete an arbitrary --out.
if (existsSync(out)) {
  if (readdirSync(out).length && !existsSync(join(out, 'delivery.json'))) {
    console.error(`${out} is not a previous build of this script; refusing to replace it.`);
    process.exit(1);
  }
  rmSync(out, { recursive: true });
}
mkdirSync(out, { recursive: true });

const magick = !flag('--no-small') && spawnSync('magick', ['-version']).status === 0;
const photos = {}, warnings = [];
let frames = 0, bytes = 0;

for (const id of readdirSync(source).filter(entry => /^\d\d$/.test(entry)).sort()) {
  const original = `assets/listing/${id}.webp`, small = `assets/listing/${id}-small.webp`;
  if (!existsSync(original)) { warnings.push(`${id}: no original ${original}; skipped`); continue; }
  const keys = readdirSync(join(source, id)).map(file => /^(\d\d)(h?)\.webp$/.exec(file))
    .filter(Boolean).map(match => Number(match[1]) + (match[2] ? .5 : 0)).sort((a, b) => a - b);
  const off = keys.filter(key => !KNOTS.includes(key) || key >= STEPS);
  if (!keys.length || off.length) { warnings.push(`${id}: keys ${off.join(', ') || 'missing'} are not on the timing table; skipped`); continue; }
  const lacking = Object.values(ANCHORS).filter(step => keys.length > 1 && !keys.includes(step));
  if (lacking.length) { warnings.push(`${id}: no frame at season step ${lacking.join(', ')}; skipped`); continue; }
  const [width, height] = size(original);
  const own = [];
  for (const key of keys) {
    const file = join(source, id, `${name(key)}.webp`);
    // Step 0 served by the untouched original is never copied into the seasonal tree.
    if (key === 0 && readFileSync(file).equals(readFileSync(original))) { own.push(0); continue; }
    const [w, h] = size(file);
    if (w !== width || h !== height) warnings.push(`${id}/${name(key)}: ${w}x${h}, original is ${width}x${height}`);
    mkdirSync(join(out, id), { recursive: true });
    const target = join(out, id, `${name(key)}.webp`);
    copyFileSync(file, target);
    frames++; bytes += readFileSync(target).length;
    if (magick) {
      // Same recipe as the listing derivatives, forced to the original small frame's box.
      const [sw, sh] = size(small);
      const made = spawnSync('magick', [file, '-resize', `${sw}x${sh}!`, '-strip', '-quality', '78', join(out, id, `${name(key)}-small.webp`)]);
      if (made.status !== 0) { console.error(String(made.stderr)); process.exit(1); }
    }
  }
  photos[Number(id)] = own.length ? { keys, original: own } : { keys };
}

writeFileSync(join(out, 'delivery.json'), JSON.stringify({
  version: 2, steps: STEPS, knots: KNOTS, durations: DURATIONS, anchors: ANCHORS,
  tiers: magick ? ['large', 'small'] : ['large'], photos,
}, null, 1) + '\n');
// Kept beside the manifest, not in it: the browser needs none of this.
writeFileSync(join(out, 'build-report.json'), JSON.stringify({ source, frames, bytes, warnings }, null, 1) + '\n');

const count = Object.values(photos).reduce((groups, photo) => {
  const n = photo.keys.length; groups[n] = (groups[n] || 0) + 1; return groups;
}, {});
console.log(`${Object.keys(photos).length} photos, ${frames} generated frames, ${(bytes / 1e6).toFixed(1)} MB large tier${magick ? ', small tier made with ImageMagick' : ', no small tier'}`);
console.log('Photos by key count:', JSON.stringify(count));
warnings.forEach(warning => console.warn(`warning: ${warning}`));
