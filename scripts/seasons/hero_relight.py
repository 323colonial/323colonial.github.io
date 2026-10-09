#!/usr/bin/env python3
"""Private re-light of hero frames 4 to 8 to the adopted dusk, night and dawn times. Published assets are not touched.
Base is the approved frame (with the revised window glass), so its leaves, frost and snow stay exactly as approved."""
import base64, json, os, subprocess, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pilot
D = pilot.OUT; MODEL = 'gemini-3-pro-image-preview'
def run(*a): return subprocess.run(a, capture_output=True, text=True)
def part(p, fit=None):
    d = subprocess.run(['magick', p] + (['-filter', 'Lanczos', '-resize', fit + '!'] if fit else []) + ['png:-'], check=True, capture_output=True).stdout
    return {'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(d).decode()}}
def one(k):
    os.makedirs(f'{D}/hero', exist_ok=True)
    base = f'{D}/win/hero/{k:02d}-after.png'; ref = f'{D}/review/img/39n/{k:02d}.webp'; name, desc = pilot.STEPS[k][2], pilot.STEPS[k][4]
    P = (f'Perform a meticulous LIGHTING-ONLY re-light of IMAGE 1, an approved photograph. It is frame {k} of a 12-frame annual timelapse, "{name}". '
         'Treat IMAGE 1 as a locked pixel canvas. Every physical edge stays at its input coordinate: roof, chimney, dormers, every window frame and muntin, siding, stone, porch, deck, lattice, path, birdbath, feeder pole, grill, every trunk and branch. '
         'Keep the seasonal state exactly as it is in IMAGE 1: the same leaves on the same branches, the same fallen leaves, the same frost and the same patches of snow in the same places and amounts. Do not add or remove snow, leaves or objects. '
         f'Change ONLY the time of day and therefore the light, the sky and the exposure, to this: {desc} {pilot.sun_text(k)} '
         + ('' if os.environ.get('NOREF') else 'IMAGE 2 shows the same house at this same moment from another camera: match its darkness, the color and depth of its sky, and how its window and porch light reads against the dusk. Use it for light only, never for composition. ') + 'The output must have exactly the composition and camera of IMAGE 1. '
         'The windows keep the same gentle soft-white glow they have in IMAGE 1, which now reads brighter against the darker scene and spills a little warm light onto the porch and the ground just outside. '
         'Preserve full photographic detail and grain. Nothing is crushed to pure black. Return ONE full-frame photograph.')
    body = {'contents': [{'role': 'user', 'parts': [{'text': P}, part(base, '2528x1696')] + ([] if os.environ.get('NOREF') else [part(ref)])}],
            'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': '3:2', 'imageSize': '2K'}, 'thinkingConfig': {'thinkingLevel': 'High'}}}
    req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent', data=json.dumps(body).encode(), headers={'x-goog-api-key': os.environ['GEMINI_API_KEY'], 'Content-Type': 'application/json'})
    try: r = json.load(urllib.request.urlopen(req, timeout=400))
    except urllib.error.HTTPError as e: return k, f'HTTP {e.code} {e.read().decode()[:300]}'
    raw = next((base64.b64decode(p['inlineData']['data']) for c in r.get('candidates', []) for p in c.get('content', {}).get('parts', []) if 'inlineData' in p), None)
    if not raw: return k, 'no image ' + json.dumps(r)[:200]
    s = f'{D}/hero/{k:02d}'; open(s + '-raw.png', 'wb').write(raw)
    run('magick', s + '-raw.png', '-filter', 'Lanczos', '-resize', '1280x848!', s + '-full.png')
    a1 = run(sys.executable, f'{pilot.HERE}/align.py', base, s + '-full.png', s + '-a.png').stdout.strip(); a2 = run(sys.executable, f'{pilot.HERE}/align.py', base, s + '-a.png', s + '.png').stdout.strip(); os.remove(s + '-a.png')
    mean = run('magick', s + '.png', '-colorspace', 'Gray', '-format', '%[fx:int(mean*100)]', 'info:').stdout
    json.dump({'step': k, 'model': MODEL, 'prompt': P, 'base': os.path.relpath(base, D), 'ref': os.path.relpath(ref, D), 'usage': r.get('usageMetadata'), 'align_first': a1, 'align_second': a2, 'mean': mean}, open(s + '.json', 'w'), indent=1)
    j = json.loads(a2) if a2 else {}
    return k, f"shift {j.get('max_shift_px')} inliers {j.get('inliers')}/{j.get('patches')} mean brightness {mean}"
if __name__ == '__main__':
    with ThreadPoolExecutor(5) as ex:
        for k, msg in ex.map(one, [int(a) for a in sys.argv[1:]]): print(k, msg)
