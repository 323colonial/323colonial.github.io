"""Check owner-corrected drawing pixels; run after scripts/marketing-plans.py."""
import subprocess


def pixels(name, box, offset=(0, 0)):
    x1, y1, x2, y2 = [round(value * 1.7) for value in box]
    return subprocess.check_output([
        "magick", f"images/{name}.png", "-crop",
        f"{x2-x1}x{y2-y1}+{x1-offset[0]}+{y1-offset[1]}",
        "+repage", "-depth", "8", "rgb:-",
    ])


main = "plan-main-marketing"
offset = (128, 536)
# No partition across from stairs or around the refrigerator recess.
for box in [(438, 609, 601, 615), (531, 560, 534, 608), (533, 558, 590, 561)]:
    assert min(pixels(main, box, offset)) == 255, f"False kitchen wall remains: {box}"
# Refrigerator label sits inside kitchen recess, not in the actual pantry.
assert min(pixels(main, (535, 576, 588, 593), offset)) < 100, "Refrigerator label missing"
# Half-bath fixtures/walls, pantry and stairs stay byte-identical to source.
# Half-bath door is now explicitly owner-corrected.
for box in [(591, 480, 640, 548), (591, 544, 665, 548),
            (748, 602, 786, 627), (814, 611, 899, 638),
            (603, 562, 694, 616), (526, 663, 590, 846)]:
    assert pixels(main, box, offset) == pixels("plan-A-4", box), f"Real geometry changed: {box}"


# Check leaf positions, not annotations: new leaves inside requested rooms;
# old leaves/arcs outside those rooms must be erased.
for label, leaf, cleared in [
    ("closet inward", (660, 813, 689, 815), (700, 812, 730, 816)),
    ("master bath inward", (771, 633, 775, 636), (753, 649, 757, 675)),
    ("garage into hallway", (866, 523, 894, 525), (911, 522, 933, 526)),
    ("half bath inward", (650, 512, 653, 515), (675, 532, 703, 536)),
]:
    assert min(pixels(main, leaf, offset)) < 200, f"Missing leaf: {label}"
    assert min(pixels(main, cleared, offset)) == 255, f"Old swing remains: {label}"

# Both great-room windows span twice the old opening width, with central mullions.
for label, bounds, center, y in [
    ("porch-side", (305, 393), 349, 476),
    ("front", (283, 399), 341, 866),
]:
    for x in [bounds[0]+3, bounds[1]-3, center]:
        assert min(pixels(main, (x-1, y-1, x+1, y+1), offset)) < 200, f"Missing {label} glazing/mullion"
assert min(pixels(main, (325, 485, 373, 526), offset)) == 255, "Great-room porch door remains"

# Two offset sliding panels and opposing slide arrows at BOTH deck openings.
for top, bottom in [(530, 612), (730, 818)]:
    middle = (top+bottom)/2
    for x, y in [(232, top+10), (236, bottom-10), (246, middle-12), (246, middle+12)]:
        assert min(pixels(main, (x-1, y-1, x+1, y+1), offset)) < 200, "Missing deck sliding panel/arrow"

# Source sheets and second-floor crop are immutable for this correction.
import hashlib
from pathlib import Path
for filename, expected in [
    ("plan-A-4.png", "eba5b35fb31372a0de403a067c81092bbc0b8658148cec7ddd038890e0c33603"),
    ("plan-A-5.png", "da6430674da310f41db0d5e7ed86238551a49947da92459ad3a3f9affea4d96a"),
    ("plan-second-marketing.png", "3ae47d99665cf2ba0db7976b16eff4276cb6aa42a9216ffe024892ab63793dab"),
]:
    assert hashlib.sha256(Path("images", filename).read_bytes()).hexdigest() == expected, filename
print("Kitchen, four inward swings, two double windows, both deck sliders, and preserved sheets pass")
