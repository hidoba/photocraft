# Isolated channel transform: PR screenshots

Synthetic offscreen captures for the isolated-channel transform PR in storytold/photocraft.

- `before.png`: image before transforming the selected Green channel.
- `warp-shown.png`: Green warped with RGB visible; Red stays in place.
- `warp-hidden.png`: Green hidden during Warp; handles remain available and Red stays visible.
- `warp-revealed.png`: Green shown again with the same Warp geometry.
- `mask-eye.png`: mask transform with other channel visibility changed.

These are prepared visual test evidence from the earlier implementation, not fresh captures of the submitted commit. The images use synthetic strokes drawn for this change and contain no personal photos or third-party art. This standalone evidence branch is separate from the code PR.

Original screenshots generated for this contribution by Vlad Grankovsky with AI assistance; available under MIT OR Apache-2.0, matching PhotoCraft.

## Current-main verification — 2026-10-13

Upstream `6f85054288a564f9fbbccb99268ffdb34e581584` compared with PR head `2b32ad9fc0e779ab2071a8a9a647ce36e0527802`. Identical Rust harness; 24 MP synthetic RGBA8, RTX 3090/Vulkan, release thin LTO/one codegen unit, six interleaved runs per build and 54 measured frames per case. Completed offscreen frames include GPU readback; initial capture/upload and commit are excluded. Default reduced preview is 1.5 MP. Warp case is a sheared affine Bezier patch.

- `preview-gpu-upgrade-summary.json`: source commits/tree, binary hashes, per-case medians and p95.
- `preview-gpu-upgrade-raw.json`: all 12 runs.
- `preview-gpu-upgrade-compare-run.py`: interleaved runner for already-built binaries.
- `upgrade-*-warp.png`: fresh synthetic captures from the PR head, inspected after the measured runs.

Build `crates/ui-egui/examples/channel_transform_gpu_bench.rs` unchanged on both source versions with `cargo +1.99.0 build --release -p photocraft-ui-egui --example channel_transform_gpu_bench`. Use separate target directories (or clean changed workspace crates when switching checkouts) to avoid Cargo reusing the other source's artifacts. Copy the binaries to the runner's two `/tmp/photocraft-upgrade-gpu-*` paths. Run the Python runner only after Cargo/rustc have exited. `--save /tmp/channel-preview` on the candidate binary produces screenshots outside measured comparison runs.
