#!/usr/bin/env python3
"""Stage colonial-6nu's reviewed local conversion; never overwrite website inputs.

Run with .pi/research/colonial-meb-lama/venv/bin/python scripts/remove-watermarks.py.
Requires the preserved originals and reviewed-inputs.json in the private evidence directory.
No download, CPU inference fallback, source cropping or automatic mask selection.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

if not __debug__:
    raise SystemExit('Optimized Python disables required integrity checks')

os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '0'
ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / '.pi/research/colonial-meb-lama'
WORK = ROOT / '.pi/artifacts/colonial-6nu'
CHECKPOINT = '7ba7aa7ac37a4d41fdbbeba3a2af7ead18058552997e3a3cd1a3b2210c9e6b4c'
os.environ['LAMA_MODEL'] = str(RUNTIME / 'big-lama.pt')

import numpy as np
from PIL import Image
import torch
from simple_lama_inpainting import SimpleLama


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    jobs = json.loads((WORK / 'reviewed-inputs.json').read_text())
    listing = json.loads((WORK / 'originals/assets/listing/manifest.json').read_text())
    redfin = {p['derivatives'][0]['path'] for p in listing['photos'] if 'redfin_source' in p}
    assert len(jobs) == 470 and len({r['path'] for r in jobs}) == 470
    assert sum(r['mask_xyxy'] is not None for r in jobs) == 426
    assert digest(RUNTIME / 'big-lama.pt') == CHECKPOINT
    assert torch.backends.mps.is_available()
    stage = WORK / 'stage'
    assert not stage.exists(), 'Never overwrite an earlier conversion'
    for job in jobs:
        for r in (job, job['small']):
            assert digest(ROOT / r['path']) == r['source_sha256'], r['path']
            assert digest(WORK / 'originals' / r['path']) == r['source_sha256']
    stage.mkdir()
    model = SimpleLama(device=torch.device('mps'))
    assert str(next(model.model.parameters()).device) == 'mps:0'
    report = dict(approval='colonial-6nu', checkpoint_sha256=CHECKPOINT,
                  package='simple-lama-inpainting==0.1.2',
                  runner_sha256=digest(Path(__file__)),
                  environment_sha256=digest(RUNTIME / 'requirements-lock.txt'),
                  originals='.pi/artifacts/colonial-6nu/originals/',
                  masters='.pi/artifacts/colonial-6nu/masters/',
                  masks='.pi/artifacts/colonial-6nu/masks/',
                  encoding='ImageMagick WebP quality 80 for Redfin listing masters, otherwise 78; small quality 78. RGB PNG masters are exact outside mask; lossy delivery is not.',
                  images=[], previews=[])
    for job in jobs:
        source = WORK / 'originals' / job['path']
        image = Image.open(source).convert('RGB')
        w, h = image.size
        assert [w, h] == job['size']
        if job['mask_xyxy'] is None:
            job['output_sha256'] = job['source_sha256']
            job['small']['output_sha256'] = job['small']['source_sha256']
        else:
            x0, y0, x1, y1 = job['mask_xyxy']
            assert all(type(n) is int for n in job['mask_xyxy'])
            assert 0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h
            mask = Image.new('L', image.size)
            mask.paste(255, (x0, y0, x1, y1))
            selected = np.asarray(mask) > 0
            assert selected.sum() == (x1 - x0) * (y1 - y0)
            mask_path = WORK / 'masks' / Path(job['path']).with_suffix('.png')
            master = WORK / 'masters' / Path(job['path']).with_suffix('.png')
            for p in (mask_path, master):
                p.parent.mkdir(parents=True, exist_ok=True)
            mask.save(mask_path)
            assert np.array_equal(np.asarray(Image.open(mask_path)), np.asarray(mask))
            torch.mps.synchronize()
            start = time.perf_counter()
            prediction = model(image, mask)
            torch.mps.synchronize()
            seconds = time.perf_counter() - start
            assert prediction.width >= w and prediction.height >= h
            assert prediction.width - w < 8 and prediction.height - h < 8
            # Remove only model padding; generated pixels cannot escape the reviewed mask.
            result = Image.composite(prediction.crop((0, 0, w, h)), image, mask)
            a, b = np.asarray(image), np.asarray(result)
            assert result.size == image.size
            assert np.array_equal(a[~selected], b[~selected])
            assert np.any(a[selected] != b[selected])
            result.save(master)
            assert np.array_equal(np.asarray(Image.open(master)), b)
            target = stage / job['path']
            small = stage / job['small']['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            quality = 80 if job['path'] in redfin else 78
            subprocess.run(['magick', str(master), '-strip', '-quality', str(quality), str(target)], check=True)
            sw, sh = job['small']['size']
            subprocess.run(['magick', str(master), '-resize', f'{sw}x{sh}!', '-strip', '-quality', '78', str(small)], check=True)
            assert Image.open(target).size == image.size
            assert list(Image.open(small).size) == job['small']['size']
            assert small.stat().st_size < 500000
            if job['path'].startswith('assets/listing/'):
                assert target.stat().st_size < 500000, job['path']
            delivered = np.asarray(Image.open(target).convert('RGB'))
            delta = np.abs(delivered.astype('int16') - b.astype('int16'))[~selected]
            job.update(output_sha256=digest(target), master_sha256=digest(master),
                       mask_sha256=digest(mask_path), outside_mask_equal_before_encoding=True,
                       delivery_outside_mask_mean_absolute_error=float(delta.mean()),
                       delivery_outside_mask_max_absolute_error=int(delta.max()),
                       device='mps:0', cpu_fallback=False, inference_seconds=seconds,
                       delivery_quality=quality)
            job['small']['output_sha256'] = digest(small)
        assert digest(source) == job['source_sha256']
        assert digest(ROOT / job['path']) == job['source_sha256']
        report['images'].append(job)
        (WORK / 'conversion.json').write_text(json.dumps(report, indent=2) + '\n')
        print(job['path'], 'clean unchanged' if job['mask_xyxy'] is None else 'staged; integrity PASS', flush=True)
    print('PASS: all masters staged; website untouched; visual review still required', flush=True)


if __name__ == '__main__':
    main()
