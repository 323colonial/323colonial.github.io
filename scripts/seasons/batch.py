#!/usr/bin/env python3
"""Staged build for exterior photos. usage: batch.py winter|shoulders POS ...   (config in CFG)"""
import pilot, prompt2, subprocess, json, sys, os
from concurrent.futures import ThreadPoolExecutor
SNOWDECK = 'Deck: at snowy steps the same thin snow lies on the deck boards, rail tops and chair seats; nothing else about the deck changes.'
FIRE = 'Fire: the fire in the stone pit stays lit, the same size. There are no other lights anywhere in the woods.'
CFG = {
 6:  dict(looks=135, aspect='4:3', has_house=False, has_plants=True, extra=[SNOWDECK, 'Hot tub: it is a Hot Spring Flair spa and it stays open exactly as in IMAGE 1, same position, size and shape, with the same water. Its blue interior lights are on, and so are its exterior lights, the vertical light strips at each corner of the cabinet. After dusk these are the main light on the deck: a blue glow in the water and on the nearest boards, rail and towels. No snow lies in the water. The folded towels stay.']),
 10: dict(looks=160, aspect='3:2', has_house=False, extra=[FIRE]),
 16: dict(looks=225, aspect='4:3', has_house=True, has_plants=True, extra=[SNOWDECK]),
 25: dict(looks=135, aspect='4:3', has_house=False, extra=['Garden: the vegetable plants inside the fence grow only from May to early October. At this moment follow that rule: {garden}. The fence, the stone wall and the wooden shed never change.']),
 27: dict(looks=120, aspect='3:2', has_house=False, extra=[FIRE]),
 43: dict(looks=180, aspect='3:2', has_house=False, has_plants=True, extra=[SNOWDECK, 'Hot tub: its cover stays closed; at snowy steps thin snow lies on the cover.']),
 17: dict(looks=270, aspect='3:2', has_house=False, extra=['Porch: it is roofed and screened, so its floor and furniture stay dry and free of snow and leaves in every season; the insect screens stay. Its ceiling lights are on, soft white, at the same brightness in every frame. The daybed cushions stay all year.', 'Table: from first frost to early spring the fruit bowl and the juice bottle are not on the table; show the bare tabletop where they stood.']),
 50: dict(looks=270, aspect='3:2', has_house=False, extra=['Porch: it is roofed and screened, so its floor and furniture stay dry and free of snow and leaves in every season; the insect screens stay. Its ceiling lights are on, soft white, at the same brightness in every frame. The daybed cushions stay all year.']),
 51: dict(looks=180, aspect='3:2', has_house=False, extra=['Porch: it is roofed and screened, so its floor and furniture stay dry and free of snow and leaves in every season; the insect screens stay. Its ceiling lights are on, soft white, at the same brightness in every frame. The daybed cushions stay all year.']),
 52: dict(looks=135, aspect='3:2', has_house=False, extra=['Porch: it is roofed and screened, so its floor and furniture stay dry and free of snow and leaves in every season; the insect screens stay. Its ceiling lights are on, soft white, at the same brightness in every frame. The daybed cushions stay all year.', 'Table: from first frost to early spring the fruit bowl and the juice bottle are not on the table; show the bare tabletop where they stood.']),
 53: dict(looks=90, aspect='3:2', has_house=False, extra=['Porch: it is roofed and screened, so its floor and furniture stay dry and free of snow and leaves in every season; the insect screens stay. Its ceiling lights are on, soft white, at the same brightness in every frame. The daybed cushions stay all year.', 'Table: from first frost to early spring the fruit bowl and the juice bottle are not on the table; show the bare tabletop where they stood.']),
 64: dict(looks=45, aspect='3:2', has_house=True),
 65: dict(looks=135, aspect='3:2', has_house=False, extra=['Garden: the beds inside the fence stay bare soil, as in IMAGE 1. The fence, the stone wall and the wooden shed never change.']),
 66: dict(looks=250, aspect='3:2', has_house=False),
}
L = lambda p: f'{pilot.ROOT}/assets/listing/{p:02d}.webp'
def one(a):
    pos, k = a; c = dict(CFG[pos]); aspect = c.pop('aspect'); o = L(pos); out = f'stage/{pos:02d}-{k:02d}'
    c['extra'] = [e.format(garden='the plants are there, as in IMAGE 1' if k in (0, 1, 10, 11) else 'the plants are gone and the beds are bare soil') for e in c.get('extra', [])]
    P = prompt2.build(k, **c); w, h = subprocess.run(['magick', 'identify', '-format', '%w %h', o], capture_output=True, text=True).stdout.split()
    raw, u = pilot.call([{'text': P}, pilot.img_part(o, pilot.CANVAS[aspect])], aspect); open(out + '-raw.jpg', 'wb').write(raw)
    subprocess.run(['magick', out + '-raw.jpg', '-resize', f'{w}x{h}!', out + '-full.png'], check=True)
    subprocess.run([sys.executable, 'align.py', o, out + '-full.png', out + '-a.png'], capture_output=True)
    r = subprocess.run([sys.executable, 'align.py', o, out + '-a.png', out + '.png'], capture_output=True, text=True).stdout; j = json.loads(r) if r.strip() else {}
    json.dump({'prompt': P, 'usage': u, 'align': j}, open(out + '.json', 'w'), indent=1)
    subprocess.run(['magick', out + '.png', '-resize', '480x360!', out + '-small.png']); subprocess.run(['magick', o, out + '.png', '-evaluate-sequence', 'Mean', '-resize', '480x360!', out + '-overlay.png'])
    return pos, k, j.get('max_shift_px'), f"{j.get('inliers')}/{j.get('patches')}", j.get('applied')
if __name__ == '__main__':
    steps = {'winter': [6], 'shoulders': [3, 9]}[sys.argv[1]]; ps = [int(x) for x in sys.argv[2:]] or list(CFG)
    with ThreadPoolExecutor(10) as ex:
        for r in ex.map(one, [(p, k) for p in ps for k in steps]): print(r, flush=True)
