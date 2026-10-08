#!/usr/bin/env python3
"""Hot tub: lighting-only re-light of a geometry-locked frame with Nano Banana Pro. usage: tub_relight.py STEP 'time and light sentence'"""
import base64, json, os, subprocess, sys, urllib.request, urllib.error
k = int(sys.argv[1]); when = sys.argv[2]; base = f'tub/{k:02d}-water.png'; out = f'tub/r{k:02d}' + os.environ.get('TAG', '')
P = ('Perform a LIGHTING-ONLY re-light of IMAGE 1, a photograph of a hot tub on a snowy deck. Treat IMAGE 1 as a locked pixel canvas: the hot tub, its cover, the steps, the towels and side table, the deck boards, the railing, the cedar wall and every tree trunk and branch stay at exactly their coordinates, sizes and shapes. Do not zoom, widen or re-frame. Do not add or remove any object, snow or leaves. '
     'Keep the swirling, bubbling water exactly as it is in shape and texture.\n\n'
     f'Change only the light, the sky and the exposure: {when} '
     'The hot tub is the star of the picture. It is a Hot Spring Flair. Its underwater lighting is many small LED points set low in the shell walls and seat backs, well below the waterline. They shine a clear, translucent BLUE, the hue of Cherenkov radiation in a reactor pool but gentler: a little less saturated, like light seen through clear water, never an opaque or neon blue. Not cyan, not turquoise, not lavender or violet. The white foam and the pale shell show through the glow. '
     'Because the lights are submerged in churning, bubbling water, the light is diffuse: the whole body of water glows from within, deepest and most saturated toward the walls where the lights are, and the individual points are only soft, blurred blooms under the surface, never sharp dots on top of it. '
     'The vertical light strips at the cabinet corners glow the same blue. The blue spills softly onto the tub rim, the nearest snowy boards, the railing and the towels. '
     'One more light: a soft, low, warm light from off camera at the right, as from a lit window out of frame. It gently warms the near deck boards, the towels and side table, the right-hand cedar wall and the side of the tub cabinet, and falls off quickly. No light fixture is visible. '
     'A second warm light: a broad, soft, diffuse warm light from the north, which is behind the camera and to its left, as from the lit house behind the photographer. It adds a gentle warm fill to the front and left side of the tub cabinet, the black steps, the tub rim and the snowy boards in the foreground, with no hard shadows. It is weaker than the blue glow of the water and does not reach the forest. '
     'The forest keeps exactly the natural, photographic look it has in IMAGE 1: the same bare grey-brown trunks and twigs with a little snow, simply darker and cooler in the dusk. Do not stylize, smooth or repaint the trees. '
     'The sky is plain and natural, like a real long-exposure photograph: a real night sky under a new moon: very dark blue-black, with only the faintest lighter tone at the horizon, and many small, pin-sharp stars of varied brightness that also show between the upper branches. No large or glowing stars and no saturated color. No glowing or large stars and no saturated color. '
     'Overall it is night, photographed as a long exposure: the forest is dark, its trunks and snow-dusted branches faintly visible in starlight, and snow away from the lights is a deep dusky blue. The lit foreground stays warm and inviting and the tub is the brightest thing in the picture. Nothing is crushed to pure black. Still easy to read, nothing crushed to black.\n\nReturn ONE full-frame photograph.')
def part(p):
    d = subprocess.run(['magick', p, '-filter', 'Lanczos', '-resize', '2400x1792!', 'png:-'], check=True, capture_output=True).stdout
    return {'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(d).decode()}}
body = {'contents': [{'role': 'user', 'parts': [{'text': P}, part(base)]}], 'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': '4:3', 'imageSize': '2K'}, 'thinkingConfig': {'thinkingLevel': 'High'}}}
req = urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent', data=json.dumps(body).encode(), headers={'x-goog-api-key': os.environ['GEMINI_API_KEY'], 'Content-Type': 'application/json'})
try: r = json.load(urllib.request.urlopen(req, timeout=400))
except urllib.error.HTTPError as e: sys.exit(f'HTTP {e.code} {e.read().decode()[:300]}')
raw = next(base64.b64decode(p['inlineData']['data']) for c in r['candidates'] for p in c['content']['parts'] if 'inlineData' in p)
open(out + '-raw.png', 'wb').write(raw); subprocess.run(['magick', out + '-raw.png', '-filter', 'Lanczos', '-resize', '1600x1205!', out + '-full.png'], check=True)
a = subprocess.run([sys.executable, 'align.py', base, out + '-full.png', out + '.png'], capture_output=True, text=True).stdout; j = json.loads(a) if a.strip() else {}
json.dump({'step': k, 'prompt': P, 'usage': r.get('usageMetadata'), 'align': j}, open(out + '.json', 'w'), indent=1)
print(k, 'shift', j.get('max_shift_px'), 'matched', j.get('inliers'), '/', j.get('patches'), 'mean', subprocess.run(['magick', out + '.png', '-colorspace', 'Gray', '-format', '%[fx:int(mean*100)]', 'info:'], capture_output=True, text=True).stdout)
