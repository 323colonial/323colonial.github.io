#!/usr/bin/env python3
"""Regenerate static photo figures only; --check rejects drift without writing."""
import argparse
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = [n for n in range(1, 74) if n not in {40, 62, 63, 68, 69, 70, 71, 72}]
STORIES = [
    [39, 34, 49, 11, 54],
    [2, 42, 44, 45, 46, 12, 59, 13, 5, 47, 48, 35, 14],
    [4, 50, 51, 17, 52, 53, 16, 43, 6, 29, 10, 67],
    [18, 37, 7, 55, 56, 36, 23, 60, 38, 57, 21, 58, 61, 22],
    [25, 65, 26, 30, 73], [3, 27], [66, 28, 41, 64],
]
SIZES = {
    'hero': '100vw',
    'story': '(max-width: 800px) calc(100vw - 40px), calc((100vw - 144px) * .55)',
    'catalog': '(max-width: 700px) calc(100vw - 66px), (max-width: 1000px) calc((100vw - 114px) / 2), (max-width: 1132px) calc((100vw - 138px) / 3), 331px',
    'gallery': '(max-width: 700px) calc(100vw - 32px), (max-width: 1000px) calc((100vw - 88px) / 2), (max-width: 1264px) calc((100vw - 112px) / 3), 384px',
}


def figure(photo, kind, ordinal):
    n = photo['position']
    large, small = photo['derivatives']
    for derivative, suffix in ((large, ''), (small, '-small')):
        if derivative['path'] != f'assets/listing/{n:02d}{suffix}.webp' or any(
                type(derivative[k]) is not int or derivative[k] <= 0 for k in ('width', 'height')):
            raise ValueError(f'Invalid derivative for photo {n}')
    caption = escape(photo['caption'])
    note = 'Conceptual basement plan — not existing finished space.' if n == 31 else ''
    alt = 'Conceptual basement renovation plan; not existing finished space.' if n == 31 else caption
    grid = kind in ('catalog', 'gallery')
    identity = f' id="photo-{n}"' if grid else ''
    link = (f'href="{large["path"]}" data-gallery-image' if grid else
            f'href="gallery.html#photo-{n}" data-photo="{n}"')
    if kind == 'hero':
        link = 'id="seasonal-hero" ' + link
    image = large if kind == 'hero' else small
    loading = 'fetchpriority="high"' if kind == 'hero' or (kind == 'gallery' and ordinal == 1) else 'loading="lazy"'
    if kind != 'hero' and not (grid and ordinal == 1):
        loading += ' decoding="async"'
    number = f'<span class="photo-number">{ordinal} / {len(CATALOG)}</span>' if grid else ''
    return (f'<figure class="media-record"{identity} data-position="{n}"><a {link} '
            f'aria-label="Enlarge photo {n}: {caption}{" " + note if note else ""}">'
            f'<img src="{image["path"]}" srcset="{small["path"]} {small["width"]}w, {large["path"]} {large["width"]}w" '
            f'sizes="{SIZES[kind]}" width="{image["width"]}" height="{image["height"]}" alt="{alt}" {loading}></a>'
            f'<figcaption>{number}<span class="caption-text">{caption}</span>'
            + (f'<span class="photo-note">{note}</span>' if note else '') + '</figcaption></figure>')


def render_page(text, name, photos):
    by_id = {p['position']: p for p in photos}
    if len(by_id) != len(photos):
        raise ValueError('Duplicate photo positions')
    regions = [('gallery', 'gallery', CATALOG)] if name == 'gallery.html' else [
        ('hero', 'hero', [1]),
        *[(f'story-{i}', 'story', ids) for i, ids in enumerate(STORIES, 1)],
        ('catalog', 'catalog', CATALOG),
    ]
    replacements = []
    for region, kind, ids in regions:
        start, end = f'<!-- photos:{region} -->', f'<!-- /photos:{region} -->'
        if text.count(start) != 1 or text.count(end) != 1:
            raise ValueError(f'Missing or duplicate photo markers: {region}')
        left, right = text.index(start), text.index(end) + len(end)
        if left + len(start) > right - len(end):
            raise ValueError(f'Reversed photo markers: {region}')
        separator = '\n' if kind in ('gallery', 'catalog') or region == 'story-6' else ''
        figures = separator.join(figure(by_id[n], kind, i) for i, n in enumerate(ids, 1))
        replacements.append((left, right, start + figures + end))
    replacements.sort()
    if any(a[1] > b[0] for a, b in zip(replacements, replacements[1:])):
        raise ValueError('Overlapping photo regions')
    for left, right, content in reversed(replacements):
        text = text[:left] + content + text[right:]
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    photos = json.loads((args.root / 'assets/listing/manifest.json').read_text())['photos']
    # Validate both outputs before writing either page.
    outputs = [(args.root / name, render_page((args.root / name).read_text(), name, photos))
               for name in ('index.html', 'gallery.html')]
    stale = [path for path, text in outputs if path.read_text() != text]
    if args.check:
        if stale:
            parser.exit(1, 'Stale photo markup: ' + ', '.join(p.name for p in stale) + '\n')
    else:
        for path, text in outputs:
            if path in stale:
                path.write_text(text)


if __name__ == '__main__':
    main()
