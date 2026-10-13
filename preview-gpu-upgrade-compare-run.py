#!/usr/bin/env python3
"""Run already-built, identical GPU benchmark harnesses without a concurrent Cargo build."""
import hashlib
import os
import json
import math
from pathlib import Path
import statistics
import subprocess
import time

active = subprocess.check_output(["ps", "-eo", "comm="], text=True).splitlines()
assert not ({"cargo", "rustc"} & {name.strip() for name in active}), "Wait for active Cargo/rustc processes before measuring"
assert subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() == "2b32ad9fc0e779ab2071a8a9a647ce36e0527802"
root = Path(__file__).resolve().parent
bins = {"upstream": "/tmp/photocraft-upgrade-gpu-upstream", "candidate": "/tmp/photocraft-upgrade-gpu-candidate"}
results = []
for iteration, version in enumerate(["upstream", "candidate", "candidate", "upstream", "upstream", "candidate", "candidate", "upstream", "upstream", "candidate", "candidate", "upstream"]):
    with (root / f"preview-gpu-upgrade-{iteration}-{version}.log").open("w") as log:
        run = subprocess.run([bins[version]], stdout=subprocess.PIPE, stderr=log, text=True, check=True, env=dict(os.environ, WGPU_BACKEND='vulkan', VK_DRIVER_FILES='/usr/share/vulkan/icd.d/nvidia_icd.json'))
    cases = [json.loads(line) for line in run.stdout.splitlines() if line.startswith("{")]
    assert len(cases) == 3, run.stdout
    results.append({"iteration": iteration, "version": version, "cases": cases})
    (root / "preview-gpu-upgrade-raw.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"{iteration + 1}/12: {version}", flush=True)
summary = {}
for version in bins:
    summary[version] = {}
    for case in ["composite", "red-all-visible", "red-only"]:
        summary[version][case] = {}
        for metric in ["geometry_ms", "completed_frame_ms", "warp_ms", "completed_warp_frame_ms"]:
            samples = sorted(v for run in results if run["version"] == version for row in run["cases"] if row["case"] == case for v in row[metric])
            summary[version][case][metric] = dict(n=len(samples), median=statistics.median(samples), p95=samples[math.ceil(.95*len(samples))-1], minimum=min(samples), maximum=max(samples))
metadata = dict(candidate_tree=subprocess.check_output(['git', 'write-tree'], text=True).strip(), upstream="6f85054288a564f9fbbccb99268ffdb34e581584", candidate_commit="2b32ad9fc0e779ab2071a8a9a647ce36e0527802", toolchain="Rust 1.99.0", profile="release thin-LTO, one codegen unit", image="synthetic 6000x4000 RGBA8", harness="1000x700 offscreen wgpu with project adapter setup", caveat="Completed frames include GPU rendering and readback; these are not native input-to-display latency. Upstream incorrectly transforms the whole layer for colour targets.", binaries={k: hashlib.sha256(Path(v).read_bytes()).hexdigest() for k,v in bins.items()})
(root / "preview-gpu-upgrade-summary.json").write_text(json.dumps(dict(metadata=metadata, results=summary), indent=2) + "\n")
for version, cases in summary.items():
    for case, metrics in cases.items():
        print(version, case, {k: round(v["median"], 3) for k,v in metrics.items()})
