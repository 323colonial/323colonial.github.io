#!/usr/bin/env python3
"""colonial-66v pilot: Nano Banana 2.1 seasonal edits. Private working script; outputs stay under .pi/artifacts."""
import base64, datetime as dt, hashlib, json, math, os, subprocess, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from zoneinfo import ZoneInfo
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = str(Path(HERE).parents[1])
OUT = str(Path(os.environ.get('COLONIAL_SEASONS_WORK', f'{ROOT}/.pi/artifacts/seasons')).resolve())
if Path(OUT).is_relative_to(ROOT) and not Path(OUT).is_relative_to(Path(ROOT) / '.pi/artifacts'):
    raise ValueError('Season scratch must be outside the repository or under .pi/artifacts')
MODEL = 'gemini-nano-banana-2.1'
LAT, LON = 39.6265, -78.2272          # Berkeley Springs, WV
TZ = ZoneInfo('America/New_York')

# Hero schedule (colonial-29s v4): the year doubles as one day, noon -> evening -> dusk -> dawn -> morning.
STEPS = [  # step, hero file, name, local date/time, outdoor state
 (0, 'assets/listing/01.webp', 'late summer', (10, 2, 10, 0), 'The original photograph: mid-morning, harder clear light. Mature deep-green canopy, sparse dry lawn, clear blue sky.'),
 (1, 'assets/seasons/early-fall.webp', 'early fall', (9, 28, 16, 30), 'Late afternoon, light starting to warm. Canopy 90% green, 10% muted yellow, a few fallen leaves.'),
 (2, 'assets/seasons/turning-leaves.webp', 'turning leaves', (10, 14, 17, 15), 'Approaching golden hour. Canopy 65% green, 35% amber and russet, moderate scattered leaves, pale blue sky.'),
 (3, 'assets/seasons/fall.webp', 'fall', (10, 28, 17, 45), 'Golden evening at peak fall. Canopy mostly red, russet and gold with a little green, slightly thinned. Olive dormant grass with moderate fallen leaves, and green moss growing in the spots that are bare of grass.'),
 (4, 'assets/seasons/first-frost.webp', 'first frost', (11, 18, 17, 13), 'Mid-November dusk about twenty minutes after sunset, first frost. No direct sun. A soft peach-pink glow lingers low in the west-southwest under a deepening blue sky. About HALF of the leaves have fallen, so many bare branches show; the leaves that remain are muted brown and russet. A thin, patchy white frost lies on the roof, with most of the dark shingles still showing, and on the shaded ground, with a first thin trace of snow only in a few shaded strips. Fallen red and brown leaves lie thickly scattered over grass that is still partly green and olive. Clearly later and barer than peak fall.'),
 (5, 'assets/seasons/first-snow.webp', 'first light snow', (12, 10, 17, 34), 'Early December deep dusk about forty-five minutes after sunset, first LIGHT snow. No direct sun. Deep blue sky with a narrow fading peach band low in the west-southwest and the first stars. Branches mostly bare. Only a thin dusting on the ground: snow covers about 40% of it in connected patches, with dormant grass and leaf litter clearly showing through the other 60%. The roof is whiter than at first frost: an even light dusting of snow over every roof plane, with the shingle texture still faintly visible through it. Far less snow than midwinter.'),
 (6, 'assets/seasons/winter.webp', 'winter', (1, 15, 19, 12), 'Winter night two hours after sunset, under a new moon. No sun and no moon. Twilight has ended: the sky is a very dark blue-black filled with stars. Photographed as a professional long-exposure night real-estate photograph: snow is dimly visible by starlight in cool blue-grey, and warm soft-white light from windows and porch lights spills onto the porch, the nearby snow and the nearest tree trunks. The house, roofline, trees and ground remain legible; nothing is crushed to pure black. Snow blankets about 85% of the ground and roofs, a few inches deep, not deep drifts, with dormant grass and leaf litter showing at the margins. Bare branches with light snow tracery.'),
 (7, 'assets/seasons/snowmelt.webp', 'snowmelt', (2, 20, 6, 19), 'Late February deep pre-dawn about forty minutes before sunrise. No direct sun. The sky is a dim, muted, desaturated blue-grey, never a bright or saturated blue, with a faint peach tone low in the east and the last stars fading. Only a little brighter than night. Thaw: snow has melted back to about 60% cover in the same places as midwinter, exposing straw-brown dormant grass. Bare branches with tiny buds.'),
 (8, 'assets/seasons/new-growth.webp', 'new growth', (3, 20, 7, 4), 'Late March dawn about ten minutes before sunrise. No direct sun yet. Soft pink and peach light fills the lower sky toward the east under pale blue; the light on the ground is cool, soft and shadowless. Snow down to about 30% in shaded patches and on the roof in remnants. Straw and olive grass with small green shoots. Sparse buds on about 20% of the canopy.'),
 (9, 'assets/seasons/spring.webp', 'spring', (4, 15, 7, 45), 'Early spring golden morning. Low sun, soft long shadows. Small fresh light-green leaves at about 55% canopy density with branches visible, clearly spring green, never yellow or gold like autumn. Clear pale-blue morning sky. Muted fresh-green short grass with light dew.'),
 (10, 'assets/seasons/late-spring.webp', 'late spring', (5, 20, 8, 0), 'Morning golden hour ending, late spring. Canopy 85% fresh green and full. Fuller soft-green lawn.'),
 (11, 'assets/seasons/midsummer.webp', 'midsummer', (7, 10, 9, 15), 'Summer morning, light hardening toward the original. Mature deep-green full canopy, lawn starting to dry back, blue sky.'),
]

HALF = {  # extra frames for the special house exteriors, where snow and ground change fastest
 4.5: (4.5, None, 'late fall', (11, 29, 17, 22), 'Late November dusk about half an hour after sunset. No direct sun. A fading peach band low in the west-southwest under deep blue. About three quarters of the leaves are down, so the canopy is mostly bare branches with scattered brown leaves. The roof carries white frost, NOT snow, with the shingles still clearly visible through it; frost on the shaded ground is a little heavier than at first frost, with thin snow traces in shaded strips only. Fallen leaves lie thick over grass that is turning from green to olive.'),
 5.5: (5.5, None, 'early winter', (12, 28, 17, 58), 'Late December, late dusk about seventy minutes after sunset. No direct sun and no moon. The sky is dark blue with stars and only the faintest paler tone low in the west-southwest. Branches bare. Snow now covers about 65% of the ground in the same patches as the first light snow, grown and joined together, with grass and leaf litter still showing in the open middle. Roofs carry a thin, even white layer. Darker than first snow, not yet full night.'),
 6.5: (6.5, None, 'late winter', (2, 2, 6, 23), 'Early February, dark pre-dawn about fifty minutes before sunrise. No direct sun and no moon. The sky is dark blue with fading stars and the first faint paling low in the east. Snow covers about 75% of the ground and most of the roof, a few inches deep and beginning to thin at its edges. Bare branches. Only slightly brighter than full night.'),
 7.5: (7.5, None, 'thaw', (3, 5, 6, 14), 'Early March, dawn twilight about twenty-five minutes before sunrise. No direct sun. Soft blue-grey sky with a peach band low in the east. Snow has melted back to about 45% of the ground in the same shrinking patches, and lies on the roof only in broken areas. Exposed grass is straw-brown and damp. Bare branches with small buds.'),
 8.5: (8.5, None, 'early spring', (4, 2, 7, 6), 'Early April, the first minutes after sunrise. The sun is barely above the horizon: weak, warm, nearly horizontal light with very long soft shadows. Snow is down to about 10%, small remnants in deep shade, none on the roof. Grass is mixed straw, olive and new green. Buds and the first small leaves on about 35% of the canopy.'),
 9.5: (9.5, None, 'mid spring', (5, 2, 7, 44), 'Early May, golden morning easing toward full daylight. Snow is gone. Fresh light-green leaves at about 70% canopy density. Lawn a fuller soft green, still mixed and natural, with the last dew. Clear pale-blue sky.'),
}
def S(step): return HALF[step] if step in HALF else STEPS[int(step)]
def lab(step): return f'{int(step):02d}' + ('h' if step % 1 else '')

def hero_ref(step):
    for p in (f'{OUT}/review/img/01/{lab(step)}.webp', f'{OUT}/hero/{lab(step)}.png'):
        if os.path.exists(p): return p
    return f'{ROOT}/{S(step)[1]}'

def sun(step):
    m, d, h, mi = S(step)[3]
    t = dt.datetime(2026, m, d, h, mi, tzinfo=TZ).astimezone(dt.timezone.utc)
    n = (t - dt.datetime(2000, 1, 1, 12, tzinfo=dt.timezone.utc)).total_seconds() / 86400
    L = math.radians((280.46 + 0.9856474 * n) % 360); g = math.radians((357.528 + 0.9856003 * n) % 360)
    lam = L + math.radians(1.915) * math.sin(g) + math.radians(0.02) * math.sin(2 * g)
    eps = math.radians(23.439 - 0.0000004 * n)
    ra = math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam)); dec = math.asin(math.sin(eps) * math.sin(lam))
    gmst = (18.697374558 + 24.06570982441908 * n) % 24
    ha = math.radians((gmst * 15 + LON) % 360) - ra
    lat = math.radians(LAT)
    el = math.asin(math.sin(lat) * math.sin(dec) + math.cos(lat) * math.cos(dec) * math.cos(ha))
    az = math.atan2(-math.sin(ha), math.tan(dec) * math.cos(lat) - math.sin(lat) * math.cos(ha))
    return round(math.degrees(az) % 360), round(math.degrees(el))

def compass(az):
    return ['north', 'north-northeast', 'northeast', 'east-northeast', 'east', 'east-southeast', 'southeast', 'south-southeast', 'south',
            'south-southwest', 'southwest', 'west-southwest', 'west', 'west-northwest', 'northwest', 'north-northwest'][round(az / 22.5) % 16]

def sun_text(step):
    az, el = sun(step)
    if el < -1: return f'The sun has set or not yet risen (about {abs(el)} degrees below the horizon toward the {compass(az)}). There is no direct sunlight anywhere, only diffuse sky light, brightest low in the {compass(az)}.'
    if el < 12: return f'The sun is very low, about {max(el,0)} degrees above the horizon, in the {compass(az)}. Direct light is weak, warm and nearly horizontal.'
    return f'The sun is {el} degrees above the horizon in the {compass(az)}.'

LIGHTS = {
 'soft': 'All interior fixtures are switched ON and use soft-white 3500K lamps: a neutral soft white, not orange.',
 'kitchen': 'All interior fixtures are switched ON. The bar of four track lights above the kitchen uses daylight-balanced lamps (about 5000K, neutral white). The ceiling fans and the dining-table fixture use soft-white 3500K lamps. Both are on together, so kitchen work surfaces read neutral while the surrounding room reads slightly warmer.',
 'bath': 'All bathroom fixtures are switched ON and use daylight-balanced lamps (about 5000K): clean neutral white, not warm, not blue.',
}

PHOTOS = {  # position: facts. keys = steps generated for this photo.
 39: dict(faces=0, kind='exterior', aspect='3:2', keys=12, where='The front of the house, which faces NORTH, with the covered entry and attached garage. The camera looks roughly south toward it. This is the same face of the house shown in the SEASON REFERENCE.'),
 41: dict(faces=90, kind='exterior', aspect='3:2', keys=12, where='The EAST side of the house with the stone chimney, the tall great-room windows and the open deck. The camera looks roughly west toward it.'),
 11: dict(faces=315, kind='exterior', aspect='3:2', keys=18, where='The house seen from the gravel driveway at its north-west corner: the NORTH-facing front with the entry porch on the left and the WEST gable end with the two garage doors nearest the camera. The camera looks roughly south-east. The small wooden well cover beside the driveway is a permanent fixture and stays in every frame.'),
 26: dict(faces=45, kind='exterior', aspect='3:2', keys=18, where='A three-quarter view of the house through the trees from the north-east: the EAST-side deck on the left and the NORTH-facing front porch on the right. The camera looks roughly south-west from well back among the trees, so tree trunks and foliage in the foreground partly hide the house. This is a DIFFERENT, more distant camera position than the season reference: keep the composition of IMAGE 1 exactly and never move closer to the house.'),
 28: dict(faces=135, kind='exterior', aspect='4:3', keys=18, where='A low aerial view of the house from the south-east, taken in 2008: the EAST wall with the stone chimney and open deck faces the camera, and the screened porch runs along the SOUTH side on the left. The drone looks roughly north-west and down. IMAGE 1 was photographed in late fall under cloud, with bare trees and bright green moss on the ground. Keep its 2008 state exactly, including the empty deck. For seasons when trees are in leaf, grow foliage on the existing bare branches without moving any trunk or branch.'),
 29: dict(looks=90, kind='outlook', aspect='3:2', keys=12, open=True, where='The open EAST-side deck. The camera stands on the deck and looks EAST over the railing to the woods and sky. The house is behind the camera.'),
 4:  dict(looks=100, kind='outlook', aspect='3:2', keys=12, where='The covered, screened back porch with the swinging daybed, on the SOUTH side of the house. The camera looks EAST along the length of the porch, with the house wall on its left and the open screened side, which faces SOUTH, on its right. The woods are seen to the south and southeast through the insect screens. The porch has a cedar ceiling with recessed lights and is fully roofed, so rain and snow never fall on its floor or furniture.'),
 67: dict(looks=90, kind='outlook', aspect='3:2', keys=12, ground=True, where='The gravel path through the woods to the stone firepit, east of the house. The camera looks EAST along the path. No building is in view. A small fire burns in the firepit in every frame.'),
 23: dict(faces=270, kind='interior', aspect='3:2', keys=4, lights='soft', where='The upstairs guest bedroom under the sloped roof. The large window behind the bed faces WEST. The smaller dormer window on the right-hand wall faces NORTH and never receives direct sun.'),
 36: dict(faces=180, porch=True, kind='interior', aspect='3:2', keys=4, lights='bath', where='The main-level half bath. Its window faces SOUTH into the covered screened porch, so the view is of the porch ceiling, posts and the woods beyond the screens, and direct sun rarely reaches it.'),
 2:  dict(faces=90, kind='interior', aspect='3:2', keys=12, lights='soft', where='The great room. The camera looks EAST toward the tall east-facing windows and glass doors around the stone hearth. The open deck and woods are outside that glass.'),
 14: dict(faces=180, porch=True, kind='interior', aspect='4:3', keys=12, lights='soft', where='The dining area. Its glass door and windows face SOUTH and open onto the covered screened porch, so the woods are seen through the porch and its screens.'),
 18: dict(faces=0, kind='interior', aspect='3:2', keys=4, lights='soft', where='The main-floor primary bedroom with blue walls. Its one window faces NORTH, so it never receives direct sun, only sky light and the view of trees.'),
 5:  dict(faces=180, porch=True, kind='interior', aspect='3:2', keys=4, lights='kitchen', where='The kitchen. The small window over the counter faces SOUTH onto the covered screened porch, so little direct sun reaches it. The stainless-steel refrigerator door directly faces the tall EAST-facing great-room windows across the room, out of frame behind the camera. Its brushed steel therefore carries a soft, blurred, vertical reflection of those windows: brighter and slightly warm when morning sun is in the east, neutral by day, dim deep blue at twilight.'),
 55: dict(kind='interior', aspect='3:2', keys=1, lights='bath', nowindow=True, where='The main-level primary bathroom. It has NO window and no daylight at all.'),
}

LOCK = ('Edit IMAGE 1, an actual real-estate photograph. This is a precise photo retouch for one frame of a camera-locked annual timelapse, NOT a new composition. '
 'IMAGE 1 is the exact structural master. Treat it as a locked pixel canvas: every physical edge stays at its input coordinate. Keep the same camera, perspective, framing, crop and aspect ratio. '
 'Keep every wall, ceiling, floorboard, beam, window frame, pane and mullion, door, trim, cabinet, counter, fixture, appliance, piece of furniture, rug, artwork and object exactly where it is, the same size and shape, with the same materials and paint colors. '
 'Outdoors keep every roofline, chimney, dormer, siding board, stone, post, railing, path, tree trunk and main branch in place. Do not add, remove or move anything. Do not zoom, rotate, crop or warp. No text, borders, people or animals. Keep the small watermark in the lower-left corner unchanged. '
 'Return ONE sharp, full-frame, photorealistic photograph. ')

GROUND = {k: '\n\nGROUND: wherever IMAGE 1 shows bare dirt or thin patchy grass, including around the stone retaining wall, beside paths and under the trees, forest moss grows naturally on the patches of forest floor, dense in between the existing patches of grass, with scattered fallen leaves lying on top.' for k in (2, 3, 4)}
GROUND.update({k: '\n\nROOF SNOW: snow lies on every roof plane and dormer roof as in the season reference: a continuous soft, thick layer with gently rounded edges at the eaves, not a thin crisp white coating.' for k in (5, 6, 7)})
_LIT = 'WINDOWS: the lamps inside are on and each window shows the lit room inside through clear glass: a gentle soft-white 3500K glow of moderate brightness, a little dimmer and less warm than a typical cozy-cabin render. Not yellow, not orange, no flare, no glossy mirror-like reflections on the glass, never blown out. '
WINDOWS = {k: _LIT for k in range(3, 10)}
WINDOWS.update({k: 'WINDOWS: full daylight. No interior glow is noticeable. The glass looks as it does in IMAGE 1, showing only faint reflections of the trees in their current seasonal state.' for k in (0, 1, 11)})
WINDOWS.update({k: 'WINDOWS: the lamps inside are on but daylight is still strong, so each window shows only a faint soft-white glow, about half as noticeable as at dusk.' for k in (2, 10)})
TONE = {k: ' Overall the room balance is neutral with only a slight warmth, because warm evening light outside is offset by the lamps.' for k in (1, 2, 3, 4)}
TONE.update({k: ' With so little daylight left, the lamps dominate: the room reads as comfortable soft white, slightly WARMER than in daytime frames. Cool twilight from the glass adds only a faint, very diffuse coolness close to the windows. Ceilings and walls must NOT show a blue glow or blue patches.' for k in (5, 6, 7, 8)})
TONE.update({k: ' Overall the room balance is clean and neutral.' for k in (0, 9, 10, 11)})
TONE[6] += ' It is full night outside: the glass is nearly black-blue and faintly mirrors the lit room, and just beyond it the snow on the deck, railings and nearest branches is dimly lit by light spilling from the windows. No daylight enters.'

def direct(pos, step):
    """Plain statement of whether direct sun reaches the face or glass in view."""
    p = PHOTOS[pos]; az, el = sun(step); off = abs((az - p['faces'] + 180) % 360 - 180)
    side = 'wall and windows in view' if p['kind'] == 'exterior' else 'windows in view'
    if el < 0: return f'No direct sun reaches the {side}. Outdoor light is dim, even and cool.'
    if off > 85: return (f'The sun is on the opposite side of the house from the {side}, so they are in open shade and receive NO direct sun. '
        + ('The house front is evenly shaded while low sun rakes across the yard and treetops from the side.' if p['kind'] == 'exterior' else
           'The room gets only soft, neutral-to-cool sky light from them. The trees outside are lit from behind the house, so only their tops and far sides catch warm light. The room must NOT turn orange or peach.'))
    if p.get('porch') and el > 20: return f'The sun is on this side but the porch roof blocks it, so NO direct sun reaches the {side}. Light entering is soft and reflected.'
    return (f'The sun shines directly onto the {side}' + ('.' if p['kind'] == 'exterior' else
        f', {max(el,1)} degrees above the horizon, so sunlight streams into the room: put clear but soft-edged patches of sunlight on the floor and furniture in line with the windows, with length that fits that sun height.'))

def bearing(looks, az):
    """Where the sun (or the twilight glow) sits relative to the camera's view direction."""
    rel = (az - looks + 180) % 360 - 180
    if abs(rel) <= 45: return 'in view, ahead of the camera', True
    if abs(rel) >= 160: return 'directly behind the camera', False
    side = 'right' if rel > 0 else 'left'
    return (f'out of frame to the {side}' if abs(rel) < 90 else f'out of frame, behind the camera to the {side}'), False

def sky_text(looks, step):
    az, el = sun(step); where, visible = bearing(looks, az)
    if el < 0:
        return (f'The twilight glow where the sun went down or will rise is {where}. ' + ('The sky in view is the brighter part, palest near the horizon.' if visible else
                'It is NOT in view. The sky in view is the darker side: an even, deeper blue with no bright or orange band at the horizon.'))
    if visible: return f'The sun is {where}, {max(el, 1)} degrees above the horizon.'
    return (f'The sun is {where}. The sun disk, its glare and any bright orange or yellow glow at the horizon must NOT appear anywhere in this picture. '
            'The sky in view is the side away from the sun: clear soft blue, at most with a few clouds faintly tinted pink. Do NOT copy the sunset sky of the season reference, which faces a different direction.')

def same_sky(p, step):
    """True when this camera looks toward the same part of the sky as the hero reference does."""
    if p['kind'] != 'exterior': return False
    cam = (p['faces'] + 180) % 360
    return abs((sun(step)[0] - cam + 180) % 360 - 180) <= 75

def outlook(pos, step):
    p = PHOTOS[pos]; az, el = sun(step); where, visible = bearing(p['looks'], az)
    if el < 0: light = 'No direct sun. The woods are in dim, even twilight.'
    elif visible: light = 'The trees are backlit with glowing edges and long shadows reach toward the camera.'
    elif 'behind' in where: light = 'Low warm sunlight comes from behind the camera, so trunks and crowns in view are front-lit and warm, while the deck or porch nearest the house lies in the house shadow. Shadows point away from the camera.'
    else: light = f'Low sunlight rakes across the scene from the {"right" if "right" in where else "left"}, so shadows of posts, rails and trees fall toward the {"left" if "right" in where else "right"}.'
    light = sky_text(p['looks'], step) + ' ' + light
    if p.get('ground'):
        cover = (' Snow covers the path, the ground and the top of the firepit stones in the same amount as the season reference, melted back in a ring close to the fire.' if int(step) in (5, 6, 7) else '') + ' The fire stays lit, the same size, and at twilight its warm light falls on the nearest stones and ground.'
    elif p.get('open'):
        cover = (' Snow lies on the open deck boards, on top of the railings and on any hot-tub cover and furniture, in the same amount as the ground in the season reference.' if int(step) in (5, 6, 7) else '') + (' A few fallen leaves lie on the deck boards.' if int(step) in (2, 3, 4) else '')
    else:
        cover = ' Nothing falls on the porch floor or furniture: no snow, no wet boards. Only the view beyond the screens changes, softened by the mesh exactly as in IMAGE 1. The recessed porch-ceiling lights are ON with soft-white 3500K lamps at the same brightness in every frame; as daylight fades they light the cedar ceiling, boards and daybed more noticeably.'
    return light + cover

PLANTS = {k: ' SEASONAL EXCEPTION to the rule against removing objects: the outdoor potted plants have been taken indoors for the cold months. Remove each outdoor potted plant together with its pot. Leave any dedicated plant stand in place, empty, and show what was behind the plant, continued naturally. Leave all other furniture. Remove nothing else.' for k in (2, 3, 8, 9)}
PLANTS.update({k: ' SEASONAL EXCEPTION to the rule against removing objects: outdoor potted plants and their dedicated plant stands are stored indoors for winter. Remove every outdoor potted plant with its pot and its stand, and show the boards, railing or ground behind them, continued naturally. Leave all other furniture. Remove nothing else.' for k in (4, 5, 6, 7)})

SHADOWS = ' BAKED LIGHT: IMAGE 1 was photographed in hard mid-morning sun. Its cast shadows and bright sunlit patches, on the roof, the walls, the deck and the ground, belong only to that moment. Do not carry them into this frame. Remove every hard shadow edge and sun patch that IMAGE 1 shows, including the dark shadowed band and lighter sunlit area on the roof, so each surface has one even tone, then light the scene only as this frame describes. A shadow may appear only where the sun position given for this frame would cast it.'

def prompt(pos, step, nrefs):
    p = PHOTOS[pos]; _, _, name, _, outdoor = S(step)
    s = LOCK + f'\n\nSCENE: {p["where"]} The house is in wooded mountains at Berkeley Springs, West Virginia (latitude 39.6 N).'
    if p.get('nowindow'):
        s += f'\n\nLIGHT: {LIGHTS[p["lights"]]} Rebalance the color of the light in the room to that target. Keep natural exposure, true material colors for tile, wood, stone and paint, clean unclipped whites, and realistic soft shadows from the existing fixtures. Do not change anything else.'
        return s
    s += f'\n\nSEASON AND TIME: Frame {step} on a 12-step year, "{name}". {outdoor} {sun_text(step)}'
    if p['kind'] != 'outlook': s += ' ' + direct(pos, step)
    if nrefs: s += ' IMAGE 2 is the SEASON REFERENCE: an approved frame of the same property at this exact season and time, from a different camera. Match its foliage color and density, ground cover, snow or frost amount, and overall outdoor light closely.' + (' Match its sky too, including its clouds and any pink or peach light.' if same_sky(p, step) else ' Its camera faces south-southwest, so its sky applies only to that direction.') + ' Natural real-estate photography: no golden haze, no oversaturated leaves. Use it for appearance only. Never copy its composition, camera position, framing or objects: the output must be the exact view of IMAGE 1.'
    if nrefs > 1: s += ' IMAGE 3 and IMAGE 4 are the approved frames of this same photograph just BEFORE and just AFTER this one in the year. Use them for continuity: the same trees turn, the same patches of snow grow or shrink, the same places stay bare. But the STATE of this frame, meaning how many leaves remain, how much snow lies and where, and how bright and warm the light is, must match IMAGE 2, the season reference for this exact step, and the description above. Do not simply copy either neighbor. Take the structure from IMAGE 1.'
    if p['kind'] in ('outlook', 'exterior'): s += PLANTS.get(int(step), '')
    if p['kind'] in ('outlook', 'exterior') and step != 0: s += SHADOWS
    if p['kind'] == 'outlook':
        s += ' ' + outlook(pos, step) + ('\n\nCHANGE ONLY: the foliage, ground, snow or frost and sky of the woods beyond, and the direction, height, color and softness of the light, as described. Keep every board, rail, post, screen frame, chain, cushion and piece of furniture exactly in place with its true colors' + ('.' if int(step) in PLANTS else ', and every plant pot too.') + ' Expose like a professional real-estate photographer: never underexposed, even at twilight.')
    elif p['kind'] == 'exterior':
        if not same_sky(p, step): s += ' ' + sky_text((p['faces'] + 180) % 360, step)
        s += (GROUND.get(int(step), '') + '\n\nCHANGE ONLY: foliage, ground cover, snow or frost, sky, and the direction, height, color and softness of sunlight and shadows, worked out from the compass facts above. '
              'Shadows must fall consistently with that sun position on the house, ground and trees. ' + WINDOWS[int(step)] + ' HOUSE COLOR: the cedar siding, stonework, trim and roof must show the same hue, saturation and brightness as the same house in the season reference at this step, a rich red-brown cedar. Do not let the house turn darker, browner or duller than the reference, even where it is in shade.')
    else:
        s += (f'\n\nINTERIOR LIGHT: {LIGHTS[p["lights"]]}'
              ' These fixtures have exactly the same color and brightness in every frame of the year. Only the daylight changes.'
              '\n\nCHANGE ONLY: (1) the view through every window and glass door, which must show this season, time and weather on exactly the same trees, trunks, branches, deck, porch and terrain that IMAGE 1 shows, at the same positions. Do not add or move any branch. The view must still look photographed through real glass, with the same soft focus, slight haze and reflections as IMAGE 1, never a crisp pasted picture; '
              '(2) the light in the room. Work out physically how daylight from the windows mixes with the fixtures given the compass facts: where direct sun can enter it makes warm or neutral patches with correct direction and soft edges; '
              'where only sky light enters it is cooler and weaker; as outdoor light fades the fixtures dominate and the room reads soft white while the glass reads darker and bluer. '
              'Glossy surfaces such as the wood floor, glass, counters and stainless steel show reflections of the window light. Matte painted walls and ceilings show only broad, soft, gradual shading from it, never a colored glow, halo or patchy tint. '
              + TONE[int(step)] +
              ' EXPOSURE: expose like a professional real-estate photographer. In every frame the room is as bright and airy as IMAGE 1, with light walls and ceilings and open shadows. Never underexposed, even at twilight; let the windows go darker instead. Do not deepen or emphasize shadows on the walls. '
              'Keep true material and paint colors, natural exposure and clean unclipped whites. No overall orange or blue filter.')
    return s

def call(parts, aspect, tries=3):
    body = {'contents': [{'role': 'user', 'parts': parts}], 'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': aspect, 'imageSize': '2K'}}}
    req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent', data=json.dumps(body).encode(),
        headers={'x-goog-api-key': os.environ['GEMINI_API_KEY'], 'Content-Type': 'application/json'})
    for i in range(tries):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=300))
            for c in r.get('candidates', []):
                for part in c.get('content', {}).get('parts', []):
                    if 'inlineData' in part: return base64.b64decode(part['inlineData']['data']), r.get('usageMetadata', {})
            err = json.dumps(r)[:300]
        except urllib.error.HTTPError as e: err = f'HTTP {e.code} {e.read().decode()[:300]}'
        except Exception as e: err = repr(e)
        time.sleep(5 * (i + 1))
    raise RuntimeError(err)

CANVAS = {'3:2': '2528x1696', '4:3': '2400x1792', '16:9': '2752x1536'}

def align_twice(master, stem):
    first = subprocess.run((sys.executable, f'{HERE}/align.py', master, stem + '-full.png', stem + '-a.png'), capture_output=True, text=True).stdout.strip()
    second = subprocess.run((sys.executable, f'{HERE}/align.py', master, stem + '-a.png', stem + '.png'), capture_output=True, text=True).stdout.strip()
    os.remove(stem + '-a.png')
    return first, second

def img_part(path, fit=None):
    # fit: scale the master to the model's exact canvas shape so the model has nothing to crop
    data = subprocess.run(['magick', path] + (['-filter', 'Lanczos', '-resize', fit + '!'] if fit else []) + ['-quality', '93', 'jpg:-'], check=True, capture_output=True).stdout
    return {'inlineData': {'mimeType': 'image/jpeg', 'data': base64.b64encode(data).decode()}}

MOSS = ' The LAST image is a real photograph of this property\'s own ground in late fall. It shows the bright green moss that grows here in broad soft carpets between the patches of grass and across the forest floor. Reproduce that moss, with that color and coverage, on the open ground of IMAGE 1 wherever grass is thin or soil is bare. Take nothing else from it: not its trees, buildings, sky or composition.'

def generate(pos, step, tag, extra_refs=()):
    if not tag or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in tag):
        raise ValueError('Tag must contain only letters, digits, hyphens or underscores')
    if not Path(OUT, tag, f'{pos:02d}').resolve().is_relative_to(OUT):
        raise ValueError('Generation output escapes scratch directory')
    master = f'{ROOT}/assets/listing/{pos:02d}.webp'
    p = PHOTOS[pos]
    refs = [] if (p.get('nowindow') or os.environ.get('NOSEASONREF')) else [hero_ref(step)] + list(extra_refs)
    text = prompt(pos, step, len(refs))
    if p['kind'] in ('exterior', 'outlook') and int(step) in (2, 3, 4): refs.append(f'{OUT}/refs/moss-ref.png'); text += MOSS
    d = f'{OUT}/{tag}/{pos:02d}'; os.makedirs(d, exist_ok=True)
    raw, usage = call([{'text': text}, img_part(master, CANVAS[p['aspect']])] + [img_part(r) for r in refs], p['aspect'])
    rawp = f'{d}/{lab(step)}-raw.jpg'; open(rawp, 'wb').write(raw)
    w, h = subprocess.run(['magick', 'identify', '-format', '%w %h', master], capture_output=True, text=True).stdout.split()
    outp = f'{d}/{lab(step)}.png'
    subprocess.run(['magick', rawp, '-resize', f'{w}x{h}!', outp], check=True)   # model fits the frame to its canvas; undo that
    json.dump({'position': pos, 'step': step, 'model': MODEL, 'prompt': text, 'refs': [os.path.relpath(r, ROOT) for r in refs],
               'master': os.path.relpath(master, ROOT), 'master_sha256': hashlib.sha256(open(master, 'rb').read()).hexdigest(),
               'raw_sha256': hashlib.sha256(raw).hexdigest(), 'usage': usage, 'generated': dt.datetime.now().isoformat(timespec='seconds')},
              open(f'{d}/{lab(step)}.json', 'w'), indent=1)
    return pos, step, usage.get('totalTokenCount')

def neighbors(pos, step):
    if step % 1: lo, hi = int(step), (int(step) + 1) % 12
    else: lo, hi = (int(step) // 3) * 3, ((int(step) // 3) * 3 + 3) % 12
    return [f'{OUT}/review/img/{pos:02d}/{lab(k)}.webp' for k in (lo, hi)]

if __name__ == '__main__':
    if sys.argv[1] == 'sun':
        for s in STEPS: print(s[0], s[2], '%02d-%02d %02d:%02d' % s[3], sun(s[0]), '|', sun_text(s[0]))
    else:
        tag = sys.argv[1]; jobs = [(int(a.split(':')[0]), float(a.split(':')[1]) if '.' in a else int(a.split(':')[1])) for a in sys.argv[2:]]
        with ThreadPoolExecutor(10) as ex:
            for f in [ex.submit(generate, pos, step, tag, neighbors(pos, step) if tag.startswith('mid') else ()) for pos, step in jobs]:
                try: print('ok', f.result())
                except Exception as e: print('FAIL', e)
