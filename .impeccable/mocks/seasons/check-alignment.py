"""Offline synthetic registration check. Run after compiling align.swift per provenance."""
from pathlib import Path
import subprocess
import tempfile
import os

root = Path(__file__).resolve().parent
binary = Path('.pi/artifacts/seasons/v2/align')
binary.parent.mkdir(parents=True, exist_ok=True)
env = {k: v for k, v in os.environ.items() if k not in ('SDKROOT', 'CPATH', 'CPLUS_INCLUDE_PATH', 'C_INCLUDE_PATH', 'LIBRARY_PATH', 'NIX_CFLAGS_COMPILE')}
env['DEVELOPER_DIR'] = '/Library/Developer/CommandLineTools'
subprocess.run(['/Library/Developer/CommandLineTools/usr/bin/swiftc', '-sdk', '/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk', '-module-cache-path', str(binary.parent / 'module-cache'), '-O', str(root / 'align.swift'), '-o', str(binary)], env=env, check=True)
with tempfile.TemporaryDirectory() as folder:
    folder = Path(folder)
    ref, moved, out = (folder / name for name in ('reference.png', 'translated.png', 'aligned.png'))
    subprocess.run(['magick', str(root / 'v2/summer.jpg'), '-resize', '640x424!', str(ref)], check=True)
    subprocess.run(['magick', str(ref), '-virtual-pixel', 'edge', '-distort', 'SRT', '0,0 1 0 9,6', str(moved)], check=True)
    subprocess.run([str(binary), str(ref), str(moved), str(out)], check=True)
    def mae(a, b):
        # Exclude boundary filling, where inverse translation cannot recover pixels.
        proc = subprocess.run(['magick', 'compare', '-metric', 'MAE', f'{a}[560x344+40+40]', f'{b}[560x344+40+40]', 'null:'], capture_output=True, text=True)
        assert proc.returncode in (0, 1), proc.stderr
        return float(proc.stderr.split('(')[1].split(')')[0])
    before, after = mae(ref, moved), mae(ref, out)
    print(f'Translation MAE before={before:.6f}, after={after:.6f}')
    assert after < before * .2, 'Registration must remove at least 80% of synthetic translation error'
print('PASS: known translation corrected without new dependencies')
