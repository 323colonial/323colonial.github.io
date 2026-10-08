#!/usr/bin/env python3
"""Rewritten prompt, exterior and outlook photos. One rule decides everything: what is listed under CHANGE changes, the rest stays.
There are no exceptions to remember, so nothing in it contradicts anything else. Each image has one stated job."""
import pilot

# State of the scene at each whole step, as plain targets. Half steps are added when needed.
STATE = {
 0:  dict(name='late summer, mid-morning', leaves='full, mature, deep green', ground='green grass, a little dry; no fallen leaves', sky='clear blue with a few white clouds', lit=False, plants='all'),
 1:  dict(name='early fall, late afternoon', leaves='full; nine leaves in ten still green, one in ten yellow', ground='green grass with only a handful of fallen leaves', sky='clear blue, slightly warmer toward the sun', lit=False, plants='all'),
 2:  dict(name='mid-October, approaching golden hour', leaves='full; about two thirds green, one third amber and russet', ground='grass turning olive; a light scatter of fallen leaves; moss in the bare patches', sky='pale blue with faint warm wisps', lit='faint', plants='stands'),
 3:  dict(name='peak fall, golden hour', leaves='slightly thinned; mostly red, russet and gold with a little green', ground='olive grass with fallen leaves scattered across it; green moss in the bare patches', sky='scattered clouds catching pink and orange', lit=True, plants='stands'),
 4:  dict(name='first frost, dusk twenty minutes after sunset', leaves='half fallen; the rest muted brown and russet, bare branches showing', ground='a thick layer of fallen red and brown leaves over grass that is still partly green and olive; thin white frost on the leaves and grass wherever the ground is shaded; no snow', sky='deepening blue with a peach band low toward the sunset', lit=True, plants='none', roof='thin patchy white frost, shingles showing'),
 5:  dict(name='first light snow, deep dusk', leaves='branches almost bare', ground='a thin first dusting of snow over about 40% of the ground, lying in connected patches in the shade of trunks and evergreens; the open middle, the paths and the ground under dense branches still show brown leaf litter and dormant olive grass', sky='deep blue with a narrow fading peach band and the first stars', lit=True, plants='none', roof='an even light dusting of snow, shingle texture faintly visible'),
 6:  dict(name='midwinter night, new moon', leaves='bare branches with a light tracery of snow', ground='a few inches of snow over about 85% of the ground, including the paths; brown leaf litter and dormant grass show only at the bases of trunks and under evergreens', sky='blue-black, full of stars', lit=True, plants='none', roof='a few inches of snow'),
 7:  dict(name='snowmelt, deep pre-dawn', leaves='bare branches with tiny buds', ground='thaw has begun: snow covers about 60% and is thinner, grainy and broken at its edges; it has gone first from the open ground and from any paths or driveway that IMAGE 1 already shows, exposing damp straw-brown grass and matted brown leaves; no new path, gravel or paving appears; it remains in the shade of trunks and evergreens', sky='dim, muted blue-grey with a faint peach tone toward sunrise', lit=True, plants='none', roof='thinning snow with shingles showing at the edges'),
 8:  dict(name='new growth, dawn ten minutes before sunrise', leaves='buds and the first small leaves on about a fifth of the branches', ground='snow is down to about 30%, only as separate shrinking patches in the deepest shade; the rest is damp straw-brown and olive grass with matted leaf litter, and the first small green shoots and green moss are appearing; existing paths are clear; lawn stays lawn, and no new path, gravel or paving appears', sky='pale blue above soft pink and peach toward sunrise', lit=True, plants='stands', roof='snow only in remnants'),
 9:  dict(name='spring, golden morning', leaves='small fresh light-green leaves at about half density, branches visible', ground='no snow; short new grass, mostly fresh green but still mixed with olive and straw patches, with light dew; green moss in the bare patches; last year\'s leaf litter mostly gone', sky='clear pale blue', lit=True, plants='stands'),
 10: dict(name='late spring, morning', leaves='fresh green at about 85% density', ground='grass a little taller, fuller and a deeper soft green than in spring, with the straw patches grown over; no dew. The grass is the only thing that grows: no new shrubs, plants or flower beds appear', sky='clear blue', lit='faint', plants='all'),
 11: dict(name='midsummer, mid-morning', leaves='full, mature, deep green', ground='mature green grass beginning to dry back, with thinner, paler patches in the open sun', sky='clear blue', lit=False, plants='all'),
}

SINCE = {
 5: 'IMAGE 1 shows the frame before this one, first frost. Since then the last leaves have fallen and the first snow has dusted the shaded ground.',
 7: 'IMAGE 1 shows the frame before this one, midwinter night. Since then about a third of the snow has melted: the ground changes visibly, with paths and open ground now bare and wet.',
 8: 'IMAGE 1 shows the frame before this one, snowmelt. Since then half of the remaining snow has gone and the first green has appeared: the ground changes visibly.',
 9: 'IMAGE 1 shows the frame before this one, new growth. Since then the last snow has gone, the grass has turned green and the trees have leafed out to half density.',
 10: 'IMAGE 1 shows the frame before this one, spring. Since then five weeks of growth have passed: the canopy and the ground are both visibly fuller and deeper green.',
}

def light(step, looks):
    """One sentence: where the light comes from for this camera, and what kind it is."""
    az, el = pilot.sun(step); rel = (az - looks + 180) % 360 - 180
    side = ('ahead of the camera' if abs(rel) <= 45 else 'behind the camera' if abs(rel) >= 135 else f'to the camera\'s {"right" if rel > 0 else "left"}')
    if el < -12: return 'Night. Light comes only from the stars, dim and cool blue on the snow and trees, and from the windows and porch lights, warm on whatever is near them. Everything stays legible.'
    if el < 0: return f'Twilight, no direct sun. Even, cool, shadowless light; the sky is brightest low {side}.'
    kind = 'very low, weak and warm, nearly horizontal' if el < 8 else 'low and warm' if el < 20 else 'clear daylight, slightly warm' if el < 35 else 'clear neutral daylight'
    shadows = 'toward the camera' if abs(rel) <= 45 else 'away from the camera' if abs(rel) >= 135 else f'to the {"left" if rel > 0 else "right"}'
    return f'Sun {max(el, 1)} degrees up, {side}; {kind}. Soft shadows fall {shadows}.' + (' The sun itself stays hidden behind trees.' if abs(rel) <= 45 else ' The sun is outside the picture.')

def build(step, looks, toward=None, has_house=True, has_plants=False, second=None, extra=(), prev=False):
    """toward: (step number, description) of a second image, or None."""
    s = STATE[step]
    lines = [f'Edit IMAGE 1 so that it shows the same view at a different moment: {s["name"]}.', '',
             'IMAGE 1 is the photograph to edit. Its camera, framing and objects are the truth.']
    if prev and step in SINCE: lines.append(SINCE[step])
    if second: lines.append('IMAGE 2 is another approved frame of this same view. ' + second)
    elif toward: lines.append(f'IMAGE 2 is an approved later frame of this same view ({STATE[toward]["name"]}). Its only job is to show which trees turn color first and where leaves collect on the ground. This frame comes long before it and looks much more like IMAGE 1.')
    lines += ['', 'KEEP the camera and framing, and the position, size and shape of everything that is not listed under CHANGE.', '', 'CHANGE these, and nothing else. This list is shared guidance written for many photographs of this property. An item applies only to things already visible in IMAGE 1. If something it mentions is not in IMAGE 1, skip that item: never add the thing, and never re-frame or re-compose the picture to include it.',
              f'- Leaves: {s["leaves"]}. Every trunk and branch stays where it is in IMAGE 1.',
              f'- Ground: {s["ground"]}.',
              f'- Sky, where sky is visible: {s["sky"]}.',
              f'- Light: {light(step, looks)} This replaces the lighting of IMAGE 1, including its shadows and sun patches.']
    if has_house:
        if 'roof' in s: lines.append(f'- Roof: {s["roof"]}.')
        lines.append('- Windows: ' + ('unlit, as in IMAGE 1.' if not s['lit'] else 'a faint soft-white glow from the lamps inside.' if s['lit'] == 'faint' else 'a gentle soft-white glow from the lamps inside, moderate, never blown out.'))
    if has_plants and s['plants'] != 'all':
        lines.append('- Deck plants: the potted plants are indoors' + (', and so are their stands' if s['plants'] == 'none' else '; their stands stay') + '. Show what was behind them.')
    lines += ['- ' + e for e in extra]
    lines += ['', 'Return one sharp, natural real-estate photograph, with any watermark unchanged.']
    return '\n'.join(lines)

if __name__ == '__main__':
    p = build(1, 225, toward=3, has_plants=True); print(p); print('\nwords:', len(p.split()))


# ---------------------------------------------------------------- interiors
LAMPS = {
 'soft': 'on, soft-white 3500K, neutral and not orange',
 'kitchen': 'on; the four track lights over the kitchen are daylight-balanced (about 5000K), the ceiling fans and dining fixture are soft-white 3500K',
 'bath': 'on, daylight-balanced (about 5000K), clean neutral white',
}
ROOM = {**{k: 'neutral with a slight warmth' for k in (1, 2, 3, 4)}, **{k: 'lamp-lit soft white, slightly warmer than by day' for k in (5, 6, 7, 8)}, **{k: 'clean and neutral' for k in (0, 9, 10, 11)}}

def daylight(step, faces, porch=False):
    """One sentence: what light comes in through the windows in view."""
    az, el = pilot.sun(step); off = abs((az - faces + 180) % 360 - 180)
    if el < -12: return 'none. It is night: the glass is near-black blue and faintly mirrors the lit room; just outside, snow or ground close to the windows is dimly lit by light spilling from them.'
    if el < 0: return 'only weak, cool twilight from the sky, which adds a faint diffuse coolness close to the glass and nothing more.'
    if off > 85: return 'soft, shadowless sky light only. The sun is on the other side of the house, so no direct sun enters and no sun patches appear.'
    if porch and el > 20: return 'soft reflected light only. A porch roof outside blocks the sun, so no sun patches appear.'
    kind = 'very low, warm and weak' if el < 8 else 'low and warm' if el < 20 else 'clear and slightly warm' if el < 35 else 'clear and neutral'
    return f'direct sun, {kind}, {max(el, 1)} degrees up, streaming in through these windows: soft-edged patches of sunlight on the floor and furniture in line with the panes, their length fitting that sun height.'

def build_interior(step, faces, lamps='soft', porch=False, prev=False, view_extra=''):
    s = STATE[step]
    lines = [f'Edit IMAGE 1, an interior photograph, so that it shows the same room at a different moment: {s["name"]}.', '',
             'IMAGE 1 is the photograph to edit. Its camera, framing, room and objects are the truth.']
    if prev and step in SINCE: lines.append(SINCE[step].replace('the ground changes visibly', 'the view outside changes visibly'))
    lines += ['', 'KEEP the camera and framing, and the position, size, shape, material and paint color of everything that is not listed under CHANGE.', '', 'CHANGE these, and nothing else. This list is shared guidance written for many photographs of this property. An item applies only to things already visible in IMAGE 1. If something it mentions is not in IMAGE 1, skip that item: never add the thing, and never re-frame or re-compose the picture to include it.',
              f'- View through the glass: the same trees, deck and terrain, at the same positions, now showing this moment. Leaves: {s["leaves"]}. Ground: {s["ground"]}. Sky: {s["sky"]}. {view_extra}It still looks photographed through real glass, with the softness of IMAGE 1.'.replace('  ', ' '),
              f'- Daylight entering: {daylight(step, faces, porch)} This replaces the daylight of IMAGE 1, including its sun patches and window glare.',
              f'- Lamps: {LAMPS[lamps]}, at the same color and brightness in every frame of the year.',
              f'- Room tone: {ROOM[step]}. Glossy surfaces (wood floor, glass, counters, steel) reflect whatever light the windows give; matte walls and ceilings take only broad, soft shading from it.',
              '- Exposure: as bright and airy as IMAGE 1, with light walls and open shadows; when it is dark outside the windows go dark, not the room.',
              '', 'Return one sharp, natural real-estate photograph, with any watermark unchanged.']
    return '\n'.join(lines)
