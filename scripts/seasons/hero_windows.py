#!/usr/bin/env python3
"""Private glass-only revision of the hero frames so window light follows photo 41. Published assets are not touched."""
import base64, json, os, subprocess, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pilot
from image_parts import png_part
D = os.path.dirname(os.path.abspath(__file__)); ROOT = pilot.ROOT; MODEL = 'gemini-3-pro-image-preview'
T = {3: (169, 128, 90), 6: (163, 141, 115), 9: (183, 149, 116)}      # photo 41 great-room glass, measured
lerp = lambda a, b, t: tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
for k in (4, 5): T[k] = lerp(T[3], T[6], (k - 3) / 3)
for k in (7, 8): T[k] = lerp(T[6], T[9], (k - 6) / 3)
T[2], T[10] = T[3], T[9]
STRENGTH = {2: 0.5, 10: 0.5}                                          # glow fades in and out at the ends
BOX = '130x110+565+378'                                               # front window, used to measure the glow
def run(*a): return subprocess.run(a, capture_output=True, text=True)
def glass_mean(img, mask):
    num = run('magick', img, mask, '-compose', 'Multiply', '-composite', '-crop', BOX, '+repage', '-resize', '1x1!', '-format', '%[fx:r] %[fx:g] %[fx:b]', 'info:').stdout.split()
    den = float(run('magick', mask, '-crop', BOX, '+repage', '-resize', '1x1!', '-format', '%[fx:mean]', 'info:').stdout or 0)
    return [255 * float(v) / den for v in num] if den > 0.02 else None
def one(k):
    name, outdoor = pilot.STEPS[k][2], pilot.STEPS[k][4]
    base = f'{D}/win/hero/{k:02d}-before.png'; run('magick', f'{ROOT}/{pilot.STEPS[k][1]}', base)
    ref = f'{D}/win/ref41-{3 if k <= 4 else 6 if k <= 7 else 9:02d}.png'
    P = (f'Perform a meticulous WINDOW-GLASS-ONLY retouch of IMAGE 1, an approved photograph of a house. It is frame {k} of a 12-frame annual timelapse, "{name}". {outdoor} '
         'Treat IMAGE 1 as a locked pixel canvas. Every pixel that is not window glass must stay exactly as it is: siding, stone, roof, snow, window frames, muntin grids, door, porch, trees, ground, sky, light and color. '
         'Do not move, redraw, sharpen, denoise or relight anything else. Preserve the full photographic detail and grain of IMAGE 1. '
         'Inside the glass of every window and the door glass only: the lamps in the house are on. Show a gentle warm soft-white glow from within, with a faint sense of the lit room behind the glass, '
         'at the same warmth and the same moderate brightness as the large windows in IMAGE 2, which shows another side of this same house at a similar moment. '
         'The glass must not be a flat bright panel, must not be orange, must not be blown out and must not be mirror-like. Any reflection left in the glass is faint and shows the trees exactly as they look in IMAGE 1 at this season, never out-of-season foliage. '
         'Keep every frame, muntin and pane edge exactly in place. Return ONE full-frame photograph.')
    body = {'contents': [{'role': 'user', 'parts': [{'text': P}, png_part(base, '2528x1696'), png_part(ref)]}],
            'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': '3:2', 'imageSize': '2K'}, 'thinkingConfig': {'thinkingLevel': 'High'}}}
    req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent', data=json.dumps(body).encode(),
                                 headers={'x-goog-api-key': os.environ['GEMINI_API_KEY'], 'Content-Type': 'application/json'})
    try: r = json.load(urllib.request.urlopen(req, timeout=400))
    except urllib.error.HTTPError as e: return k, f'HTTP {e.code} {e.read().decode()[:300]}'
    raw = next((base64.b64decode(p['inlineData']['data']) for c in r.get('candidates', []) for p in c.get('content', {}).get('parts', []) if 'inlineData' in p), None)
    if not raw: return k, 'no image ' + json.dumps(r)[:200]
    s = f'{D}/win/hero/{k:02d}'; open(s + '-raw.png', 'wb').write(raw)
    run('magick', s + '-raw.png', '-filter', 'Lanczos', '-resize', '1280x848!', s + '-full.png')
    al = run(sys.executable, f'{D}/align.py', base, s + '-full.png', s + '-aligned.png').stdout.strip()
    run('magick', base, s + '-aligned.png', '-compose', 'Difference', '-composite', '-colorspace', 'Gray', '-blur', '0x2', '-threshold', '8%', '-morphology', 'Open', 'Disk:3', '-morphology', 'Close', 'Disk:4',
        '(', '-size', '1280x848', 'xc:black', '-fill', 'white', '-draw', 'rectangle 330,170 1130,520', ')', '-compose', 'Multiply', '-composite', '-blur', '0x1.5', s + '-mask.png')
    got = glass_mean(s + '-aligned.png', s + '-mask.png'); gain = [1, 1, 1]
    if got: gain = [max(0.55, min(1.4, T[k][i] / max(got[i], 1))) for i in range(3)]
    run('magick', s + '-aligned.png', '-color-matrix', f'{gain[0]} 0 0 0 {gain[1]} 0 0 0 {gain[2]}', s + '-toned.png')
    st = STRENGTH.get(k, 1.0)
    run('magick', s + '-mask.png', '-evaluate', 'multiply', str(st), s + '-mask-s.png')
    run('magick', base, s + '-toned.png', s + '-mask-s.png', '-composite', s + '-after.png')
    after = glass_mean(s + '-after.png', s + '-mask.png')
    json.dump({'step': k, 'model': MODEL, 'prompt': P, 'ref': os.path.relpath(ref, D), 'usage': r.get('usageMetadata'), 'align': al, 'target': T[k], 'model_glass': got, 'gain': gain, 'strength': st, 'final_glass': after}, open(s + '.json', 'w'), indent=1)
    return k, f"tokens {r.get('usageMetadata', {}).get('totalTokenCount')} target {[round(v) for v in T[k]]} model {[round(v) for v in got] if got else None} final {[round(v) for v in after] if after else None} strength {st}"
if __name__ == '__main__':
    with ThreadPoolExecutor(3) as ex:
        for k, msg in ex.map(one, [int(a) for a in sys.argv[1:]]): print(k, msg)
