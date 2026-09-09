"""Rebuild buyer-facing crops from original CAD rasters; requires ImageMagick.

Main-floor kitchen opening/refrigerator recess corrected from owner confirmation
and IMG_0242 Medium.jpeg; other geometry retained, original CAD rasters untouched.
Coordinates use the 2000px-wide source preview scale.
Areas come only from printed dimensions, rounded to the nearest 10 sq ft;
these are selected spaces, not measured living-area or whole-floor totals.
"""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SCALE = 1.7  # Original sheets are 3400px wide.


def build(sheet, name, crop, labels, masks=()):
    args = ["magick", str(ROOT / f"images/plan-A-{sheet}.png"),
            "-font", "DejaVu-Sans", "-pointsize", "17", "-stroke", "none"]
    for x1, y1, x2, y2 in [*masks, *(box for box, _ in labels)]:
        args += ["-fill", "white", "-draw",
                 f"rectangle {x1*SCALE},{y1*SCALE} {x2*SCALE},{y2*SCALE}"]
    for (x1, y1, x2, y2), text in labels:
        # Center text inside the erased dimension line without touching walls.
        args += ["-fill", "#172c24", "-gravity", "NorthWest", "-draw",
                 f"translate {(x1+x2)/2*SCALE},{(y2-1)*SCALE} "
                 f"text-anchor middle text 0,0 '{text}'"]
    x, y, width, height = crop
    args += ["-crop", f"{round(width*SCALE)}x{round(height*SCALE)}+{round(x*SCALE)}+{round(y*SCALE)}",
             "+repage", "-strip", "-set", "comment",
             f"Marketing crop of plan-A-{sheet}.png; "
             + ("kitchen opening and refrigerator recess owner/photo-corrected; other geometry retained; "
                if sheet == 4 else "original sketch/photo-derived geometry retained; ")
             + "not field-measured. Areas rounded from source dimensions.",
             str(ROOT / f"images/plan-{name}-marketing.png")]
    subprocess.run(args, check=True)


if __name__ == "__main__":
    build(4, "main", (75, 315, 1210, 680), [
        ((525, 406, 615, 420), "~450 sq ft"),  # 45 × 10
        ((1038, 671, 1130, 685), "~620 sq ft"),  # 24 × 26
        ((607, 698, 685, 713), "~20 sq ft"),  # 6 ft 7.5 in × 3 ft 6 in
        ((120, 789, 209, 804), "~360 sq ft"),  # 10 × 36
        ((515, 920, 611, 934), "~70 sq ft"),  # 12 × 6
        ((534, 576, 590, 591), "FRIDGE"),  # Kitchen recess beside actual pantry.
    ], masks=[(286, 399, 346, 413), (795, 399, 852, 413), (960, 399, 1018, 413),
              # No wall facing stairs; peninsula is cabinetry, not a partition.
              # Stop before actual pantry wall at x603; preserve half-bath walls.
              (437, 608, 602, 616), (531, 558, 535, 608), (533, 558, 590, 562)])
    build(5, "second", (145, 515, 1070, 425), [
        ((502, 594, 576, 608), "~90 sq ft"),  # 10 ft 9 in × 8
        ((751, 569, 819, 584), "~30 sq ft"),  # 6 ft 6 in × 4 ft 9 in
        ((850, 815, 938, 830), "~100 sq ft"),  # 7 ft 5.5 in × 14
    ], masks=[(628, 570, 728, 582), (963, 570, 1068, 582),
              (435, 728, 452, 870), (826, 515, 834, 526), (166, 515, 173, 526)])
