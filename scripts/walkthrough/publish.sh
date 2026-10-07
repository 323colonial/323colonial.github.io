#!/usr/bin/env bash
# Assemble local web assets, not a remote deployment. Never serve a half-converted bundle.
#   scripts/walkthrough/publish.sh WORK_DIR
set -euo pipefail
work=${1:?work directory}
root=$(cd "$(dirname "$0")/../.." && pwd)
out=$root/assets/walkthrough
mkdir -p "$root/assets"
stage=$(mktemp -d "$root/assets/.walkthrough-stage.XXXXXX")
# Stage contains only files this invocation creates. Previous bundle is retained for recovery.
trap 'rm -rf "$stage"' EXIT
mkdir "$stage/tex"
cp "$work/out/house.glb" "$work/out/scene.json" "$stage/"
python3 - "$stage/scene.json" > "$stage/inputs" <<'PY'
import json, re, sys
scene = json.load(open(sys.argv[1]))
inputs = [('tex', t) for t in sorted({m['tex'] for m in scene['materials'].values() if m.get('tex')})]
if scene.get('baked', True):
    inputs += [('lm', p) for p in scene['pages']]
    inputs += [('photo', p) for p in scene.get('photoPages', [])]
for kind, name in inputs:
    if not re.fullmatch(r'[A-Za-z0-9_-]+', name):
        raise ValueError('Unsafe asset name: ' + repr(name))
    print(kind, name)
print('baked', int(scene.get('baked', True)))
PY
while read -r kind name; do
  case "$kind" in
    tex)
      if [ -f "$work/textures/$name.png" ]; then
        magick "$work/textures/$name.png" -resize '1024x1024>' -quality 88 -define webp:alpha-quality=90 "$stage/tex/$name.webp"
      elif [ -f "$work/textures/$name.jpg" ]; then
        magick "$work/textures/$name.jpg" -resize '2048x2048>' -quality 84 "$stage/tex/$name.webp"
      else
        echo "missing texture: $name" >&2
        exit 1
      fi ;;
    lm) magick "$work/out/lm_$name.png" -quality 92 -define webp:method=5 "$stage/lm_$name.webp" ;;
    photo) magick "$work/out/photo_$name.png" -quality 86 -define webp:alpha-quality=95 -define webp:method=5 "$stage/photo_$name.webp" ;;
    baked)
      if [ "$name" = 1 ]; then cp "$work/out/lightmaps.json" "$stage/";
      else printf '{"range":4,"gains":{}}\n' > "$stage/lightmaps.json"; fi ;;
  esac
done < "$stage/inputs"
rm "$stage/inputs"
magick "$work/sky_tonemapped.jpg" -resize 6144x3072 -quality 78 "$stage/sky.jpg"
backup=
if [ -e "$out" ]; then
  backup=$(mktemp -d "$root/assets/.walkthrough-previous.XXXXXX")
  mv "$out" "$backup/walkthrough"
fi
if ! mv "$stage" "$out"; then
  [ -z "$backup" ] || mv "$backup/walkthrough" "$out"
  exit 1
fi
trap - EXIT
[ -z "$backup" ] || echo "Previous bundle retained: $backup/walkthrough"
du -sh "$out"
