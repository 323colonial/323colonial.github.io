"""Reproduce reviewed border trims without rescaling the photograph.
Usage: python3 scripts/trim-listing-margins.py EDITED_PNG_DIRECTORY OUTPUT_DIRECTORY
Reads explicit manifest bounds only. Original PNGs and untrimmed assets stay untouched.
Requires ImageMagick; output retains existing WebP quality 78.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    source_dir, output_dir = map(Path, sys.argv[1:])
    photos = json.loads((ROOT / 'assets/listing/manifest.json').read_text())['photos']
    # Validate every input before writing any output.
    for photo in photos:
        if not any('margin_trim' in d for d in photo['derivatives']):
            continue
        source = source_dir / Path(photo['edited_source']).name
        if hashlib.sha256(source.read_bytes()).hexdigest() != photo['edited_source_sha256']:
            raise SystemExit(f'Source changed: {source}; stopped.')
    output_dir.mkdir(parents=True, exist_ok=True)
    for photo in photos:
        for d in photo['derivatives']:
            trim = d.get('margin_trim')
            if not trim:
                continue
            source = source_dir / Path(photo['edited_source']).name
            x, y, w, h = trim['xywh']
            # Resize BEFORE cropping: reproduce the existing derivative scale,
            # never enlarge a trimmed image back to its former width.
            command = ['magick', str(source), '-auto-orient', '-colorspace', 'sRGB',
                       '-resize', f"{trim['input_size'][0]}x>",
                       '-crop', f'{w}x{h}+{x}+{y}', '+repage', '-strip']
            pixels = subprocess.check_output(command + ['-depth', '8', 'rgb:-'])
            if hashlib.sha256(pixels).hexdigest() != trim['retained_rgb_sha256']:
                raise SystemExit(f'Retained pixels differ: {d["path"]}; stopped.')
            target = output_dir / Path(d['path']).name
            subprocess.run(command + ['-quality', '78', str(target)], check=True)
            if hashlib.sha256(target.read_bytes()).hexdigest() != d['sha256']:
                raise SystemExit(f'Output encoding differs: {target}; inspect ImageMagick version.')
            print(f'{target}: {w}x{h}; retained source pixels verified')


if __name__ == '__main__':
    main()
