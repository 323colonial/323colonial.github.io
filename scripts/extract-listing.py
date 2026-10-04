"""Regenerate approved listing derivatives from original DOCX; requires ImageMagick.
Usage: python3 scripts/extract-listing.py '/path/to/Listing Feedback 323 Colonial Dr.docx'
Original document and legacy images are never modified. Site needs no build step.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
APPROVED = json.loads((ROOT / 'tests/fixtures/approved-listing.json').read_text())
# x, y, width, height in original embedded image pixels. Watermarks remain inside.
CROPS = {
    1: (24, 24, 1726, 1144), 2: (14, 18, 1726, 1148),
    4: (18, 12, 1726, 1144), 5: (10, 12, 1726, 1149),
    7: (34, 25, 1726, 1147),
    14: (3, 9, 1307, 960), 16: (7, 10, 1393, 958),
    23: (5, 50, 1442, 917), 27: (9, 6, 1661, 1150),
}
NOTES = {
    14: 'Trim partial countertop/cabinet at right; retain dining furniture and MLS watermark.',
    16: 'Trim partial right-edge railing; retain grill, deck and MLS watermark.',
    23: 'Trim top ceiling vent; retain full room evidence and MLS watermark.',
    27: 'Trim partial deck at right; retain paths, trees, firepit and MLS watermark.',
    12: 'Retained as supplied: already-truncated windows cannot be recovered by cropping. No invented pixels.',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    source = Path(sys.argv[1])
    if digest(source.read_bytes()) != APPROVED['document_sha256']:
        raise SystemExit('DOCX differs from approved source; review before regenerating.')
    output = ROOT / 'assets/listing'
    output.mkdir(parents=True, exist_ok=True)
    photos = []
    with ZipFile(source) as doc, tempfile.TemporaryDirectory() as tmp:
        for approved in APPROVED['photos']:
            photo = dict(approved)
            n = photo['position']
            content = doc.read(photo['source']) if photo['source'].startswith('word/') else (ROOT / photo['source']).read_bytes()
            if digest(content) != photo['source_sha256']:
                raise SystemExit(f'Source changed at position {n}; stopped.')
            original = Path(tmp) / 'source'
            original.write_bytes(content)
            photo['crop_xywh'] = CROPS.get(n)
            photo['crop_note'] = NOTES.get(n, 'Remove screenshot viewer chrome only; retain complete photograph and MLS watermark.' if n in CROPS else 'Uncropped; retain original framing and any watermark.')
            photo['provenance'] = ('Conceptual example only' if n == 31 else 'Owner photograph' if n in (6, 20, 30) else 'Prior-listing photograph' if photo['id'] == 'Previous Listing' else 'Listing photograph')
            photo['derivatives'] = []
            for suffix, width in [('', 1600), ('-small', 720)]:
                target = output / f'{n:02}{suffix}.webp'
                command = ['magick', str(original)]
                if n in CROPS:
                    x, y, w, h = CROPS[n]
                    command += ['-crop', f'{w}x{h}+{x}+{y}', '+repage']
                command += ['-resize', f'{width}x>', '-strip', '-quality', '78', str(target)]
                subprocess.run(command, check=True)
                w, h = map(int, subprocess.check_output(['magick', 'identify', '-format', '%w %h', str(target)], text=True).split())
                photo['derivatives'].append({'path': str(target.relative_to(ROOT)), 'width': w, 'height': h, 'sha256': digest(target.read_bytes())})
            photos.append(photo)
    manifest = {'document': APPROVED['document'], 'document_sha256': APPROVED['document_sha256'], 'approval': APPROVED['approval'], 'processing': 'ImageMagick; explicit crops only, no generative edits; WebP quality 78; max 1600px and 720px; no upscaling. Source document retained outside repository.', 'photos': photos}
    (output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f'Wrote {len(photos)} ordered images, two sizes each, and provenance manifest.')


if __name__ == '__main__':
    main()
