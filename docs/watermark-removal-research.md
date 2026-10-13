# Watermark-removal decision — colonial-meb

## Owner decision

The owner confirmed permission from the relevant photo rights holder to remove marks. This is owner confirmation, not independent license review. Full framing must remain intact: no photographic cropping, resizing of master images, or nanobanana regeneration.

After reviewing the six-image LaMa trial and expanded 30-image validation, the owner accepted small corner reconstruction artifacts as good enough. That acceptance supersedes the research recommendation to require manual correction of every questionable patch. It does not establish that reconstructed pixels are original property details. The owner requested a follow-up Bead to convert website photos, then close this research task and hand off.

The website is unchanged at research closeout. Existing PRODUCT.md/DESIGN.md watermark-preservation language describes the current assets; the implementation must update that language and provenance when replacement occurs. No push or deployment is authorized.

## Selected method

Use `simple-lama-inpainting==0.1.2` locally with explicit PyTorch `mps` on the Apple M3 Max (40-core GPU, 128 GB unified memory). `PYTORCH_ENABLE_MPS_FALLBACK=0` succeeded; model parameters reported `mps:0`. CPU still performs image I/O, preparation and compositing.

- Python 3.11.11; torch 2.14.1; torchvision 0.29.1; full package freeze retained privately.
- Upstream: <https://github.com/advimman/lama>.
- Wrapper: <https://github.com/enesmsahin/simple-lama-inpainting>.
- Both repositories carry Apache-2.0 licenses. Checkpoint is the wrapper publisher's third-party TorchScript conversion, not an independently reproduced model.
- Checkpoint: <https://github.com/enesmsahin/simple-lama-inpainting/releases/download/v0.1.0/big-lama.pt>.
- Size: **205803670 bytes**. SHA256: `7ba7aa7ac37a4d41fdbbeba3a2af7ead18058552997e3a3cd1a3b2210c9e6b4c`. Publisher supplied no release-asset digest; this hash records the downloaded artifact, not independent authenticity proof.
- Setup and first six samples approved through `colonial-1i0`; owner subsequently requested GPU-first execution and expanded validation.

Feed full RGB image plus binary watermark mask to LaMa. Remove only model-added padding, then composite predicted pixels inside the mask onto the original image. Assert original dimensions and exact decoded equality outside the mask before delivery encoding. Lossy WebP re-encoding may change decoded pixels outside the mask; distinguish that codec effect from generated edits and measure it rather than claiming byte equality after lossy encoding.

Do not use one fixed mask for every asset: watermark size/shape varies and some images are clean. Preserve clean assets unchanged. Do not remove unrelated labels, approximate-boundary information or the conceptual-plan disclosure.

## Evidence

| Trial | Result |
|---|---|
| Photocraft, 2 images | Grass plausible; sofa introduced a conspicuous false seam. |
| LaMa, 6 images | All integrity checks passed; sofa, grass and decking plausible. First inference 2.40 s; later 0.35–0.76 s. Snow patches differed between frames. |
| LaMa, 30 images | 28 new sources and 2 prior snow controls, with expanded masks. 30/30 source hashes, dimensions, outside-mask equality and output serialization checks passed. No visible MLS mark remained in inspected corners. |
| Expanded performance | 0.280–0.833 s per inference; median 0.353 s; total 12.364 s. Excludes model loading and file I/O. |
| Expanded visual review | 14 plausible candidates; 16 flagged for closer review (2 originals and 14 snow frames). Subjective hard-case triage, not a statistical success rate. Owner subsequently accepted this quality threshold. |
| Seasonal review | Five adjacent-frame pairs sampled at 0/25/50/75/100% blends. Porch relatively coherent; snow sometimes smooth or inconsistent. No live animation/iPad certification. |

Examples of residual issues: softened chair/deck geometry in original 16; inferred instrument/window detail in original 59; a conspicuous brown/gray reconstructed tree/ground patch in photo 66's snow frame. These are accepted small-corner artifacts, not proof of hidden detail. Integrity checks and complete watermark coverage remain required.

Alternatives: authorized clean originals preserve real detail but the owner rejected the delay; licensing/reshooting costs remain unknown. GIMP provides manual correction; installed FFmpeg interpolation is not the selected method. Hosted generative services add uploads/costs. Local LaMa has no per-image API charge. No paid service or photo upload was used.

## Complete conversion scope

Current local website catalog: **65 stable photo IDs**, of which **57** visibly carry MLS marks. Unmarked original IDs: **5, 6, 7, 20, 25, 30, 31, 73** (31 is conceptual).

`assets/seasons-next/frames.json` describes **54 photo IDs and 405 non-original full-size seasonal frames**. Original keys reuse listing assets. All 405 were exported conservatively; not all are watermarked. For example, photo 5's seasonal key 0 has a mark despite its clean listing original. Inspect frames individually rather than inferring watermark presence from the base image.

Implementation must cover affected full-size listing and seasonal images, rebuild their small delivery variants with ordinary image processing, and rebuild affected GIF previews. The owner explicitly excluded GIF frames from manual editing because the GIF can be regenerated. No new seasonal image synthesis is needed. Inventory current runtime, HTML, preview/build references before replacement; exclude retired `assets/seasons/` and pruned/unpublished files unless current references prove otherwise.

Preserve IDs, filenames/URLs where practical, dimensions, approved captions, animation timing, and no-JS/reduced-motion/save-data/print fallbacks. Retain original assets and source hashes separately before replacement. Record masks, method, checkpoint hash and derivative hashes; update tests that freeze source/output hashes intentionally, not by weakening provenance checks.

## Exact local handoff artifacts

These private artifacts are not committed; check existence before reuse. Do not recreate or overwrite any owner-edited export blindly.

- `.pi/research/colonial-meb-lama/`: `venv/`, `big-lama.pt`, `checkpoint-provenance.json`, `requirements-lock.txt`, `gpu-trial.log`, `validate30.py`, `expanded-inputs.json`, `expanded-gpu.log`.
- `.pi/research/colonial-meb-photocraft/`: two initial fill results, logs and verification hashes.
- `~/Downloads/lama-trial/`: six before/after/mask sets, `comparison.png`, `results.json`, `README.txt`.
- `~/Downloads/lama-validation-30/`: 30 before/after/mask sets, `comparison-1.png` through `comparison-3.png`, `seasonal-crossfade-phases.png`, `results.json`, `visual-review.json`, `README.txt`.
- `~/Downloads/all-website-photos/`: flat **462 PNGs**, named `photo-NN-original.png` (57) and `photo-NN-season-KK.png` (405). `h` indicates a half-step key, not a month. Every copy was byte-verified during flattening; later user edits are possible.
- `~/Downloads/all-website-photos-source-export/`: preserved original export tree, `original-webp/`, `seasonal/`, initial and seasonal manifests, and `flat-export-manifest.json` mapping flat names to source paths/hashes. No files deleted during flattening.

Implementation follow-up: `colonial-6nu` — replace website watermarked photos and seasonal frames with accepted LaMa derivatives, including derived sizes and GIF previews. This is the requested handoff target.

Separate issue `colonial-tyl` tracks the iPad seasonal animation halt. Do not fold that unrelated investigation into watermark conversion.
