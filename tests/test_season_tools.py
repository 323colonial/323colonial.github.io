"""Offline authoring checks. Requires ImageMagick; never calls generation APIs."""
from concurrent.futures import ThreadPoolExecutor
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'scripts/seasons'


def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PilotPaths(unittest.TestCase):
    def test_import_and_sun_are_offline_and_use_private_paths(self):
        with patch.dict(os.environ, {}, clear=True), patch('urllib.request.urlopen', side_effect=AssertionError('network')), patch('subprocess.run', side_effect=AssertionError('process')):
            pilot = load('pilot')
        self.assertEqual(Path(pilot.ROOT), ROOT)
        self.assertEqual(Path(pilot.OUT), ROOT / '.pi/artifacts/seasons')
        self.assertTrue(Path(pilot.ROOT, 'assets/listing/01.webp').is_file())
        with tempfile.TemporaryDirectory() as tmp:
            scratch = Path(tmp, 'not-created')
            env = dict(os.environ, COLONIAL_SEASONS_WORK=str(scratch))
            result = subprocess.run([sys.executable, str(TOOLS / 'pilot.py'), 'sun'], cwd=tmp, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(result.stdout.splitlines()), 12)
            self.assertFalse(scratch.exists())
            with patch.dict(os.environ, env):
                self.assertEqual(Path(load('pilot').OUT), scratch.resolve())

    def test_repository_output_and_tag_escape_rejected_before_generation(self):
        for out in (ROOT, ROOT / 'assets/seasons', TOOLS):
            with self.subTest(out=out), patch.dict(os.environ, COLONIAL_SEASONS_WORK=str(out)):
                with self.assertRaises(ValueError):
                    load('pilot')
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, COLONIAL_SEASONS_WORK=tmp):
            pilot = load('pilot')
            pilot.OUT = tmp  # Keep red runs private even before the environment override exists.
            with patch.object(pilot, 'call', side_effect=AssertionError('generation')), patch.object(pilot, 'img_part', side_effect=AssertionError('image')), patch.object(pilot.os, 'makedirs', side_effect=AssertionError('write')):
                for tag in ('../escape', '/absolute', 'nested/../../escape'):
                    with self.subTest(tag=tag), self.assertRaises(ValueError):
                        pilot.generate(39, 6, tag)
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_hero_destinations_exist_before_generation(self):
        for name in ('hero_half', 'hero_relight'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, COLONIAL_SEASONS_WORK=tmp):
                pilot = load('pilot')
                with patch.dict(sys.modules, pilot=pilot):
                    module = load(name)
                def stop(*args, **kwargs):
                    self.assertTrue(Path(tmp, 'hero').is_dir(), 'paid call before output directory exists')
                    raise RuntimeError('offline stop')
                with patch.object(pilot, 'img_part', return_value={}), patch.object(pilot, 'call', side_effect=stop), patch('urllib.request.urlopen', side_effect=stop):
                    if name == 'hero_relight':
                        module.part = lambda *args: {}
                    with patch.dict(os.environ, GEMINI_API_KEY='offline-test-not-a-key'), self.assertRaisesRegex(RuntimeError, 'offline stop'):
                        module.one(9.5 if name == 'hero_half' else 6)

    def test_scratch_consumers_keep_source_executable_path(self):
        for name in ('hero_half', 'hero_relight', 'tween'):
            text = (TOOLS / (name + '.py')).read_text()
            self.assertNotIn("f'{D}/align.py'", text)
            self.assertIn("f'{pilot.HERE}/align.py'", text)


class Alignment(unittest.TestCase):
    def test_frame_workers_own_parallelism_and_patch_results_stay_ordered(self):
        align = load('align')
        original = align.run
        owners = set()
        observed = set()
        lock = threading.Lock()
        def run(*args):
            with lock:
                observed.add(threading.get_ident())
            return original(*args)
        align.run = run
        with tempfile.TemporaryDirectory() as tmp:
            def one(n):
                with lock:
                    owners.add(threading.get_ident())
                scratch = Path(tmp, str(n)); scratch.mkdir()
                image = str(ROOT / f'assets/listing/{n:02d}-small.webp')
                w, h, rows = align.measure(image, image, str(scratch))
                self.assertGreater(len(rows), 12)
                self.assertEqual(rows, sorted(rows, key=lambda r: (r[1], r[0])))
                self.assertTrue(all(r[2:4] == (0, 0) for r in rows))
                self.assertIsNotNone(align.fit(rows)[0])
            with ThreadPoolExecutor(2) as pool:
                list(pool.map(one, (1, 39)))
        self.assertEqual(observed, owners, 'inner patch workers multiply subprocess concurrency')

    def test_alignment_keeps_residual_check_and_rejects_weak_fits(self):
        align = load('align')
        image = str(ROOT / 'assets/listing/01-small.webp')
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()) as output:
            align.main(image, image, str(Path(tmp, 'aligned.png')))
            result = json.loads(output.getvalue())
            self.assertTrue(result['applied'])
            self.assertEqual(result['residual_max_px'], 0)
            self.assertEqual(result['residual_median_px'], 0)
        rows = [(x, y, 0, 0, 1) for x in (0, 50, 100) for y in (0, 50, 100)]
        with tempfile.TemporaryDirectory() as tmp, patch.object(align, 'measure', return_value=(720, 477, rows)), contextlib.redirect_stdout(io.StringIO()) as output:
            align.main(image, image, str(Path(tmp, 'weak.png')))
            self.assertFalse(json.loads(output.getvalue())['applied'])
            self.assertTrue(Path(tmp, 'weak.png').is_file())


if __name__ == '__main__':
    unittest.main()
