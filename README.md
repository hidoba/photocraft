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


## Current-main verification — 2026-10-14

Code PR head: `ad7d704789bcf5e87f603fedebec83c9c0b3301c`, on main `99e1138877e6aa7e856c6883b415e708d042fc59`.
The final committed source is byte-identical to the working tree validated after the two review fixes.
Engine/UI: 4,618 passed / 0 failed / 32 ignored (83 suites). Strict all-target Clippy, fmt, layers,
full wasm, adversarial commands and quick perf pass; the final release app has HEIF enabled.

The retained 24 MP comparison measures published `2b32ad9f` against `3e0cefc6` on main `99e11388`.
It uses the same GPU harness, Rust 1.99, thin LTO/one codegen unit, RTX 3090/Vulkan,
six interleaved runs per build and 54 frames per case. GPU rendering/readback are included;
initial capture/upload and full-resolution commit are excluded. The preview proxy is 1.5 MP.
The current head preserves the measured GPU implementation; its two additional review fixes
change eye normalization during background commit and Quick Mask proxy capture.

- `preview-local-rebase-summary.json`: measured source commits/tree, binary hashes, medians/p95.
- `preview-local-rebase-raw.json`: all twelve measured runs.
- `preview-local-rebase-compare-run.py`: runner for already-built binaries at the recorded commits.
- `local-rebase-*-warp.png`: inspected synthetic captures from measured `3e0cefc6`.
- `quick-mask-fix-*.png`: inspected 3000x2000/factor-2 Quick Mask affine/Warp preview and commit captures from the final validated source.
- `validated-head.json`: final committed source identity, local checks and release binary hash.

Build the unchanged `channel_transform_gpu_bench` example at the two measured commits using separate
target directories and the default release profile, then copy the binaries to the runner's `/tmp` paths.
Run only after Cargo/rustc have exited. For the Quick Mask captures, the snapshot harness's input
texture limit was set to 8192 for a 3000-pixel CPU canvas. The document and strokes are synthetic.

These timings apply to the measured affine RGB preview and affine-patch Warp path. The current-head
quick performance run reports `failures=[]`; no baseline, budget or aggregate parity number changed.
