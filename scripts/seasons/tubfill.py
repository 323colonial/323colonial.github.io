#!/usr/bin/env python3
"""Hot tub in-between frames: shallow objects-only edits (2.1), then lighting-only re-lights (Pro) with the approved winter as a narrow reference."""
import pilot, subprocess, json, sys, base64, os, urllib.request
from concurrent.futures import ThreadPoolExecutor
src = open('tub.py').read(); HEAD = eval(src[src.index("HEAD = (") + 7:src.index("PLANT_OUT =")].strip())
O = f'{pilot.ROOT}/assets/listing/06.webp'
GONE = '- The potted plant, its white pot and the wrought-iron stand are indoors. Remove all three (if any of them is still in IMAGE 1). Where they were, show the deck boards, the deck railing and the trees beyond it.\n'
TAIL = '- Hot tub water: unchanged, the same swirling water as IMAGE 1.\n- Light, sky and exposure: unchanged from IMAGE 1.\n\nEverything not listed stays pixel for pixel as in IMAGE 1, and just as sharp.'
OBJ = {  # step: (base, change)
 2: (O, '- Trees: about a third of the leaves have turned amber and russet; the rest stay green. Same trees, same shapes.\n- Deck boards: dry, with a few fallen leaves.\n' + GONE),
 4: ('tub/fA.png', '- Trees: half of the leaves have fallen. The rest are muted brown and russet, and bare branches show between them.\n- Deck boards and rail tops: a thin white frost and a few fallen leaves. No snow.\n' + GONE),
 5: ('tub/wA.png', '- Snow: a first thin dusting lies on the deck boards and rail tops, with the boards still showing through, and a trace on the branches. No snow in the water or on the towels.\n' + GONE),
 7: ('tub/wA.png', '- Snow: old snow is melting. Patchy thin snow remains on parts of the deck boards and rail tops with wet boards between, and on the ground beyond the railing. No snow in the water or on the towels.\n' + GONE),
 8: ('tub/wA.png', '- Trees: the bare branches carry buds and a first haze of tiny pale-green leaves.\n- Deck boards: damp and clear of snow.\n' + GONE),
}
LIGHT = {  # step: (moment, strength of the tub and warm lights, sky and exposure)
 4: ('dusk about twenty minutes after sunset in mid-November', 'at about half of their night strength', 'The sky is a deepening blue with a soft peach band low down. The deck and trees are in dim, cool, shadowless light, clearly darker than day but far from night.'),
 5: ('deep dusk about forty-five minutes after sunset in early December', 'at about three quarters of their night strength', 'The sky is deep blue with the first few faint stars. The scene is dark and cool, a step short of night, and stays easy to read.'),
 7: ('deep pre-dawn about forty minutes before sunrise in late February', 'at about three quarters of their night strength', 'The sky is a dim, muted blue-grey, a little paler low down, with the last faint stars. The scene is dark and cool, a step short of night, and stays easy to read.'),
 8: ('dawn about ten minutes before sunrise in late March', 'at about a third of their night strength', 'The sky is pale blue with soft pink low down. The light is cool, soft and shadowless, with no direct sun yet, and the scene is fairly bright.'),
}
def obj(k):
    base, change = OBJ[k]; out = f'tub/o{k:02d}'
    for attempt in (1, 2, 3):
        raw, u = pilot.call([{'text': HEAD + change + TAIL}, pilot.img_part(base, pilot.CANVAS['4:3'])], '4:3'); open(out + '-raw.jpg', 'wb').write(raw)
        subprocess.run(['magick', out + '-raw.jpg', '-resize', '1600x1205!', out + '-full.png'], check=True)
        j = json.loads(subprocess.run([sys.executable, 'align.py', base, out + '-full.png', out + '.png'], capture_output=True, text=True).stdout or '{}')
        if j.get('inliers', 0) >= 20: break
    print('objects', k, 'attempts', attempt, 'shift', j.get('max_shift_px'), j.get('inliers'), '/', j.get('patches'), flush=True); return j.get('inliers', 0) >= 20
def part(p):
    d = subprocess.run(['magick', p, '-filter', 'Lanczos', '-resize', '2400x1792!', 'png:-'], check=True, capture_output=True).stdout
    return {'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(d).decode()}}
def relight(k):
    when, strength, sky = LIGHT[k]; base = f'tub/o{k:02d}.png'; out = f'tub/L{k:02d}'
    P = ('Perform a LIGHTING-ONLY re-light of IMAGE 1, a photograph of a hot tub on a deck. Treat IMAGE 1 as a locked pixel canvas: every object, tree, leaf, patch of frost or snow, the framing and the swirling water stay exactly where and as they are. Do not add or remove anything.\n\n'
         'IMAGE 2 is an approved night photograph of this same deck. Use it ONLY for the character of its lights: the blue-cyan glow of the hot tub water with soft submerged points, the blue vertical light strip on the cabinet corner, the soft warm light on the deck at the right, and the weaker warm fill on the boards at the front left. Take nothing else from IMAGE 2: not its snow, its trees, its sky or its darkness.\n\n'
         f'Change only the light, sky and exposure of IMAGE 1 to {when}. {sky} The lights from IMAGE 2 show {strength}; the warm lights never reach the trees. Keep the trees as crisp and natural as in IMAGE 1.\n\nReturn ONE full-frame photograph.')
    body = {'contents': [{'role': 'user', 'parts': [{'text': P}, part(base), part('tub/WINTER.png')]}], 'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': '4:3', 'imageSize': '2K'}, 'thinkingConfig': {'thinkingLevel': 'High'}}}
    req = urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent', data=json.dumps(body).encode(), headers={'x-goog-api-key': os.environ['GEMINI_API_KEY'], 'Content-Type': 'application/json'})
    r = json.load(urllib.request.urlopen(req, timeout=400))
    raw = next(base64.b64decode(p['inlineData']['data']) for c in r['candidates'] for p in c['content']['parts'] if 'inlineData' in p)
    open(out + '-raw.png', 'wb').write(raw); subprocess.run(['magick', out + '-raw.png', '-filter', 'Lanczos', '-resize', '1600x1205!', out + '-full.png'], check=True)
    j = json.loads(subprocess.run([sys.executable, 'align.py', base, out + '-full.png', out + '.png'], capture_output=True, text=True).stdout or '{}')
    json.dump({'step': k, 'prompt': P, 'align': j}, open(out + '.json', 'w'), indent=1)
    print('relight', k, 'shift', j.get('max_shift_px'), j.get('inliers'), '/', j.get('patches'), flush=True)
with ThreadPoolExecutor(5) as ex: ok = dict(zip(OBJ, ex.map(obj, OBJ)))
with ThreadPoolExecutor(4) as ex: list(ex.map(relight, [k for k in LIGHT if ok.get(k)]))
