"""Run: blender -b -P tests/test_walkthrough_blender.py (no renders or downloads)."""
import sys
from pathlib import Path
import tempfile
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/walkthrough'))
import hb
import house
import project

for drawn in (False, True):
    B = hb.Builder()
    B.mats = house.MATS
    B.poly('paint', [(0, 26.91, 0), (4, 26.91, 0), (4, 26.91, 4), (0, 26.91, 4)])
    surface = B.surfs[0]
    if drawn:
        surface.verts0 = [v.copy() for v in surface.verts]
        for v in surface.verts:
            v.y = house.ycal(v.y)
    B.pack(size=128)
    points = []
    def keep(p):
        points.append(p.copy())
        return np.ones(p.shape[:2], dtype=bool)
    with tempfile.TemporaryDirectory() as tmp:
        project.project(B, {}, tmp, tmp, 128, house.ycal, keep=keep)
    assert points, 'projection must sample test surface'
    expected = house.ycal(26.91) if drawn else 26.91
    assert np.allclose(points[0][..., 1], expected), (drawn, points[0][0, 0, 1], expected)
print('PASS: projection calibrates drawn surfaces once and leaves measured shell unchanged')
