#!/usr/bin/env python3
"""Photo 6, the hot tub: a chain of small tailored edits outward from the original, forward 1..6 and backward 11..7."""
import pilot, subprocess, json, sys, os
from concurrent.futures import ThreadPoolExecutor
O = f'{pilot.ROOT}/assets/listing/06.webp'; D = 'tub'; os.makedirs(D, exist_ok=True)
HEAD = ('IMAGE 1 is a photograph of a hot tub on a wooden deck. Make a small change to it and return the same photograph.\n\n'
        'The picture contains only these things, and each stays exactly where it is, at the same size, shape and angle: the Hot Spring Flair hot tub with its open cover standing behind it, its blue-lit water and the lit vertical light strips at its cabinet corners; the two black steps at its left; the small wooden side table with folded white towels; the wrought-iron plant stand; the deck boards; the deck railing; the cedar wall on the right with the grey electrical panel; the trees beyond the railing; and a small patch of sky at the upper left. '
        'Nothing else exists in this picture and nothing may be added. The camera does not move: do not zoom out, widen, tilt or re-frame, and keep the tub exactly as large in the frame as it is now. The hot tub lights are on in every version.\n\nCHANGE ONLY:\n')
PLANT_OUT = '- The potted plant with yellow and green leaves has been taken indoors. Remove the plant and its white pot. The empty wrought-iron stand remains. Where the plant was, show the deck railing and the trees beyond it.\n'
STAND_OUT = '- The wrought-iron plant stand has been taken indoors too. Remove it. Where it stood, show the deck boards and the lower part of the railing.\n'
STAND_IN = '- The empty wrought-iron plant stand is back in its usual place just right of the side table, in front of the railing.\n'
PLANT_IN = '- A potted croton with yellow and green leaves in a white pot is back on the wrought-iron stand, as large as the stand is tall.\n'
S = {
 1: '- Trees: about one leaf in ten has turned yellow; the rest stay green.\n- Light: late afternoon. The sun is behind the camera and the house, so the deck is in soft open shade and the trees beyond are lit slightly warm.\n- Deck boards: dry, with two or three fallen leaves.\n',
 2: '- Trees: about a third of the leaves are now amber and russet.\n- Light: a little lower and warmer than in IMAGE 1, still soft shade on the deck.\n- Deck boards: a few more fallen leaves.\n' + PLANT_OUT,
 3: '- Trees: the leaves are now mostly red, russet and gold with a little green. Same trees, same shapes.\n- Deck boards: a light scatter of fallen leaves.\n- Light, sky and exposure: unchanged from IMAGE 1.\n',
 4: '- Trees: half of the leaves have fallen; the rest are brown and russet, with bare branches showing.\n- Deck boards and rail tops: a thin white frost. No snow.\n- Light, sky and exposure: unchanged from IMAGE 1.\n' + STAND_OUT,
 5: '- Trees: the branches are almost bare.\n- Deck boards and rail tops: a thin dusting of snow with boards showing through. No snow in the water.\n- Light, sky and exposure: unchanged from IMAGE 1.\n',
 6: '- Trees: bare, with a light tracery of snow on the branches.\n- Deck boards and rail tops: an even thin layer of snow. No snow in the water or on the towels.\n- Light, sky and exposure: unchanged from IMAGE 1.\n',
 11: '- Trees: full deep-green midsummer leaves, with no yellow.\n- Light: clear mid-morning daylight.\n- Deck boards: dry.\n',
 10: '- Trees: fresh, lighter green late-spring leaves, slightly less dense.\n- Light: soft morning sun from the left, ahead of the camera.\n- Deck boards: dry.\n',
 9: '- Trees: the leaves are smaller and sparser: small new light-green leaves at about half density, with branches visible between them.\n- Light, sky and exposure: unchanged from IMAGE 1.\n' + PLANT_OUT,
 8: '- Trees: bare branches with buds and only a few tiny leaves.\n- Deck boards: damp, with small remnants of snow at the foot of the railing only.\n- Light, sky and exposure: unchanged from IMAGE 1.\n',
 7: '- Trees: bare branches.\n- Deck boards and rail tops: patchy thin snow, melting, with wet boards between.\n- Light, sky and exposure: unchanged from IMAGE 1.\n' + STAND_OUT,
}
def make(k, base):
    P = HEAD + S[k] + '\nEverything not listed stays pixel for pixel as in IMAGE 1.'; out = f'{D}/{k:02d}'
    for attempt in (1, 2):
        raw, u = pilot.call([{'text': P}, pilot.img_part(base, pilot.CANVAS['4:3'])], '4:3'); open(out + '-raw.jpg', 'wb').write(raw)
        subprocess.run(['magick', out + '-raw.jpg', '-resize', '1600x1205!', out + '-full.png'], check=True)
        subprocess.run([sys.executable, 'align.py', base, out + '-full.png', out + '-a.png'], capture_output=True)
        r = subprocess.run([sys.executable, 'align.py', base, out + '-a.png', out + '.png'], capture_output=True, text=True).stdout; j = json.loads(r) if r.strip() else {}
        if j.get('inliers', 0) >= 20: break
    ro = subprocess.run([sys.executable, 'align.py', O, out + '.png', '/tmp/claude-501/tubchk%d.png' % k], capture_output=True, text=True).stdout; jo = json.loads(ro) if ro.strip() else {}
    json.dump({'step': k, 'base': base, 'prompt': P, 'usage': u, 'align': j, 'vs_original': jo, 'attempts': attempt}, open(out + '.json', 'w'), indent=1)
    subprocess.run(['magick', O, out + '.png', '-evaluate-sequence', 'Mean', '-resize', '400x301!', out + '-overlay.png'])
    print(k, 'vs base: shift', j.get('max_shift_px'), 'matched', j.get('inliers'), '/', j.get('patches'), '| vs original: matched', jo.get('inliers'), '/', jo.get('patches'), 'shift', jo.get('max_shift_px'), '| attempts', attempt, flush=True)
    return out + '.png', j.get('inliers', 0) >= 20
def chain(steps):
    base = O
    for k in steps:
        base, ok = make(k, base)
        if not ok: print('chain stopped at', k, flush=True); break
def chain2(a):
    base, steps = a
    for k in steps:
        base, ok = make(k, base)
        if not ok: print('chain stopped at', k, flush=True); break
with ThreadPoolExecutor(2) as ex: list(ex.map(chain2, [('tub/02.png', [3, 4, 5, 6]), ('tub/10.png', [9, 8, 7])]))
