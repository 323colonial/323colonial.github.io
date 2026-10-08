#!/usr/bin/env python3
"""Photo 28: every season as a single-image edit, no reference image, so the model cannot borrow another camera."""
import pilot, subprocess, json, sys
from concurrent.futures import ThreadPoolExecutor
ORIG = f'{pilot.ROOT}/assets/listing/28.webp'; LATE = 'fin/28/04h.final.png'
KEEP = ('This is a precise retouch of IMAGE 1, NOT a new picture. Treat IMAGE 1 as a locked pixel canvas. The drone camera, its height, tilt and framing do not change. '
        'The house, roof, dormer, chimney, deck, railing, screened porch, propane tanks, stone retaining wall, stone planter, driveway and road stay at exactly their coordinates, sizes and shapes. '
        'Every tree trunk and main branch in IMAGE 1 stays exactly where it is, including the large pale tree on the right. Do NOT add any tree, sapling, shrub or object that is not in IMAGE 1, and do not remove any. '
        'The top edge of the picture stays filled with the same woods as IMAGE 1: do NOT reveal sky, horizon or a sunset there. Keep the deck empty. Keep the watermark. Return ONE sharp full-frame photograph. ')
JOBS = {
 0: (ORIG, 'Change ONLY this: it is late summer in clear mid-morning light. Grow mature deep-green leaves on the existing bare branches, so the same trees are simply in leaf; leaves may hide parts of the ground and road behind them but the trunks stay visible where they are. The ground between is green grass and moss with no fallen leaves. Neutral daylight, soft shadows.'),
 3: (ORIG, 'Change ONLY this: it is peak fall at golden hour, the sun low in the west-southwest, behind and to the left of the camera, so warm low light falls on the east wall facing the camera only weakly and the trees glow. Put red, russet and gold leaves, a little thinned, on the existing bare branches. Scatter fallen leaves over the moss and grass. The lamps inside are on: windows show a gentle soft-white glow.'),
 9: (ORIG, 'Change ONLY this: it is mid-April, a golden morning with the low sun in the east behind the camera, gently front-lighting the east wall, chimney and deck. Put small fresh light-green leaves at about half density on the existing bare branches, so branches still show. The ground is fresh green moss and grass with no fallen leaves. Clear soft light.'),
 6: (LATE, 'Change ONLY this: it is a midwinter night two hours after sunset under a new moon, photographed as a long-exposure night photograph. A few inches of snow cover the roof, the deck floor and railing tops, the stone walls and about 85% of the ground, with leaf litter showing at the margins, and a light tracery of snow on the branches. The scene is dark blue but fully legible, nothing crushed to black. The windows keep their soft-white glow, which spills onto the deck and nearby snow.'),
}
def one(k):
    base, what = JOBS[k]
    raw, u = pilot.call([{'text': KEEP + what}, pilot.img_part(base, pilot.CANVAS['4:3'])], '4:3')
    s = f'own28/{k:02d}'; open(s + '-raw.jpg', 'wb').write(raw)
    subprocess.run(['magick', s + '-raw.jpg', '-resize', '1280x960!', s + '-full.png'], check=True)
    subprocess.run([sys.executable, 'align.py', ORIG, s + '-full.png', s + '-a.png'], capture_output=True)
    r = subprocess.run([sys.executable, 'align.py', ORIG, s + '-a.png', s + '.png'], capture_output=True, text=True).stdout
    j = json.loads(r) if r.strip() else {}
    json.dump({'step': k, 'prompt': KEEP + what, 'base': base, 'usage': u, 'align': j}, open(s + '.json', 'w'), indent=1)
    return k, j.get('max_shift_px'), f"{j.get('inliers')}/{j.get('patches')}"
import os; os.makedirs('own28', exist_ok=True)
with ThreadPoolExecutor(4) as ex:
    for r in ex.map(one, [int(a) for a in sys.argv[1:]] or list(JOBS)): print(r)
