#!/usr/bin/env python3
"""Rebuild existing 24-second email/OG loops from cleaned hero masters, without inference.

Run in the existing LaMa venv after remove-watermarks.py; writes private stage only.
Keep original 120 frames, 200ms delay, infinite loop, 480x318 and 300x199 geometry.
"""
import hashlib
import json
from pathlib import Path
import subprocess

if not __debug__:
    raise SystemExit('Optimized Python disables required integrity checks')

from PIL import Image

WORK = Path('.pi/artifacts/colonial-6nu')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report = json.loads((WORK / 'conversion.json').read_text())
    by_path = {r['path']: r for r in report['images']}
    sources = ['assets/listing/01.webp'] + [f'assets/seasons-next/01/{k:02}.webp' for k in range(1, 12)]
    frames = WORK / 'gif-frames'
    frames.mkdir(exist_ok=False)
    previews = []
    for suffix, size in [('', (480, 318)), ('-small', (300, 199))]:
        name = f'assets/email/323-colonial-hero{suffix}.gif'
        original = Image.open(WORK / 'originals' / name)
        assert original.size == size and original.n_frames == 120 and original.info['loop'] == 0
        for i in range(120):
            original.seek(i)
            assert original.info['duration'] == 200
        anchors = []
        folder = frames / ('small' if suffix else 'large')
        folder.mkdir()
        for k, source in enumerate(sources):
            master = WORK / 'masters' / Path(source).with_suffix('.png')
            assert digest(master) == by_path[source]['master_sha256']
            anchor = folder / f'anchor-{k:02}.png'
            subprocess.run(['magick', str(master), '-resize', f'{size[0]}x{size[1]}!', str(anchor)], check=True)
            anchors.append(Image.open(anchor).convert('RGB'))
        for i in range(120):
            k, fraction = divmod(i, 10)
            frame = Image.blend(anchors[k], anchors[(k + 1) % 12], fraction / 10)
            path = folder / f'frame-{i:03}.png'
            frame.save(path)
        output = WORK / 'stage' / name
        output.parent.mkdir(parents=True, exist_ok=True)
        assert not output.exists()
        colors = 96 if suffix else 128
        subprocess.run(['ffmpeg', '-v', 'error', '-framerate', '5', '-i', str(folder / 'frame-%03d.png'),
                        '-filter_complex', f'[0:v]split[a][b];[a]palettegen=max_colors={colors}[p];[b][p]paletteuse=dither=bayer:bayer_scale=3',
                        '-loop', '0', str(output)], check=True)
        check = Image.open(output)
        assert check.size == size and check.n_frames == 120 and check.info['loop'] == 0
        for i in range(120):
            check.seek(i)
            assert check.info['duration'] == 200
        previews.append(dict(path=name, source_sha256=digest(WORK / 'originals' / name),
                             output_sha256=digest(output), size=list(size), frames=120,
                             duration_ms=24000, loop=0, sources=sources,
                             recipe=f'12 integer seasonal anchors; 10 linear blends per segment; ImageMagick resize, FFmpeg palettegen max_colors={colors}, paletteuse dither=bayer:bayer_scale=3; no generated imagery',
                             runner_sha256=digest(Path(__file__))))
        print(name, output.stat().st_size, 'bytes; geometry/timing PASS')
    report['previews'] = previews
    (WORK / 'conversion.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
