#!/usr/bin/env bash
# Gather the walkthrough's source textures into a work directory:
#   scripts/walkthrough/prepare.sh WORK_DIR
# - CC0 materials and the sky from Poly Haven (https://polyhaven.com, CC0)
# - surfaces cut straight from the listing photographs in assets/listing/
# - a few generated fills (granite, carpet, fabric, lattice)
# Needs curl, python3 and ImageMagick 7 (magick).
set -euo pipefail
work=${1:?work directory}
root=$(cd "$(dirname "$0")/../.." && pwd)
src=$work/src
T=$work/textures
L=$root/assets/listing
mkdir -p "$src" "$T"

python3 - "$src" <<'PY'
import json, os, sys, urllib.request
src = sys.argv[1]
UA = {"User-Agent": "323-colonial-walkthrough/1.0"}
def get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return
    open(path, "wb").write(urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read())
def files(asset):
    return json.load(urllib.request.urlopen(urllib.request.Request("https://api.polyhaven.com/files/" + asset, headers=UA)))
for t in ["wood_floor_worn", "rustic_stone_wall", "weathered_plank_siding", "roof_slates_02", "interior_tiles",
          "wood_floor_deck", "leafy_grass", "forest_leaves_02", "gravel_floor", "oak_veneer_01", "bark_brown_02"]:
    get(files(t)["Diffuse"]["2k"]["jpg"]["url"], os.path.join(src, t + "_diff.jpg"))
f = files("park_parking")
get(f["hdri"]["4k"]["hdr"]["url"], os.path.join(src, "park_parking_4k.hdr"))
get(f["tonemapped"]["url"], os.path.join(src, "park_parking_tm.jpg"))
PY

cp "$src/park_parking_4k.hdr" "$work/sky.hdr"
cp "$src/park_parking_tm.jpg" "$work/sky_tonemapped.jpg"
for f in "$src"/*_diff.jpg; do
  magick "$f" -resize 1024x1024 -quality 88 "$T/$(basename "$f" _diff.jpg).jpg"
done
uv run --quiet --python 3.12 --with numpy --with pillow python "$root/scripts/walkthrough/oakfloor.py" "$T/oakfloor.jpg"

# --- from the listing photographs (pixel boxes read off the published frames) ---
magick "$L/13.webp" -crop 469x327+404+340 +repage -resize 1024x "$T/fireplace.jpg"      # stone surround, photo 13
magick "$L/13.webp" -crop 80x60+587+573 +repage -resize 256x "$T/fire.jpg"               # stove glass
magick "$L/59.webp" -crop 217x167+603+495 +repage -resize 512x "$T/art_bird.jpg"         # painting, photo 59
magick "$L/45.webp" -crop 96x66+836+430 +repage -resize 384x "$T/art_roots.jpg"          # print, photo 45
magick "$L/45.webp" -crop 78x38+468+430 +repage -resize 384x "$T/art_leaf.jpg"           # leaf panel, photo 45
magick "$L/40.webp" -crop 118x238+649+458 +repage -resize 256x "$T/frontdoor_out.jpg"    # front door, photo 40
magick "$L/11.webp" -crop 191x142+816+484 +repage -resize 512x "$T/garagedoor.jpg"       # garage door, photo 11
magick "$L/21.webp" -virtual-pixel edge -distort Perspective \
  '859,309 0,0  1230,275 512,0  1230,647 512,640  859,572 0,640' -crop 512x640+0+0 +repage "$T/oakdoors2.jpg"   # closet doors, photo 21
magick "$T/oakdoors2.jpg" -crop 256x640+0+0 +repage "$T/oakdoor.jpg"
magick "$L/49.webp" -crop 176x363+1102+342 +repage -resize 256x "$T/halfglass_in.jpg"    # porch door, photo 49
magick "$T/halfglass_in.jpg" -fill '#5c6b5e' -colorize 55 "$T/halfglass_out.jpg"

# --- kitchen and wall-art patches, squared up from the listing photographs ---
# south kitchen wall, photo 48 (taken square-on): plain crops
magick "$L/48.webp" -crop 778x221+252+617 +repage \( +clone -crop 74x178+79+43 +repage -flop \) -geometry +5+43 -composite -resize 1024x "$T/kit_s_base.jpg"   # island corner in the shot is painted out with the mirrored half of the same door
magick "$L/48.webp" -crop 690x193+303+290 +repage -resize 1024x "$T/kit_s_upper.jpg"
magick "$L/48.webp" -crop 784x109+350+483 +repage -resize 1024x "$T/kit_s_splash.jpg"
# west kitchen wall, photo 15 (oblique): four-corner rectification of each flat front
rect() { # out W H  x1,y1 x2,y2 x3,y3 x4,y4  (TL TR BR BL in the photo)
  magick "$L/15.webp" -virtual-pixel edge -distort Perspective "$4 0,0  $5 $2,0  $6 $2,$3  $7 0,$3" -crop "$2x$3+0+0" +repage "$T/$1.jpg"
}
rect kit_fridge 384 746  799.2,334.8 1022.3,333.7 1022.3,730.1 811.9,730.1
rect kit_range  512 478  573.8,519.7 736.1,519.7 735,713.5 575,713.5
rect kit_w_upper 640 418  560,286.6 777,285.5 777,429.5 560,430.5
rect kit_w_fridgetop 512 174  799.2,266.1 987.5,265 987.5,332.6 799.2,332.6
rect kit_w_base 160 320  737.2,530.8 795.3,530.8 795.3,689.7 737.2,689.7
# island cabinet faces, photo 35 (taken from the hall): end panel, trash pull-out, the two door fronts
rect35() { magick "$L/35.webp" -virtual-pixel edge -distort Perspective "$4 0,0  $5 $2,0  $6 $2,$3  $7 0,$3" -crop "$2x$3+0+0" +repage "$T/$1.jpg"; }
rect35 isl_a 400 464  425,644 538,678 538,949.5 425,891.5
rect35 isl_b 256 440  539,678 634,653 634,876.5 539,939
rect35 isl_c 288 464  640,650 806.5,646.5 806.5,869 640,875
rect35 isl_d 224 464  812.5,648 890,656.5 890,900 812.5,869
# primary bath, photos 56 and 55: tile wainscot with its accent band, towel shelf, medicine cabinet
magick "$L/56.webp" -crop 324x209+842+482 +repage -resize 512x "$T/bath_wainscot.jpg"
magick "$L/55.webp" -crop 172x164+421+272 +repage -resize 256x "$T/bath_shelf.jpg"
magick "$L/55.webp" -crop 112x174+636+286 +repage -resize 192x "$T/bath_cabinet.jpg"
# square floor tile, as in the baths and mudroom: four 12 in. tiles to the repeat
magick -size 512x512 xc:'#d9cfbf' -seed 4 +noise Gaussian -blur 0x3 -modulate 100,40,100 -fill none -stroke '#b9ad9b' -strokewidth 5 \
  -draw "line 0,0 512,0 line 0,128 512,128 line 0,256 512,256 line 0,384 512,384 line 0,0 0,512 line 128,0 128,512 line 256,0 256,512 line 384,0 384,512" "$T/floortile.jpg"
# primary bedroom: the duvet's damask (photo 37) and the print over the bed (photo 18)
magick "$L/37.webp" -crop 331x202+648+698 +repage -resize 512x512! "$T/bedding.jpg"
# wall art
magick "$L/45.webp" -crop 52x116+968+411 +repage -resize 208x "$T/art_banjos.jpg"   # banjos and violin, photo 45
magick "$L/46.webp" -crop 52x56+672+302 +repage -resize 256x "$T/art_metal.png"
magick "$L/35.webp" -crop 76x70+1215+381 +repage -resize 256x "$T/art_frame.jpg"

# originals of three artworks, from the links the owner supplied (the artists' own images; see docs)
art() { curl -sL -m 40 -A "Mozilla/5.0 (Macintosh) AppleWebKit/605.1.15 Safari/605.1.15" -o "$src/$1" "$2"; }
art neuro.jpg https://www.gregadunn.com/wp-content/uploads/2025/06/Neurogenesis-I-2025-remaster.jpg
art makie.jpg https://www.gregadunn.com/wp-content/uploads/2012/05/Maki-e-Neurons.jpg
art bird.jpg "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.myikona.gr%2Fwp-content%2Fuploads%2F2020%2F11%2Fpinakas-se-kamva-orizontios-saloni-d-03500-oil-painting-of-blue-cerulean-warbler-song-bird.jpg&f=1&nofb=1"
magick "$src/neuro.jpg" -crop 1200x760+0+40 +repage -resize 1024x "$T/art_blue.jpg"
magick "$src/makie.jpg" -resize 1024x "$T/art_roots.jpg"
magick "$src/bird.jpg" -crop 866x590+106+110 +repage "$T/art_bird.jpg"
# the door crop has a knob printed on it; the model adds real levers, so paint it out
magick "$T/oakdoors2.jpg" -crop 256x640+0+0 +repage \( +clone -crop 44x70+212+222 +repage \) -geometry +212+295 -composite "$T/oakdoor.jpg"   # the stile just above it, copied down

# --- generated ---
magick -size 256x512 xc:'#f1efe9' -fill '#e4e1da' -draw "rectangle 30,330 226,480" \
  -fill '#b9c4c4' -stroke '#8d8a80' -strokewidth 5 -draw "ellipse 128,170 52,110 0,360" "$T/frontdoor_in.jpg"
magick -size 512x512 xc:gray50 -seed 7 +noise Random -colorspace Gray -blur 0x1.2 -auto-level -sigmoidal-contrast 9,48% \
  \( -size 512x512 xc:gray50 -seed 3 +noise Random -colorspace Gray -blur 0x4 -auto-level \) -compose Multiply -composite \
  -auto-level -level 0%,100%,0.8 +level-colors '#3b3531','#d6cdc0' "$T/granite.jpg"
magick -size 512x512 xc:gray50 -seed 11 +noise Random -colorspace Gray -blur 0x0.7 -auto-level -level 20%,80% \
  +level-colors '#b3a089','#d8c9b3' "$T/carpet.jpg"
magick -size 256x256 xc:gray50 -seed 5 +noise Random -colorspace Gray -motion-blur 0x2+0 -auto-level -level 15%,85% \
  +level-colors '#d9d9d9','#ffffff' "$T/fabric.jpg"
magick -size 256x256 xc:none -fill '#55201a' -draw "stroke #55201a stroke-width 22 line 0,0 256,256 line -128,128 128,384 line 128,-128 384,128 line 0,256 256,0 line -128,128 128,-128 line 128,384 384,128" "$T/lattice.png"

# fine vertical brushing for stainless steel
magick -size 256x256 xc:gray50 -seed 21 +noise Random -colorspace Gray -motion-blur 0x40+90 -auto-level -level 30%,70% +level-colors '#f1f1f1','#ffffff' "$T/brushed.jpg"

# --- tree canopy card: the maple in the sky photograph, keyed off the blue sky ---
magick "$src/park_parking_tm.jpg" -crop 2010x1060+1885+450 +repage -resize 1024x "$work/crown.png"
magick "$work/crown.png" \( +clone -fx "(b-max(r,g))>0.015 || (r+g+b)/3>0.78 ? 0 : 1" -blur 0x0.7 -level 40%,60% \) \
  -alpha off -compose CopyOpacity -composite "$work/crown_keyed.png"
magick "$work/crown_keyed.png" -alpha extract \( -size 1024x540 radial-gradient:white-black -level 25%,62% \) \
  -compose Multiply -composite "$work/crown_alpha.png"
magick "$work/crown_keyed.png" -alpha off "$work/crown_alpha.png" -compose CopyOpacity -composite "$T/canopy.png"
ls "$T"
