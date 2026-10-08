# colonial-wtm: synchronized seasonal hero and narrative architecture

Evaluation only. Nothing here is implemented, prototyped, generated or published. Status: draft for owner review, 7 October 2026. Revised the same day after owner feedback: keep the hero's timing, and cut generation cost.

## Recommendation

Run one shared annual clock for the hero and the scroll-sequenced narrative photos. Each participating photo shows a two-frame window of its annual sequence, stacked above its untouched original `<img>`. The clock advances one dissolve at a time and only crosses a frame boundary when every visible in-scope photo has the next frame decoded. Galleries, the viewer, previews and full-size links keep reading `assets/listing/NN.webp` and never see a seasonal file.

Timing matches the approved hero, at the owner's direction: a 24 second year on a 12-step grid, 2 seconds per step. This supersedes the ticket's working figure of about 24 frames. An earlier draft of this document proposed a 60 second year, and that is withdrawn.

Photos do not all need 12 generated frames. Each photo supplies key frames at whichever grid steps it needs, and the runtime dissolves between neighboring keys. An exterior supplies all 12. An interior with window views can supply the 4 season anchors and dissolve over 6 seconds between them. A windowless interior supplies 1. That is the main control on both generation cost and download size.

I do not recommend extending the current hero technique. `seasonal-hero.js` stacks every frame as its own layer with its own infinite animation and loads all of them at once. That is fine for one photo. Across 67 photos it is the wrong shape, and the numbers below show why.

## Revision from the colonial-66v pilot, 7 October 2026

The pilot changed three things in this design. The sections below still describe the 12-step, 24 second version and need a full pass before this ticket closes.

1. **Timing is a table, not one number.** The owner chose 18 hero frames at 2 seconds each, a 36 second year. Six of those frames sit at half steps 4.5 to 9.5, so the delivery manifest carries the list of key positions on the 12-step year and the seconds spent between each pair. Every photo follows that one table, which keeps them in sync. A photo with fewer keys dissolves across the same stretched time.
2. **Keys per photo.** Special house exteriors (1, 11, 26, 28, 39, 41) get 18. Other ground-level exteriors and porch views get 12. Large-window rooms get 6, at steps 0, 3, 5, 6, 8, 9. Small-window rooms get 4. Windowless rooms keep the original. Keys may sit at half steps, so `keys` holds numbers such as 4.5 and files are named `04h`.
3. **Catalog.** The owner intends to remove photos 40, 62, 63 and 68 to 72 from the gallery (ticket colonial-rp8). Budgets and counts here assume 73 photos and will shrink.

Winter is now full night and the steps either side are dusk and pre-dawn, so readiness and transfer budgets are unchanged in kind but frame bytes for dark frames should be re-measured.

## What exists today

Measured from the working tree on 7 October 2026.

| Item | Value |
| --- | --- |
| Catalog | 73 stable positions, `assets/listing/NN.webp` and `NN-small.webp` |
| Hero | position 1, 1280x848, 366 KB large, 126 KB small |
| Narrative | 66 positions in 7 stories of 7, 13, 13, 14, 7, 4 and 8 photos |
| Gallery only | 15, 19, 20, 24, 31, 32. Position 31 is the conceptual plan, not a photograph |
| Narrative originals, small tier | 720w, 5.2 MB total, median 71 KB, max 153 KB |
| Narrative originals, large tier | 1146w to 1600w, 16.2 MB total, median 230 KB, max 478 KB |
| Current seasonal hero | 11 generated 1280x848 WebPs, 3.78 MB, mean 343 KB, all fetched once the hero is visible |
| Current hero decoded memory | 12 frames x 4.34 MB = 52 MB |
| Current hero layers | 12 stacked images, each with an infinite opacity animation, `plus-lighter` blending |

Large-tier widths vary by photo: 32 at 1440w, 21 at 1280w, 7 at 1200w, 5 at 1600w, 1 at 1146w. The seasonal contract has to follow each photo's own dimensions, not one global size.

`graphify-out/graph.json` does not exist, so everything here was verified against source.

Relevant behavior in `listing.js`: each sequenced story keeps at most two photos with non-zero opacity. It sets `--photo-opacity` on the photo's `<a>`, sets `hidden` on the figure at zero opacity, reads the first `<img>` in each figure for geometry and preloading, and skips sequencing under reduced motion, under 300px of available height, or when desktop copy is taller than the space.

## Alternatives considered

**Extend the current all-layers hero technique.** Rejected. Each 12-key photo holds 52 MB decoded and 12 animating layers, and fetches every frame up front, about 3.8 MB for the hero. Two such photos on screen during a scroll blend double that. On a 1440px DPR 2 screen each hero layer is roughly a 22 MB texture, so 12 layers approach 260 MB of GPU memory as an upper estimate. Each image also runs its own clock, which is the drift the ticket rules out.

**One video per photo.** Rejected for now. Bytes would likely be several times smaller, but frame-accurate sync across several videos is unreliable, iOS limits concurrent decoders, and "hold every visible photo at the same coherent frame until a slow one is ready" becomes guesswork. Keep it as the contingency if the transfer thresholds below cannot be met with stills.

**Canvas or WebGL compositing.** Rejected. It gives exact blending in one layer per photo, but it reimplements `srcset`, `object-fit`, link semantics and print fallback that the browser already does. No demonstrated need.

**Animated WebP or AVIF.** Rejected. No pause, no seek, no shared phase.

**CSS-only keyframes.** Rejected. CSS cannot wait for an image to decode before advancing.

**One video per photo, measured.** I encoded the 12 existing hero frames as a 24 second looping video with the same 2 second linear dissolves, using ffmpeg on the stills we already have. No AI video tool is involved and any aspect ratio works. The result is larger and softer than the stills:

| Delivery of the 12-scene hero at 1280x848 | Size |
| --- | --- |
| 12 WebP stills, as published today | 4.1 MB |
| H.264 video, crf 28 | 6.2 MB |
| H.264 video, crf 24 | 10.1 MB |
| VP9 video, crf 34 | 6.6 MB |
| AV1 video, crf 34 | 5.4 MB |

At 720px the videos are 2.0 to 3.3 MB against about 1.5 MB of stills. The reason shows up in a second test. Encoding only the 12 key frames as a 12-frame video came out larger with motion prediction on, 3.7 MB, than with every frame coded independently, 2.9 MB. The frames look alike to a person, but each was generated separately, so leaves, grass and snow texture differ in every pixel and a codec finds nothing to reuse. A dissolve also changes every pixel on every video frame, which is the worst case for video.

**Animated GIF.** Rejected. The existing email GIF of this hero is 5.7 MB at only 480x318 and 128 colors.

**One large sheet holding every frame.** Rejected. JPEG, PNG and WebP compress each region independently, so tiles that resemble each other save nothing. The whole sheet must download before the first frame shows, and it decodes to about 52 MB at once for 12 hero frames.

Stills dissolved by the browser are the smallest delivery for this imagery. The savings have to come from fewer generated frames and fewer animated photos.

## Rendering model

The original `<img>` stays first inside its `<a>`, in flow, opaque and unmodified. It sizes the box. The runtime appends one `.season-stack` element after it, absolutely positioned over the same box, holding two images:

- lower layer: frame k+1 at opacity 1
- upper layer: frame k, opacity animating linearly from 1 to 0

With an opaque lower layer, ordinary source-over compositing gives exactly `(1-s)·A + s·B`. No `plus-lighter` is needed, so that feature gate goes away. The stack is opaque wherever the photo is, and it sits inside the `<a>` that already carries `--photo-opacity`. The browser composites the seasonal pair first and applies scroll opacity to the result as a group. Scroll blending therefore behaves exactly as it does today.

The mistake to avoid is giving both seasonal layers partial opacity, `1-s` and `s`. Coverage then drops to 75% at the midpoint and the story background shows through. On top of the existing scroll blend that reads as a pulse of lightening or darkening on every dissolve.

At a frame boundary the upper layer is at opacity 0 and the lower layer shows frame k+1 alone. The runtime inserts decoded frame k+2 beneath it and removes the old upper layer. A new frame only ever enters underneath a fully opaque one, so a late paint cannot show as a blank.

A photo joins by fading its stack from 0 to 1 over 600 ms above the original. It leaves by removing the stack. Because the original is never altered, no-JS, print and reduced motion need only `display: none` on `.season-stack`.

Geometry holds only if every seasonal frame has exactly the pixel dimensions of the original derivative at the same tier. The layers use the same `object-fit: contain` box, so equal dimensions mean no shift and unchanged transparent letterboxing.

## Shared clock

One logical clock holds the grid step k from 0 to 11 and the time elapsed within that step. Phase is `(k + elapsed/2s) / 12`.

- Every upper layer in a dissolve gets a finite Web Animation with the same `startTime` on `document.timeline`. Photos that join mid-dissolve use that same start time. Sync comes from sharing one number, not from correcting drift afterwards.
- The compositor interpolates. No per-frame JavaScript runs for seasons, so scroll handling in `listing.js` is not competing with it.
- Animations are finite and one dissolve long. This also sidesteps the screenshot tooling problem recorded in colonial-29s, where capture reset infinite animations.
- A photo with sparse keys runs one long dissolve between its neighboring keys, with opacity derived from the same shared clock. A photo with one key has no dissolve.
- Year order is chronological from the originals' season: late summer at phase 0, fall at 0.25, winter at 0.5, spring at 0.75. The existing twelve hero scenes are this grid.
- Initial phase is 0. For exteriors frame 0 is the original file, so the first coherent frame costs nothing.
- The dissolve curve is linear with no holds. A pure frame exists only for an instant.

### Duration

24 seconds per year, 2 seconds per grid step, as the approved hero runs today. The cost of that choice is download rate, covered under budgets. Sparse keys are how interiors stay cheap at this speed.

## Readiness barrier

Participating set: the hero while it intersects the viewport, plus sequenced narrative photos with non-zero scroll opacity. The lookahead set is the next photo in the scroll direction for a story near the viewport, the same photo `listing.js` already preloads.

1. At the start of each grid step the runtime requests, for the participating and lookahead photos, any key frame needed two steps ahead, and calls `decode()` on each.
2. At the boundary, if every participating photo has what the next step needs, the clock starts that step for all of them together.
3. If any is missing, every photo holds at that grid step. A 12-key photo holds on a whole frame. A sparse-key photo may hold part way through its long dissolve, which is still the same shared phase.
4. Recovery is bounded. Errored requests are retried twice with backoff, 10 seconds in total. After that the clock enters a stalled pause, the control reads "Resume animation", and nothing advances. Resume, an `online` event, or the stuck photo leaving the viewport re-checks the barrier.

Newly visible photos:

- If the lookahead already decoded the current pair, the photo joins at the shared phase before it gains any opacity. This is the normal case.
- If not, the photo shows its original. It requests the frames for the next boundary and counts toward that boundary's barrier. When it is ready it joins with the 600 ms fade as the next dissolve starts.
- A photo that scrolls away drops out of the barrier at once and its pending requests are abandoned. Fast scrolling through fourteen photos therefore shows originals and never queues fourteen sets of frames.

Under this policy the page shows either the shared seasonal phase or an original photograph. It does not show a seasonal frame from a different phase or a blank box, and the page never blocks scrolling while it waits.

If no seasonal frame can be loaded at all, for example the manifest fetch fails, the page stays on originals and the controls stay hidden. Galleries and the viewer do not depend on any of this.

## Controls and accessibility

- One footer group replaces the single button: Pause or Resume animation, then four season buttons for late summer, fall, winter and spring. No controls or labels on the hero itself, matching the approved hero.
- Pause freezes immediately, including mid-fade. The status text tells the truth, "Paused between fall and winter", or "Paused at winter" when exactly on an anchor. No season button shows as pressed while the state is a blend.
- A season button pauses the clock, loads that anchor for the participating photos, then dissolves them together over 600 ms straight to it. While paused on an anchor, a newly visible photo needs one frame.
- Resume continues from the held phase.
- Joined links get the existing hero description, "Animated seasonal concept. Opens the original property photograph." Seasonal layers are `alt=""`, not focusable, and ignore pointer events.
- Focus handling, captions, dots, counters and `inert` state in `listing.js` are untouched. A focused photo still stays fully visible and keeps animating.

Reduced motion, no-JS, print and save-data show originals and fetch nothing seasonal. If reduced motion turns on mid-session, stacks are removed at once with no animation. If it turns off again, the animation does not restart by itself. The control reappears as "Resume animation".

Seasonal autoplay in the narrative is a scoped exception to the product brief's no-autoplay rule, as the hero already is. Photo identities still change only by scroll.

## Lifecycle

| Event | Behavior |
| --- | --- |
| Tab hidden | Clock pauses, no fetches. On return it resumes from the same phase with no catch-up. |
| Any dialog open, including viewer, catalog and details | Clock pauses. The page is under a 90% backdrop. Dialogs show originals and allocate nothing seasonal. Close resumes from the same phase. |
| Photo scrolls out | Stack removed, decoded frames released, original shows. |
| Photo re-enters | Joins at the current shared phase as any new photo does. |
| Story falls back to inline photos | Originals only in that story. Recommended for the first build, see open choices. |
| `gallery.html` | Never loads the seasonal script or manifest. |
| bfcache restore | Treated like tab return. Animations are rebuilt from the logical clock. |
| Fresh load or ordinary back navigation | Starts at phase 0. |
| Same-tab state | Store only a "paused" flag in `sessionStorage` so a visitor who paused is not surprised after visiting the gallery. Do not persist phase. No cross-tab or cross-visitor sync. |
| Resize or breakpoint change | `layoutStories` rebuilds tracks. Stacks are dropped and rejoin at the current phase with the tier the new layout selects. |

## Shared asset contract

Owner: colonial-wtm. colonial-66v supplies sample metadata and produces conforming files. This is version 1 and needs 66v's agreement before intermediate production or final export.

**Photo ID.** The catalog position, 1 to 73, as used in `data-position`, `gallery.html#photo-N` and `assets/listing/NN.webp`.

**Phase grid.** `steps` is 12. Step k represents phase k/12. Anchors are late summer 0, fall 3, winter 6, spring 9. Every photo uses the same grid, so photos cannot drift apart. If the step count ever changes it stays a multiple of 4 and the anchors keep their fractions of the year.

**Treatment.** Every position has exactly one:

- `animated`: has `keys`, the grid steps for which this photo has its own frame. All four anchors are required. The runtime dissolves linearly between neighboring keys, wrapping from the last to the first.
- `invariant`: one generated frame for the whole year, for example a windowless interior with rebalanced light. Written as one key.
- `gallery-only`: no seasonal files. Originals everywhere.
- `non-photo`: no seasonal files and never edited. Position 31.

**Original reference.** `original` lists the keys served by the existing original derivative instead of a generated file. The hero uses it at step 0. Originals are never copied into the seasonal tree.

**Paths.** `assets/seasons/NN/FF-small.webp` and `assets/seasons/NN/FF-large.webp`, where NN is the position and FF is the key's grid step, both zero padded.

**Dimensions.** Each file has exactly the pixel width and height of that photo's original derivative at the same tier, as recorded in `assets/listing/manifest.json`. No crop, no padding, no change of aspect ratio. Small is 720w. Large is that photo's existing large width.

**Format.** WebP, sRGB, metadata stripped, encoded with the existing ImageMagick pipeline. No AVIF unless the byte thresholds fail.

**Eligibility.** A photo is in the delivery manifest only when the owner has approved its anchors and every frame and every transition between neighboring keys, including the wrap, has passed 66v's QA. A photo with any failed frame is left out entirely and shows its original. There is no partial year.

**Private versus public.** The delivery manifest holds only what the browser needs. Provenance, prompts, source hashes, model versions, QA records and byte reports stay in a private working manifest that the publish allowlist never includes. This matches how `assets/seasons/provenance.json` is handled now.

Delivery manifest example, `assets/seasons/delivery.json`:

```json
{
  "version": 1,
  "steps": 12,
  "year_seconds": 24,
  "anchors": {"late-summer": 0, "fall": 3, "winter": 6, "spring": 9},
  "photos": {
    "1":  {"treatment": "animated", "keys": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], "original": [0]},
    "2":  {"treatment": "animated", "keys": [0, 3, 6, 9]},
    "36": {"treatment": "invariant", "keys": [0]},
    "15": {"treatment": "gallery-only"},
    "31": {"treatment": "non-photo"}
  }
}
```

Position 1 is the exterior hero with 11 generated frames. Position 2 is a great room with window views, shown here with the 4 anchors only. Position 36 is a half bath with one rebalanced frame. The treatments shown illustrate the format. 66v's inventory decides the real ones.

Private working manifest, one record per unique frame, kept out of publication:

```json
{
  "position": 2, "key": 3, "anchor": "fall", "room_class": "interior",
  "original": {"small": "assets/listing/02-small.webp", "large": "assets/listing/02.webp"},
  "outputs": [
    {"path": "assets/seasons/02/03-small.webp", "width": 720, "height": 479, "bytes": 81234, "sha256": "..."},
    {"path": "assets/seasons/02/03-large.webp", "width": 1280, "height": 852, "bytes": 246810, "sha256": "..."}
  ],
  "master_sha256": "...", "model": "...", "prompt_ref": "...",
  "registration_max_px": 0.8, "anchor_approved": "owner, date", "qa": "pass"
}
```

The delivery manifest for all 73 positions is a few kilobytes.

## Budgets

Device and network assumptions: a 4 GB Android phone and a 3 GB iPhone at 390px wide, DPR 3, on slow 4G at 1.6 Mbps and fast 4G at 9 Mbps. A 1440x900 DPR 2 laptop on broadband. Per-frame bytes are assumed to match today's originals until 66v reports real exports.

**Tier selection.** Seasonal layers use the small tier whenever the viewport is 800px wide or less. Otherwise they use whichever tier the original's `currentSrc` selected. Left alone, a 390px DPR 3 phone picks the large file, and two large photos need 1.5 to 3 Mbps, which slow 4G cannot carry.

**Layers.** Worst case on screen is two photo identities: the hero with story 1's first photo, or two photos mid scroll blend. That is 4 seasonal image layers, plus up to 2 join fades. Today's hero alone uses 12.

**Decoded memory.** Each photo holds at most 3 seasonal frames, two shown and one prefetched. With one lookahead photo that is 9 frames.

| Tier | Per frame | 9-frame ceiling |
| --- | --- | --- |
| Small, 720x479 | 1.4 MB | 12 MB |
| Large, 1280x852 | 4.4 MB | 39 MB |
| Large, 1600x1046 | 6.7 MB | 60 MB |

The current 12-frame hero already holds 52 MB.

**Transfer rate at a 24 second year.**

| Case | 12 keys, one frame per 2 s | 4 keys, one frame per 6 s |
| --- | --- | --- |
| Small, median 71 KB | 0.28 Mbps | 0.09 Mbps |
| Small, max 153 KB | 0.61 Mbps | 0.20 Mbps |
| Large, median 230 KB | 0.92 Mbps | 0.31 Mbps |
| Large, max 478 KB | 1.91 Mbps | 0.64 Mbps |
| Hero large, mean 343 KB | 1.37 Mbps | not applicable |

A photo left on screen stops costing anything after one year, once its keys are in the HTTP cache. A 12-key photo tops out at 12 frames, a 4-key photo at 4.

Two 12-key photos at the small tier need 0.6 to 1.2 Mbps. That fits slow 4G with little room, which is one more reason to keep 12 keys for exteriors only.

**Session cost. This is the number to look at.** At 10 seconds per photo, a 12-key photo downloads about 7 seasonal frames, a 4-key photo about 3, an invariant photo 1. If all 66 narrative photos had 12 keys, a full read would add about 36 MB at the small tier or 113 MB at the large tier, on top of 5.2 MB or 16.2 MB of originals. With most interiors on 4 keys or 1, the added transfer falls to roughly a third of that. The exact figure waits on 66v's classification.

**Catalog size.** If all 67 hero and narrative photos had 12 keys, the published tree would hold about 64 MB small plus 199 MB large, 263 MB in total. Sparse keys bring it well under that. GitHub Pages allows a 1 GB site and soft-limits bandwidth at 100 GB a month. Every re-export also grows the Git history for good.

**Generation cost.** Generated images needed equal the total number of keys, less the keys served by originals. All 67 photos at 12 keys is about 800 generations. As an illustration only, 10 exteriors at 12 keys, 40 windowed interiors at 4 and 17 windowless interiors at 1 comes to about 290. The split is a guess until 66v classifies the set. Going from 4 keys to 12 on an interior can happen later, photo by photo, without touching the runtime or other photos.

**Working classification from captions, 7 October 2026.** Not yet checked against the pixels. 66v's inventory replaces it.

| Group | Positions | Keys |
| --- | --- | --- |
| Hero | 1 | 12, already produced |
| Exteriors, decks, grounds, aerials | 3, 6, 10, 16, 25 to 29, 33, 39 to 41, 43, 62 to 72 | 12 |
| Screened porch, treated as exterior and not light-rebalanced | 4, 17, 50 to 53 | 12 |
| Interiors with windows | about 30 | 4 |
| Primary bath, no window per owner | 7, 55, 56 | 1 |
| Already seasonal by caption | 8 fall color, 9 snowfall | none, see open choices |

That is about 31 new photos at 12 keys, 30 at 4 and 3 at 1, roughly 465 accepted generated images and about 500 delivered frames. A full read of the page would download about 38 MB at the small tier or 120 MB at the large tier. The published tree would be about 160 MB.

**Download scheduler, owner proposal.** Buffer by scroll proximity and cycle time: the visible photos first, then the next photos in the scroll direction, then the ones behind, each ordered by which key the clock reaches soonest. Fetch order blooms outward on two axes, time first: the keys the clock reaches next for the visible photos, then those same keys for the nearest photos in the scroll direction, then the following season, then photos further away. Whole years are never fetched for their own sake. A photo's year fills in only if the visitor stays near it. With five 12-key photos buffered and no scrolling, the scheduler needs 2.5 frames a second, 1.4 Mbps at the small tier, for at most 24 seconds.

The scheduler fixes readiness. Photos near the viewport join on time and the barrier rarely holds. It does not reduce bytes. It spends more of them sooner, so it needs a throttle: measure throughput from frames already fetched, using Resource Timing, then shrink the window, drop to the small tier, or stop prefetching when the link is slow or `saveData` is set. Window size, tier rules and thresholds are parameters for the implementation follow-up. The barrier stays as the backstop for when the scheduler cannot keep up.

**Generation cost.** Published Gemini API price for `gemini-3-pro-image-preview`, the model colonial-29s used, is $0.134 per 1K or 2K image, or $0.067 through the batch API. 4K is $0.24 and gives nothing useful at 1600px delivery.

| Scenario | Accepted images | At 1 attempt each | At 4 attempts each, standard | At 4 attempts each, batch |
| --- | --- | --- | --- | --- |
| Working classification above | 465 | $62 | $250 | $125 |
| Every photo at 12 keys | 726 | $97 | $390 | $195 |
| Exteriors and porch only, interiors later | 341 | $46 | $185 | $90 |

Four attempts is a ceiling for planning, not an expectation. With a settled prompt and reference images, plan on about two.

Other models in the family, at Google's list price on 7 October 2026: `gemini-3.1-flash-image-preview` is $0.067 at 1K, $0.034 batch, and up to $0.151 at higher resolutions. `gemini-2.5-flash-image` was $0.039 and was scheduled to shut down on 2 October 2026. Both current models accept up to 14 reference images per request. The owner has quoted lower prices of $0.02, $0.04 and $0.08, source not yet confirmed. At either set of prices the bill stays under a few hundred dollars.

Production order, following the owner's divide-and-conquer proposal and what colonial-29s did for the hero: generate the four anchors first, get them approved, then fill each gap from the fixed master with the two neighboring approved frames as appearance references. Every request edits the fixed master. No request edits a previous output, which is how geometry drifts. The approved hero frame for the same step goes in as a reference for every other photo, so "step 4" means the same foliage and light everywhere.

Batch pricing suits each bulk round, because each round already waits on owner review. It does not suit sample and prompt development, where a 24 hour target turnaround per try is too slow. Filling by bisection takes two or three batch rounds, so two or three days of waiting. The `nanobanana` CLI has no batch mode, so batch needs a small script like the existing private `generate.py`.

The hero's own history is not a guide to retry rates. The hero's 11 frames went through five rounds, v2 to v6, and its artifact folder holds far more than 11 raw outputs, but the exact call count was not logged. Reference images sent with each request add a cent or less per call.

The API bill is the small part. The larger cost is review: each accepted frame needs registration, a full-size check and a check of both neighboring dissolves, about 465 frames and as many transitions. Three things cut that:

1. For interiors, composite the generated window regions and a matched light adjustment onto one fixed rebalanced master. The room's geometry then cannot drift, registration passes by construction, and review is limited to the windows.
2. Settle prompts and recipe on the representative samples at standard price, then run the bulk through the batch API.
3. Stage it. Exteriors and porch first, since they carry the visible seasons. Interiors follow after the owner has seen the exteriors running.

**Proposed thresholds, to confirm at review.**

| Measure | Threshold |
| --- | --- |
| Small frame | 120 KB, hero 150 KB |
| Large frame | 350 KB, hero 420 KB |
| Published seasonal tree | 300 MB |
| Seasonal transfer per narrative photo at 10 s dwell, small tier | 550 KB at 12 keys, 250 KB at 4 keys |
| Live decoded seasonal frames | 9 |
| Animating seasonal layers | 4 |
| Boundary holds on fast 4G over three years of hero plus a two-photo scene | none over 100 ms |
| Slow 4G | holds allowed, zero incoherent or blank states |
| Scroll handler p95 with seasons running | within 10% of today's on the same device |
| Boundary swap work on the phone | under 8 ms |

If 66v's real exports exceed the frame caps or the 300 MB tree, hold the affected photos and record it. Do not lower the bar quietly.

## Touchpoints for the later implementation

Not edited by this ticket.

- `seasonal-hero.js`: replaced by one seasonal runtime for hero and narrative. The `data-seasons` URL list on the hero link goes away in favor of the manifest.
- `listing.js`: unchanged logic. The seasonal runtime needs to learn which photos have non-zero opacity and which is the lookahead, either from a small event dispatched at the end of `updatePhotos` or by observing `hidden` on figures. Seasonal layers must come after the original `<img>`, because `photoInset` and the preload code read the first image.
- `listing.css`: `.season-stack` positioning under `.hero-photo a` and `.is-scrolling .media-record > a`, and its `display: none` under print and reduced motion. The `plus-lighter` rules go.
- `index.html`: the footer control group, and removal of `data-seasons`. Listing prose, captions, alt text and figure markup stay byte-identical.
- `gallery.html` and `gallery.js`: no change. The viewer resolves photos from `[data-gallery-image]` links to `assets/listing/`.
- `assets/listing/manifest.json`: no change. It stays the record of originals.
- `scripts/publish-files.txt` and `tests/seo.test.mjs`: both enumerate seasonal files by name today. A full set needs a generated allowlist section and a matching test, decided when publication is separately approved.
- `PRODUCT.md`, `DESIGN.md`, `.impeccable/design.json`: update the autoplay exception, hero description and controls when the build is accepted.
- Analytics: no new events. `photo_open` and the rest keep their meaning.
- Hosting: no build step or backend is required. Repository growth from binary frames is the cost to watch.

## Verification strategy for the follow-up

Browser fixtures under `tests/`, following the existing iframe pattern, each reporting PASS. The clock takes its year length from one constant that fixtures can shorten. Phase is proven by reading the clock's frame and elapsed time and each upper layer's computed opacity. A screenshot alone is not evidence.

1. Shared phase. With hero and two narrative photos participating, computed opacities agree within 0.02 at 25%, 50% and 75% of every one of the 12 steps, including the wrap from step 11 to 0. Include one 12-key and one 4-key photo.
2. Exact blend. Over a known background, the midpoint pixel of a dissolve equals the mean of the two frames within rounding, and coverage is full. Repeat with the photo at 50% scroll opacity and compare with the same check on originals.
3. Scroll plus season. Scroll forward and backward through a blend while a dissolve runs. No geometry change in the photo box, caption, dots or story height. At most 4 seasonal layers exist.
4. Fast scroll. Fling through a 14-photo story. No more than the participating and lookahead photos have seasonal requests in flight, abandoned requests do not attach late, and no photo shows a frame from a phase other than the shared one.
5. Unready entry. Delay one photo's frames. It shows its original, the others hold on a whole frame at the next boundary, and it joins when ready.
6. Failure. Return 404, a corrupt body, and a stalled response for a required frame. The clock holds, retries twice, then stalls with the Resume control. Gallery, viewer and links keep working throughout.
7. Hidden tab and dialogs. Phase after return equals phase before. No seasonal requests while hidden or under a dialog.
8. Pause and seasons. Pause mid-fade freezes within one frame and the status names both neighboring anchors. Each season button lands every participating photo on the same anchor. Resume continues from there.
9. Originals stay originals. With seasons running, the viewer image, both previews, the full-size link, every catalog thumbnail and every `gallery.html` link resolve to `assets/listing/` and their bytes match the manifest hashes. No element in either gallery references `assets/seasons/`.
10. Fallbacks. With scripts disabled, in print media, under reduced motion and with save-data, no seasonal request is made and the rendered photos are the originals. Toggling reduced motion on and off mid-run does not restart motion.
11. Navigation. Open `gallery.html` and return by link, by back, and from bfcache. The paused preference survives. Nothing seasonal loads on the gallery page.
12. Regression. The existing Node, Python and browser fixtures still pass, including narrative scroll, resize reading position, focus, print layout and analytics events.
13. Budgets. On the phone profile under slow 4G and fast 4G throttling, record transfer per photo, live decoded frames, layer count and scroll handler timing against the thresholds above.

## Open choices with recommendations

1. **Keys per photo.** Year length is settled at 24 seconds. Recommend 12 keys for exteriors, 4 for interiors with window views, 1 for windowless interiors, confirmed photo by photo at anchor review. A 6 second dissolve between anchors through a window may look too coarse on large windows, and those photos can be raised to 12.
2. **Unready photos and the barrier.** Recommend that a visible unready photo holds the clock at the next boundary for up to 10 seconds. The looser option lets the others keep going while it shows its original. That is smoother on bad networks but leaves one still photo beside moving ones.
3. **Inline fallback stories.** Recommend originals only when a story is not sequenced. Those layouts can show three or four photos at once on the smallest screens, which breaks the two-photo ceiling.
4. **Manual season buttons under reduced motion.** Recommend none in the first build. A static season switch is possible later without animation.
5. **Large tier on wide desktops.** Recommend allowing it. If the session cost above is too high, restricting the narrative to the small tier everywhere cuts transfer by about two thirds at some loss of sharpness on large retina screens.
6. **Where the frame map lives.** Recommend a separate `delivery.json`. Inlining it in `index.html` saves one request but ties generated data to hand-maintained markup.
7. **Interior phase 0.** Interiors start on a rebalanced frame, not the original, so the first join is a visible lighting change over 600 ms. If that reads badly at review, the alternative is to join interiors only while they are off screen.

8. **Photos 8 and 9.** Their captions already name fall color and snowfall. Recommend moving both to gallery-only so they leave the narrative but keep their IDs, captions and deep links. Deleting either one changes the 73-photo catalog, the "View all 73 photos" label, frozen captions and tests, and needs its own ticket. Story 6 would drop to three photos, so the aerial choice there is worth a second look at the same time.

## Separately approved follow-up, not part of this ticket

Scope: build the private hero and narrative integration against the accepted contract and the accepted assets from colonial-66v.

Gates, in order:

1. Owner accepts this architecture and the contract. 66v agrees the contract before intermediate production.
2. Owner accepts 66v's representative samples, then the scoped anchors.
3. 66v delivers frames that pass its asset QA and reports real byte totals against the thresholds.
4. Implementation runs the verification list above end to end, including registration as seen through real scroll and season compositing, and the performance budgets on real devices.
5. Owner accepts the private result.
6. Publication, public disclosure wording, allowlist changes and deployment are a further separate decision.

colonial-66v owns asset QA and its local transition preview. The follow-up owns runtime and end-to-end QA. Neither current ticket delivers integrated website behavior.
