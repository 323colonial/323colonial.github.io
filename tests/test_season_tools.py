"""Offline authoring checks. Requires ImageMagick; never calls generation APIs."""
from concurrent.futures import ThreadPoolExecutor
import ast
import base64
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
sys.path.insert(0, str(TOOLS))


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
                        module.png_part = lambda *args: {}
                    with patch.dict(os.environ, GEMINI_API_KEY='offline-test-not-a-key'), self.assertRaisesRegex(RuntimeError, 'offline stop'):
                        module.one(9.5 if name == 'hero_half' else 6)


class SharedRecipeTools(unittest.TestCase):
    def test_tub_relight_imports_do_not_require_pilot_scratch_or_timezone(self):
        # Execute imports only; the CLI body would generate an image.
        tree = ast.parse((TOOLS / 'tub_relight.py').read_text())
        tree.body = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        for scratch in (str(ROOT), tempfile.gettempdir()):
            with self.subTest(scratch=scratch), patch.dict(sys.modules), patch.dict(os.environ, COLONIAL_SEASONS_WORK=scratch), patch('zoneinfo.ZoneInfo', side_effect=AssertionError('timezone lookup')), patch('urllib.request.urlopen', side_effect=AssertionError('network')), patch('subprocess.run', side_effect=AssertionError('process')):
                sys.modules.pop('pilot', None)
                exec(compile(tree, 'tub_relight.py', 'exec'), {})

    def test_png_callers_keep_exact_encoding_commands(self):
        cases = {
            'hero_relight': [('base.png', '2528x1696'), ('ref.png', None)],
            'hero_windows': [('base.png', '2528x1696'), ('ref.png', None)],
            'tubfill': [('base.png', '2400x1792'), ('tub/WINTER.png', '2400x1792')],
            'tub_relight': [('base.png', '2400x1792')],
            'tubtween': [('base.png', '2400x1792')],
        }
        raw = b'\x89PNG\r\n\x1a\n\x00\xffunchanged'
        for name, expected in cases.items():
            tree = ast.parse((TOOLS / (name + '.py')).read_text())
            ctx = dict(base='base.png', ref='ref.png')
            # Import only the encoder, never the historical recipe's generation body.
            imports = ast.Module(body=[n for n in tree.body if isinstance(n, ast.ImportFrom) and n.module == 'image_parts'], type_ignores=[])
            exec(compile(imports, name, 'exec'), ctx)
            calls = sorted([n for n in ast.walk(tree) if isinstance(n, ast.Call) and
                            isinstance(n.func, ast.Name) and n.func.id == 'png_part'],
                           key=lambda n: (n.lineno, n.col_offset))
            self.assertEqual(len(calls), len(expected), name)
            for call, (path, fit) in zip(calls, expected):
                with self.subTest(name=name, path=path), patch('subprocess.run', return_value=subprocess.CompletedProcess([], 0, raw)) as run:
                    result = eval(compile(ast.Expression(call), name, 'eval'), ctx)
                    command = ['magick', path] + (['-filter', 'Lanczos', '-resize', fit + '!'] if fit else []) + ['png:-']
                    run.assert_called_once_with(command, check=True, capture_output=True)
                    self.assertEqual(result, {'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(raw).decode()}})

    def test_shared_png_bytes_and_errors(self):
        image_parts = load('image_parts')
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp, 'input.ppm')
            image.write_bytes(b'P6\n2 1\n255\n\xff\x00\x00\x00\xff\x00')
            real_run = subprocess.run
            encoded = []
            def capture(*args, **kwargs):
                result = real_run(*args, **kwargs)
                encoded.append(result.stdout)
                return result
            for fit in (None, '3x4', '2400x1792', '2528x1696'):
                # Capture one real encoding: separate invocations carry different PNG timestamps.
                with patch('subprocess.run', side_effect=capture):
                    part = image_parts.png_part(str(image), fit)
                self.assertEqual(part['inlineData']['mimeType'], 'image/png')
                data = base64.b64decode(part['inlineData']['data'])
                self.assertEqual(data, encoded[-1])
                self.assertTrue(data.startswith(b'\x89PNG\r\n\x1a\n'))
                self.assertEqual((int.from_bytes(data[16:20], 'big'), int.from_bytes(data[20:24], 'big')),
                                 tuple(map(int, fit.split('x'))) if fit else (2, 1))
            with self.assertRaises(subprocess.CalledProcessError):
                image_parts.png_part(str(Path(tmp, 'missing.png')))

    def test_two_pass_callers_keep_paths_summaries_and_json_failures(self):
        for name in ('hero_half', 'hero_relight', 'tween'):
            for second in (' {"inliers":23,"patches":30,"max_shift_px":2} \n', ' \n', 'not JSON'):
                with self.subTest(name=name, second=second), tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, COLONIAL_SEASONS_WORK=tmp, GEMINI_API_KEY='offline-test'):
                    pilot = load('pilot'); smooth = load('smooth'); tmp = pilot.OUT
                    with patch.dict(sys.modules, pilot=pilot, smooth=smooth):
                        module = load(name)
                    first = ' {"inliers":21} \n'
                    commands = []
                    def run(args, **kw):
                        if len(args) > 1 and str(args[1]).endswith('/align.py'):
                            commands.append((args, kw))
                            Path(args[-1]).write_bytes(b'aligned')
                            return subprocess.CompletedProcess(args, 1, first if len(commands) == 1 else second, 'diagnostic')
                        if args[-1] == 'png:-':
                            return subprocess.CompletedProcess(args, 0, b'png')
                        value = '1280 848' if 'identify' in args else '0.5'
                        return subprocess.CompletedProcess(args, 0, value, '')
                    response = {'candidates': [{'content': {'parts': [{'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(b'raw').decode()}}]}}], 'usageMetadata': {'totalTokenCount': 3}}
                    job = 9.5 if name == 'hero_half' else 6 if name == 'hero_relight' else ('between', '01', 9.5)
                    stem = f'{tmp}/between/01/09h' if name == 'tween' else f'{tmp}/hero/' + ('06' if name == 'hero_relight' else '09h')
                    master = stem + '-blend.png' if name == 'tween' else f'{tmp}/win/hero/06-after.png' if name == 'hero_relight' else f'{ROOT}/assets/listing/01.webp'
                    with patch('subprocess.run', side_effect=run), patch.object(pilot, 'call', return_value=(b'raw', {})), patch.object(pilot, 'img_part', return_value={}), patch('urllib.request.urlopen', return_value=io.StringIO(json.dumps(response))), patch.object(smooth, 'score', return_value=(1, 2, 3)) as score:
                        if second == 'not JSON':
                            with self.assertRaises(json.JSONDecodeError): module.one(job)
                        else:
                            module.one(job)
                            metadata = json.loads(Path(stem + '.json').read_text())
                            if name == 'hero_relight':
                                self.assertEqual((metadata['align_first'], metadata['align_second']), (first.strip(), second.strip()))
                            else:
                                self.assertEqual(metadata['align'], json.loads(second) if second.strip() else {})
                            if name == 'tween': self.assertEqual(score.call_count, 1)
                    self.assertEqual(commands, [
                        ((sys.executable, str(TOOLS / 'align.py'), master, stem + '-full.png', stem + '-a.png'), {'capture_output': True, 'text': True}),
                        ((sys.executable, str(TOOLS / 'align.py'), master, stem + '-a.png', stem + '.png'), {'capture_output': True, 'text': True}),
                    ])
                    self.assertFalse(Path(stem + '-a.png').exists())
                    self.assertEqual(Path(stem + '.png').read_bytes(), b'aligned')

    def test_two_pass_errors_preserve_intermediate_and_propagate(self):
        pilot = load('pilot')
        self.assertTrue(callable(getattr(pilot, 'align_twice', None)), 'shared two-pass helper missing')
        for failure in ('first', 'second', 'missing', 'cleanup'):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as tmp:
                stem = str(Path(tmp, 'frame')); calls = []
                def run(args, **kw):
                    calls.append(args)
                    if failure == 'first' or failure == 'second' and len(calls) == 2:
                        raise OSError('launch failed')
                    if failure != 'missing': Path(args[-1]).write_bytes(b'keep')
                    return subprocess.CompletedProcess(args, 0, '{}\n', '')
                with contextlib.ExitStack() as stack:
                    stack.enter_context(patch('subprocess.run', side_effect=run))
                    if failure == 'cleanup': stack.enter_context(patch('os.remove', side_effect=PermissionError('cleanup failed')))
                    with self.assertRaises(OSError): pilot.align_twice('master.png', stem)
                self.assertEqual(len(calls), 1 if failure == 'first' else 2)
                self.assertEqual(Path(stem + '-a.png').exists(), failure in ('second', 'cleanup'))


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
