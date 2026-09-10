"""Rebuild buyer-facing crops from original CAD rasters; requires ImageMagick.

Main-floor kitchen opening/refrigerator recess corrected from owner confirmation
and IMG_0242 Medium.jpeg. Door swings, double great-room windows and both deck
sliders corrected from owner confirmation (2026-09-10; bath into bath).
Other geometry retained, original CAD rasters untouched. Symbols are nominal:
fixture clearances and opening sizes are not field-measured.
Coordinates use the 2000px-wide source preview scale.
Areas come only from printed dimensions, rounded to the nearest 10 sq ft;
these are selected spaces, not measured living-area or whole-floor totals.
"""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SCALE = 1.7  # Original sheets are 3400px wide.


def build(sheet, name, crop, labels, masks=(), drawing=""):
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
    if drawing:
        args += ["-fill", "none", "-stroke", "#777777", "-strokewidth", "0.6",
                 "-draw", f"scale {SCALE},{SCALE} {drawing}"]
    x, y, width, height = crop
    args += ["-crop", f"{round(width*SCALE)}x{round(height*SCALE)}+{round(x*SCALE)}+{round(y*SCALE)}",
             "+repage", "-strip", "-set", "comment",
             f"Marketing crop of plan-A-{sheet}.png; "
             + ("kitchen owner/photo-corrected; four door swings, two double great-room windows "
                "and both deck sliders owner-corrected; other geometry retained; "
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
        ((667, 535, 735, 549), "HALF BATH"),  # Clear of new inward leaf.
    ], masks=[(286, 399, 346, 413), (795, 399, 852, 413), (960, 399, 1018, 413),
              # No wall facing stairs; peninsula is cabinetry, not a partition.
              # Stop before actual pantry wall at x603; preserve half-bath walls.
              (437, 608, 602, 616), (531, 558, 535, 608), (533, 558, 590, 562),
              # Erase old swing symbols, retaining jambs and room walls.
              (692, 774, 735, 816), (753, 645, 796, 679),
              (900, 488, 938, 526), (661, 493, 708, 536),
              (646, 482, 660, 540),  # Relocate half-bath label away from leaf.
              # Double the great-room openings; erase the old porch-door swing.
              (305, 471, 393, 481), (325, 481, 373, 526),
              (283, 861, 399, 872),
              # Replace both ambiguous deck-opening lines with sliding panels.
              (230, 530, 239, 612), (230, 730, 239, 818)], drawing="""
        # Closet: hinge at lower jamb, leaf inside closet.
        line 691,775 699,775
        line 691,815 699,815
        path 'M 694,775 A 39,39 0 0,0 655,814 L 694,814'
        # Master bath: vanity-side hinge, partial inward leaf below W.C.
        # Partial bath swings preserve schematic fixtures, not certify clearance.
        path 'M 755,640 A 39,39 0 0,1 756.3,629.9 L 794,640'
        # Garage: leaf and arc in hallway, not garage.
        line 900,488 908,488
        line 900,524 908,524
        line 900,524 900,532
        line 908,524 908,532
        path 'M 900,488 A 36,36 0 0,0 864,524 L 900,524'
        # Half bath: show partial inward opening to keep leaf clear of vanity.
        path 'M 663,493 A 41,41 0 0,0 642.5,498.5 L 663,534'
        # Two equal glazed bays, each window twice the original opening width.
        rectangle 305,472 393,480
        line 305,476 393,476
        line 349,472 349,480
        rectangle 283,862 399,870
        line 283,866 399,866
        line 341,862 341,870
        # Double sliding deck doors: overlapping panels and opposite slide arrows.
        rectangle 231,530 233,575
        rectangle 235,567 237,612
        line 230,530 239,530
        line 230,612 239,612
        path 'M 246,549 L 246,565 M 243,562 L 246,565 L 249,562'
        path 'M 246,593 L 246,577 M 243,580 L 246,577 L 249,580'
        rectangle 231,730 233,778
        rectangle 235,770 237,818
        line 230,730 239,730
        line 230,818 239,818
        path 'M 246,752 L 246,768 M 243,765 L 246,768 L 249,765'
        path 'M 246,796 L 246,780 M 243,783 L 246,780 L 249,783'
    """)
    build(5, "second", (145, 515, 1070, 425), [
        ((502, 594, 576, 608), "~90 sq ft"),  # 10 ft 9 in × 8
        ((751, 569, 819, 584), "~30 sq ft"),  # 6 ft 6 in × 4 ft 9 in
        ((850, 815, 938, 830), "~100 sq ft"),  # 7 ft 5.5 in × 14
    ], masks=[(628, 570, 728, 582), (963, 570, 1068, 582),
              (435, 728, 452, 870), (826, 515, 834, 526), (166, 515, 173, 526)])
