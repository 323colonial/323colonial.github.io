#!/usr/bin/env python3
"""Aerials 3 and 33: single-image edits, no reference image."""
import pilot, prompt2, subprocess, json, sys, os
from concurrent.futures import ThreadPoolExecutor
os.makedirs('aer', exist_ok=True)
L = lambda p: f'{pilot.ROOT}/assets/listing/{p:02d}.webp'
KEEP = ('This is a precise retouch of IMAGE 1, an aerial photograph, NOT a new picture. Treat IMAGE 1 as a locked pixel canvas. The drone camera, its height, tilt and framing do not change. '
        'Every building, roof, road, driveway, clearing, ridge line and horizon stays at exactly its coordinates, size and shape, and every tree stays where it is. Do NOT add or remove any tree, building or object. '
        'Any map pin, marker or watermark in IMAGE 1 stays exactly as it is. Return ONE sharp full-frame photograph. ')
def edit(pos, tag, base, P, aspect):
    o = L(pos); out = f'aer/{pos:02d}-{tag}'; w, h = subprocess.run(['magick', 'identify', '-format', '%w %h', o], capture_output=True, text=True).stdout.split()
    for attempt in (1, 2):
        raw, u = pilot.call([{'text': P}, pilot.img_part(base, pilot.CANVAS[aspect])], aspect); open(out + '-raw.jpg', 'wb').write(raw)
        subprocess.run(['magick', out + '-raw.jpg', '-resize', f'{w}x{h}!', out + '-full.png'], check=True)
        subprocess.run([sys.executable, 'align.py', base, out + '-full.png', out + '-a.png'], capture_output=True)
        j = json.loads(subprocess.run([sys.executable, 'align.py', base, out + '-a.png', out + '.png'], capture_output=True, text=True).stdout or '{}')
        if j.get('inliers', 0) >= 15: break
    json.dump({'prompt': P, 'base': base, 'align': j, 'attempts': attempt}, open(out + '.json', 'w'), indent=1)
    subprocess.run(['magick', o, out + '.png', '-evaluate-sequence', 'Mean', '-resize', '480x', out + '-overlay.png']); subprocess.run(['magick', out + '.png', '-resize', '480x', out + '-small.png'])
    print(pos, tag, 'attempts', attempt, 'shift', j.get('max_shift_px'), j.get('inliers'), '/', j.get('patches'), flush=True); return out + '.png'
def three():
    o = L(3); T = lambda k, looks=200: prompt2.light(k, looks)
    s = edit(3, '00', o, KEEP + 'Change ONLY this: it is late summer in clear mid-morning light. Grow mature deep-green leaves on the existing bare trees so the same woods are simply in full leaf. Lawns and clearings are green. Clear blue sky where sky shows. Soft neutral daylight with no hard shadows.', '4:3')
    with ThreadPoolExecutor(4) as ex:
        ex.submit(edit, 3, '03', s, KEEP + 'Change ONLY this: IMAGE 1 shows these woods in full summer leaf. Make it peak fall at golden hour: keep every leaf mass where it is and turn it red, russet, orange and gold with a little green left. ' + T(3) + ' Lamps are on in the house: its windows show a gentle soft-white glow.', '4:3')
        ex.submit(edit, 3, '09', o, KEEP + 'Change ONLY this: it is mid-April on a golden morning. Put small fresh light-green leaves at about half density on the existing bare trees, so branches still show. Grass and moss are fresh green, with no fallen leaves. ' + T(9), '4:3')
        f45 = ex.submit(edit, 3, '04h', o, KEEP + 'Change ONLY this: it is dusk in late November, about half an hour after sunset. The trees stay bare as they are. A light white frost lies on the roofs and on shaded ground; there is no snow. The overcast is gone: the sky is clear, deep blue with a fading peach band low toward the sunset. ' + T(4.5) + ' Lamps are on in the house: its windows show a gentle soft-white glow.', '4:3')
        base = f45.result()
    edit(3, '06', base, KEEP + 'Change ONLY this: it is a midwinter night two hours after sunset under a new moon, photographed as a long exposure. A few inches of snow cover the roofs, lawns, clearings and about 85% of the ground, with a light tracery of snow on the bare branches. The sky is blue-black with small stars. The scene is dark blue but fully legible, nothing crushed to black. The house windows keep their soft-white glow.', '4:3')
def thirty3():
    o = L(33); pin = ['The map pin marker stays exactly as it is, the same color and brightness in every frame.']
    with ThreadPoolExecutor(3) as ex:
        for k in (3, 9, 6):
            c = dict(looks=45, has_house=False, extra=pin + (['This is a wide aerial view: the snow shows on roofs, fields and clearings and as a pale dusting through the bare canopy; distant ridges are dark blue. Any distant town or house lights in IMAGE 1 may glow faintly; add none.'] if k == 6 else []))
            ex.submit(edit, 33, f'{k:02d}', o, prompt2.build(k, **c), '16:9')
with ThreadPoolExecutor(2) as ex: a = ex.submit(three); b = ex.submit(thirty3); a.result(); b.result()
