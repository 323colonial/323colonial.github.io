"""Pipeline regressions, no Blender or network required: python3 tests/test_walkthrough_tools.py."""
import ast
import copy
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import SimpleNamespace as NS
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'scripts/walkthrough'


def definitions(name, names, **context):
    tree = ast.parse((TOOLS / name).read_text())
    tree.body = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    exec(compile(tree, str(TOOLS / name), 'exec'), context)
    return context


class PipelineTests(unittest.TestCase):
    def test_bake_signature_tracks_geometry_and_lighting(self):
        with tempfile.TemporaryDirectory() as work:
            sky = Path(work) / 'sky.hdr'
            sky.write_bytes(b'sky')
            ctx = definitions('build.py', ['layout_signature'], json=json, os=os,
                              HERE=str(TOOLS), TEX=work, HDRI=str(sky), SIZE=64,
                              SAMPLES=16, SUN_ROT=1, LM_RANGE=4, house=NS(MATS={'paint': {'color': [1, 1, 1]}}))
            surface = NS(page='in0', ox=4, oy=4, pw=20, ph=20, mat='paint',
                         verts=[(0, 0, 0), (1, 0, 0), (0, 0, 1)], tris=[(0, 1, 2)],
                         uv0=[(0, 0), (1, 0), (0, 1)], nrm=[(0, 1, 0)] * 3,
                         lm=[(0, 0), (1, 0), (0, 1)], dens=1)
            model = NS(surfs=[surface], lights=[(0, 0, 7, 1)], downlights={})
            signature = ctx['layout_signature']
            base = signature(model)
            moved = copy.deepcopy(model)
            moved.surfs[0].verts = [(x + 8, y, z) for x, y, z in surface.verts]
            self.assertNotEqual(base, signature(moved), 'translation must invalidate bake')
            moved = copy.deepcopy(model)
            moved.lights[0] = (0, 0, 8, 1)
            self.assertNotEqual(base, signature(moved), 'light movement must invalidate bake')
            moved = copy.deepcopy(model)
            moved.downlights[0] = .25
            self.assertNotEqual(base, signature(moved), 'light direction/size must invalidate bake')
            ctx['SUN_ROT'] = 2
            self.assertNotEqual(base, signature(model), 'sky rotation must invalidate bake')
            ctx['SUN_ROT'] = 1
            sky.write_bytes(b'changed sky')
            self.assertNotEqual(base, signature(model), 'sky bytes must invalidate bake')

    def test_export_requires_current_encoded_maps_and_never_revives_old_photos(self):
        import time
        with tempfile.TemporaryDirectory() as work:
            out = Path(work) / 'out'
            out.mkdir()
            (out / 'lm_in0.png').write_bytes(b'lightmap')
            (out / 'photo_in0.png').write_bytes(b'stale photo')
            fake_bpy = NS(ops=NS(object=NS(select_all=lambda **kw: None),
                                  export_scene=NS(gltf=lambda **kw: None)))
            ctx = definitions('build.py', ['export'], bpy=fake_bpy, os=os, json=json, time=time,
                              WORK=work, FT=.3048, SUN_ROT=1, PHOTO_PAGES=[],
                              house=NS(MATS={}, ground=lambda x, y: 0, GROUND_N=0),
                              layout_signature=lambda b: 'current', check_shell=lambda b: {}, log=lambda *a: None)
            B = NS(solids=[], floors=[], doors=[])
            for stamp, expected in [('old', False), ('current', True)]:
                (out / 'lightmaps.json').write_text(json.dumps({'signature': stamp}))
                ctx['export'](None, B, [], {'in0': None})
                scene = json.loads((out / 'scene.json').read_text())
                self.assertEqual(scene['baked'], expected)
                self.assertEqual(scene['photoPages'], [], 'stale projection must not be rediscovered')

    def publish_fixture(self, tmp, baked=False):
        root = Path(tmp)
        scripts = root / 'scripts/walkthrough'
        scripts.mkdir(parents=True)
        shutil.copy(TOOLS / 'publish.sh', scripts)
        work = root / 'work'
        (work / 'out').mkdir(parents=True)
        (work / 'textures').mkdir()
        (work / 'out/house.glb').write_bytes(b'new model')
        (work / 'out/scene.json').write_text(json.dumps({'baked': baked, 'pages': ['in0'], 'photoPages': [], 'materials': {'paint': {'tex': 'paint'}}}))
        (work / 'sky_tonemapped.jpg').write_bytes(b'sky')
        (work / 'textures/paint.jpg').write_bytes(b'paint')
        out = root / 'assets/walkthrough'
        (out / 'tex').mkdir(parents=True)
        (out / 'house.glb').write_bytes(b'old model')
        (out / 'tex/paint.webp').write_bytes(b'old texture')
        # Conversion stub: exercises orchestration, not ImageMagick codecs.
        bin_dir = root / 'bin'
        bin_dir.mkdir()
        magick = bin_dir / 'magick'
        magick.write_text('#!/usr/bin/env bash\nset -eu\n[ "${FAIL_CONVERT:-0}" = 0 ]\ncp "$1" "${@: -1}"\n')
        magick.chmod(0o755)
        env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ['PATH'])
        return scripts / 'publish.sh', work, out, env

    def test_publish_fresh_unbaked_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            script, work, out, env = self.publish_fixture(tmp)
            result = subprocess.run(['bash', str(script), str(work)], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((out / 'house.glb').read_bytes(), b'new model')
            self.assertEqual(json.loads((out / 'lightmaps.json').read_text())['gains'], {})
            self.assertFalse(list(out.glob('lm_*.webp')))

    def test_failed_publish_preserves_previous_bundle(self):
        for failure in ['missing-texture', 'conversion']:
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as tmp:
                script, work, out, env = self.publish_fixture(tmp, baked=True)
                (work / 'out/lightmaps.json').write_text('{"range":4,"gains":{"in0":1}}')
                (work / 'out/lm_in0.png').write_bytes(b'lightmap')
                if failure == 'missing-texture':
                    (work / 'textures/paint.jpg').unlink()
                else:
                    env['FAIL_CONVERT'] = '1'
                before = {str(p.relative_to(out)): p.read_bytes() for p in out.rglob('*') if p.is_file()}
                result = subprocess.run(['bash', str(script), str(work)], env=env, capture_output=True)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                after = {str(p.relative_to(out)): p.read_bytes() for p in out.rglob('*') if p.is_file()}
                self.assertEqual(before, after)

    def test_unbaked_bundle_passes_node_asset_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / 'assets/walkthrough'
            assets.mkdir(parents=True)
            for source in (ROOT / 'assets/walkthrough').iterdir():
                if source.name != 'scene.json' and not source.name.startswith('lm_'):
                    (assets / source.name).symlink_to(source)
            scene = json.loads((ROOT / 'assets/walkthrough/scene.json').read_text())
            scene['baked'] = False
            (assets / 'scene.json').write_text(json.dumps(scene))
            (root / 'walkthrough').symlink_to(ROOT / 'walkthrough')
            result = subprocess.run(['node', '--test', '--test-name-pattern=assets referenced',
                                     str(ROOT / 'tests/walkthrough.test.mjs')], cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_note_boundary_rejects_invalid_requests_without_writes(self):
        import http.server
        import threading
        import base64
        handler = definitions('serve.py', ['Handler'], http=http, os=os, threading=threading,
                              json=json, base64=base64)['Handler']
        for headers, body, status in [
            ({'Origin': 'https://untrusted.invalid'}, b'{}', 403),
            ({'Host': 'untrusted.invalid'}, b'{}', 403),
            ({'Content-Length': str(5 * 1024 * 1024)}, b'', 413),
            ({}, b'{bad', 400),
            ({}, b'[]', 400),
            ({}, b'{"note":123}', 400),
            ({}, b'{"note":"x","image":"data:image/jpeg;base64,!"}', 400),
            ({}, json.dumps({'note': 'test', 'image': 'data:image/jpeg;base64,' + base64.b64encode(b'\xff\xd8\xfftest').decode()}).encode(), 200),
        ]:
            with self.subTest(headers=headers, body=body), tempfile.TemporaryDirectory() as tmp:
                req = object.__new__(handler)
                req.path = '/__note'
                req.server = NS(server_address=('127.0.0.1', 8377))
                req.headers = {'Host': '127.0.0.1:8377', 'Origin': 'http://127.0.0.1:8377',
                               'Content-Length': str(len(body)), **headers}
                req.rfile, req.wfile = io.BytesIO(body), io.BytesIO()
                codes = []
                req.send_error = lambda code, *a: codes.append(code)
                req.send_response = lambda code: codes.append(code)
                req.send_header = lambda *a: None
                req.end_headers = lambda: None
                cwd = os.getcwd()
                try:
                    os.chdir(tmp)
                    if status == 200:
                        Path('.walkthrough-notes').mkdir()
                        Path('.walkthrough-notes/003.jpg').write_bytes(b'previous')
                    req.do_POST()
                    self.assertEqual(codes, [status])
                    if status == 200:
                        self.assertEqual(json.loads(req.wfile.getvalue()), {'n': 4})
                        self.assertEqual(Path('.walkthrough-notes/003.jpg').read_bytes(), b'previous')
                        self.assertEqual(Path('.walkthrough-notes/004.jpg').read_bytes(), b'\xff\xd8\xfftest')
                    else:
                        self.assertEqual(list(Path(tmp).iterdir()), [])
                finally:
                    os.chdir(cwd)


if __name__ == '__main__':
    unittest.main()
