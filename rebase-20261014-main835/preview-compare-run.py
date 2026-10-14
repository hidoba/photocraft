"""Reproduce the cached channel-preview comparison with the accompanying Rust example."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--before', type=Path, required=True)
parser.add_argument('--after', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--runs', type=int, default=6)
parser.add_argument('--before-head', required=True)
parser.add_argument('--after-head', required=True)
parser.add_argument('--base', required=True)
parser.add_argument('--icd', default='/usr/share/vulkan/icd.d/lvp_icd.json')
parser.add_argument('--adapter-note', default='llvmpipe Vulkan software adapter; these are not new NVIDIA measurements')
args = parser.parse_args()
if args.runs < 1:
    parser.error('--runs must be positive')
env = os.environ.copy()
env.update({'WGPU_BACKEND': 'vulkan', 'VK_DRIVER_FILES': args.icd})
def other_renderer_count():
    count = 0
    for entry in Path('/proc').iterdir():
        if entry.name.isdigit():
            try:
                count += entry.joinpath('comm').read_text(errors='replace').startswith('UnrealEditor')
            except OSError:
                pass
    return count

raw = []
for mode in ['integer', 'fractional']:
    for repetition in range(args.runs):
        order = ['before', 'after'] if repetition % 2 == 0 else ['after', 'before']
        for build in order:
            binary = getattr(args, build).resolve()
            other_before = other_renderer_count()
            run = subprocess.run([str(binary)] + (['--fractional'] if mode == 'fractional' else []), env=env, text=True, capture_output=True, check=True)
            rows = [json.loads(line) for line in run.stdout.splitlines() if line.startswith('{')]
            if len(rows) != 3 or any(row['cpu'] for row in rows):
                raise RuntimeError('Expected the three GPU workflows')
            raw.append({'mode': mode, 'run': repetition, 'build': build, 'rows': rows, 'adapter': '\n'.join(line for line in run.stderr.splitlines() if line.startswith('adapter:')), 'other_renderers_before': other_before, 'other_renderers_after': other_renderer_count()})
            args.out.with_suffix('.raw.json').write_text(json.dumps(raw, indent=2) + '\n')
            print(f'{mode} round {repetition + 1}/{args.runs}: {build}', flush=True)
summary = {
    'before': args.before_head,
    'after': args.after_head,
    'base': args.base,
    'fixture': '6000x4000 RGBA8 synthetic; default 1.5 MP proxy; 1000x700 offscreen frames and readback; warmed dragging excludes initial capture/upload and commit',
    'build': 'Rust 1.99.0 release; thin LTO; one codegen unit',
    'adapter_scope': args.adapter_note,
    'other_renderer_overlap_detected': any(row['other_renderers_before'] or row['other_renderers_after'] for row in raw),
    'runs_per_build_per_mode': args.runs,
    'binary_sha256': {build: hashlib.file_digest(getattr(args, build).open('rb'), 'sha256').hexdigest() for build in ['before', 'after']},
    'workflows': [],
}
for mode in ['integer', 'fractional']:
    for case in ['composite', 'red-all-visible', 'red-only']:
        metrics = {}
        for metric in ['geometry_ms', 'completed_frame_ms', 'warp_ms', 'completed_warp_frame_ms']:
            stats = {}
            for build in ['before', 'after']:
                samples = [value for run in raw if run['mode'] == mode and run['build'] == build for row in run['rows'] if row['case'] == case for value in row[metric]]
                samples.sort()
                stats[build] = {'n': len(samples), 'p50_ms': statistics.median(samples), 'p95_ms': samples[math.ceil(0.95 * len(samples)) - 1]}
            old = stats['before']['p50_ms']; new = stats['after']['p50_ms']
            stats['change_ms'] = new - old
            stats['change_percent'] = 100 * (new / old - 1) if old else None
            metrics[metric] = stats
        summary['workflows'].append({'mode': mode, 'case': case, 'metrics': metrics})
args.out.with_suffix('.summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2), flush=True)
