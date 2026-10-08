"""Check a browser viewport PNG against crossfade-pixels.html's paint() JSON.

Usage: python3 tests/check_crossfade_pixels.py SCREENSHOT.png PROBES.json
Requires existing ImageMagick tooling, not a new Python/browser dependency.
"""
import json
import subprocess
import sys


def check_pixels(screenshot, manifest):
    width, height = map(int, subprocess.check_output(
        ['magick', 'identify', '-format', '%w %h', screenshot], text=True).split())
    vw, vh = manifest['viewport']
    assert abs(width / vw - height / vh) < .01, 'Screenshot must be an uncropped viewport capture'
    pixels = subprocess.check_output(['magick', screenshot, '-alpha', 'off', '-depth', '8', 'rgb:-'])
    def pixel(point):
        x, y = round(point['x'] * width / vw), round(point['y'] * height / vh)
        assert 0 <= x < width and 0 <= y < height, f'Probe outside screenshot: {point}'
        offset = (y * width + x) * 3
        return list(pixels[offset:offset + 3])

    failures = []
    assert manifest['probes'], 'No pixel probes'
    for probe in manifest['probes']:
        actual, expected = pixel(probe), pixel(probe['reference'])
        if any(abs(a - b) > 3 for a, b in zip(actual, expected)):
            failures.append(f"{probe['name']}: expected {expected} (CSS {probe['rgb']}), got {actual}")
    assert not failures, manifest['label'] + '\n' + '\n'.join(failures)
    print(f"PASS: {manifest['label']} ({len(manifest['probes'])} screen pixels)")


if __name__ == '__main__':
    with open(sys.argv[2]) as source:
        check_pixels(sys.argv[1], json.load(source))
