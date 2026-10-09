# Private authoring tools

These tools are not in the buyer publication allowlist. Running generation APIs or a full-scene bake requires separate approval; offline tests do not grant it.

## Seasonal pilot

`scripts/seasons/pilot.py` reads originals from the repository's `assets/listing/`. Scratch defaults to ignored `.pi/artifacts/seasons/`, not the source directory. Set `COLONIAL_SEASONS_WORK` to an existing private workspace to reuse its `review/`, `hero/` and `refs/` inputs. External scratch directories or paths under `.pi/artifacts/` are accepted; other repository paths are rejected. Nothing is moved or copied automatically. Import and `python3 scripts/seasons/pilot.py sun` do not create outputs or call generation APIs. Pilot generation tags are single directory names, not paths.

`hero_half.py`, `hero_relight.py` and `tween.py` use that scratch root but locate `align.py` beside their source. Other historical seasonal recipes still use their existing working-directory-relative inputs; this change does not migrate those workspaces.

Alignment parallelism belongs to frame-level callers (for example, ten workers in `batch.py`). Each `align.py` process measures patches serially, including the residual pass. One ten-frame batch therefore has at most ten ImageMagick child processes at a time, rather than up to eighty from nested patch pools. Independent simultaneous invocations are not globally throttled; ImageMagick may also use internal threads. Standalone alignment trades speed for this resource bound. Fit rejection and image quality remain unchanged.

Offline checks, with installed ImageMagick:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_season_tools.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_export_wb.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_lighting_reference.py
```

## Walkthrough

`build.py` keeps page metadata for export/encode, but creates floating-point atlas targets and active `BAKE` nodes only with `--bake`. Export without baking still reports every page and rejects stale encoded lighting. Source changes remain part of the bake fingerprint; older bakes must be regenerated before encoding, not restamped.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_walkthrough_tools.py
blender -b --python-exit-code 1 -P tests/test_walkthrough_blender.py
```

The Blender test uses temporary synthetic inputs and a tiny one-page bake; it does not validate full-scene lighting quality or overwrite existing assets.
