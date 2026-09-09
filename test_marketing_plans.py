"""Check owner-corrected kitchen pixels; run after scripts/marketing-plans.py."""
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
# Actual half-bath, pantry and stairs stay byte-identical to source.
for box in [(591, 480, 735, 548), (603, 562, 694, 616), (526, 663, 590, 846)]:
    assert pixels(main, box, offset) == pixels("plan-A-4", box), f"Real geometry changed: {box}"
print("Kitchen opening, refrigerator label, and preserved geometry pass")
