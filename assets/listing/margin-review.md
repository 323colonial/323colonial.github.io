# Photo margin review — colonial-286

Reviewed all 33 buyer-listing images (32 photographs and one concept plan), both derivative sizes, and all 36 legacy house photographs/simulations in `images/` and `assets/plates/`. Inspected contact sheets, enlarged candidate corners and edge-pixel profiles. Legacy images, source PNGs, source DOCX, captions and image URLs remain unchanged.

## Confirmed margins

White outer margins on the positions below; position 28 has a dark charcoal margin. Bounds are conservative: retain uncertain transition pixels and thin inner outlines rather than risk cutting photographic content. No automatic blanket trim.

Paths are `assets/listing/NN.webp` and `assets/listing/NN-small.webp`. Each rectangle is **x, y, width, height** in that derivative's pre-trim pixels. Exact original dimensions, before/after file hashes and retained pre-encoding RGB hashes are recorded in `manifest.json` → `derivatives[].margin_trim`.

| Position | Full-size rectangle | Small rectangle |
| --- | --- | --- |
| 10 | 4, 9, 1590, 1051 | 1, 4, 717, 473 |
| 11 | 8, 7, 1444, 962 | 3, 3, 712, 474 |
| 12 | 8, 10, 1444, 960 | 3, 4, 714, 475 |
| 13 | 0, 10, 1591, 1054 | 0, 4, 716, 475 |
| 15 | 8, 9, 1136, 756 | 4, 5, 710, 473 |
| 17 | 3, 5, 1443, 960 | 1, 2, 716, 476 |
| 18 | 3, 7, 1443, 961 | 1, 3, 716, 477 |
| 19 | 6, 6, 1444, 963 | 2, 2, 717, 478 |
| 21 | 6, 12, 1444, 956 | 2, 5, 714, 473 |
| 22 | 3, 10, 1445, 962 | 1, 4, 718, 479 |
| 24 | 6, 12, 1444, 964 | 2, 5, 716, 479 |
| 26 | 4, 6, 1444, 958 | 1, 2, 717, 476 |
| 28 | 9, 8, 1330, 882 | 4, 4, 713, 472 |
| 29 | 8, 9, 1444, 960 | 3, 4, 715, 475 |
| 32 | 4, 9, 1444, 814 | 1, 4, 716, 403 |
| 33 | 4, 5, 1444, 814 | 1, 2, 717, 404 |

## Unchanged and ambiguous edges

- Positions **1–9, 14, 16, 20, 23, 25, 27, 30, 31**: both files unchanged. Pale sky in 8, snow in 9, and hot-tub edge in 6 are photographic content, not solid margins. Position 31 is a drawing; its white paper and disclaimers remain intact.
- **Position 13 left edge**: nonuniform image-like detail reaches into the apparent white strip. Left edge remains untrimmed in both sizes; requires owner review before any further crop.
- Compressed/soft transitions and inner gray/dark outlines are retained on other candidates. Small-image offsets round down independently on each axis to keep all uncertain edge pixels.
- All 36 legacy house images have no confirmed solid outer margins. Existing watermarks remain part of their photographs. Unused placeholder, product illustrations and architectural drawings are not house-photo candidates and remain untouched.

## Reproduction and checks

Inputs are the hash-verified owner-edited PNGs, not decoded WebP files. Recreate the existing full/small image scale **before** cropping, then encode once at the existing WebP quality 78. No scaling after cropping, recoloring, sharpening, generative changes or edits to originals. Encoding is lossy; decoded WebP pixels are not claimed bit-identical. Before encoding, an independent RGB row-slice comparison verified every retained pixel against the corresponding pre-trim image. All outputs remain under the existing 500 KB limit.

```sh
python3 tests/test_listing.py
python3 scripts/trim-listing-margins.py /path/to/edited-listing-photos /tmp/reproduced-margin-trims
```

The reproduction command checks source hashes before any writes, verifies retained RGB hashes, and requires exact output hashes. Use a separate output directory to verify without touching the site. It intentionally regenerates only the 32 affected assets. The historical `extract-listing.py` reads the original DOCX, not the current edited PNGs, and must not be used to overwrite these reviewed assets.

`index.html` and `gallery.html` retain all image references; intrinsic dimensions and `srcset` width descriptors now match the cropped files. Regression checks freeze reviewed crop bounds and validate those HTML dimensions alongside existing captions, provenance, output hashes and legacy-preservation checks.
