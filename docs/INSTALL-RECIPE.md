# Vulca Install Recipe

Pragmatic install notes when Vulca is consumed via MCP + full orchestrated layer pipeline.

This file exists because the default `pip install vulca` install is sufficient
for core evaluate + create workflows, but the orchestrated decompose pipeline
(`layers_split(mode="orchestrated")`) has a multi-step setup that's easy to
miss. The obstacles this recipe documents were surfaced during the 2026-04-24
γ Scottish showcase session.

## Who this is for

If you only use `evaluate_artwork`, `generate_image`, or basic layer tools via
`regenerate` / `extract` / `vlm` modes — stop here, the pip install is enough.

If you want `layers_split(mode="orchestrated")` (the SOTA YOLO + Grounding DINO
+ SAM + SegFormer decompose pipeline) — keep reading.

## Prerequisites

- macOS (Apple Silicon) or Linux with CUDA or CPU
- ~2 GB free disk for SAM v1 checkpoint
- Python 3.10-3.13 (MCP server defaults to 3.11 via homebrew on macOS)

## Step 1 — Identify your MCP server's Python

The vulca-mcp entry point is a `#!/usr/bin/env python` shebang. On macOS +
homebrew it's typically `/opt/homebrew/opt/python@3.11/bin/python3.11`.

```bash
head -1 $(which vulca-mcp)
```

**Important:** your shell's `python3` may be a different version (e.g., 3.14).
Deps installed into shell Python are NOT visible to the MCP server. You must
install into the Python that `vulca-mcp` uses.

Remember the MCP Python for the rest of this recipe. Substitute `$MCP_PY` for
its path below.

## Step 2 — Install Vulca with [sam] extra

```bash
$MCP_PY -m pip install "vulca[sam,mcp,layers]"
```

This pulls:
- `segment-anything>=1.0` — Meta SAM v1 for orchestrated pipeline
- `timm>=1.0.0` — transformers timm_wrapper requires modern timm
- `torch>=2.0`, `Pillow`, `numpy` — core ML stack

**Known conflict warning:** if you also have `torchscale` installed, it pins
`timm==0.6.13` which conflicts with transformers 4.49's timm_wrapper expectation.
Tolerable since torchscale is not on orchestrated path; ignore the pip warning.

**Critical conflict — do NOT install `[sam,sam3]` together.** The `[sam]` extra
(EVF-SAM) requires `transformers==4.49`; the `[sam3]` extra requires
`transformers>=4.50`. Pip resolves to 4.50+, breaking EVF-SAM at import time.
Pick one extra per environment. v0.18.0 will resolve this via separate marker
guards; until then this is a hard pick-one constraint.

## Step 3 — Download SAM v1 checkpoint

The orchestrated pipeline references a hardcoded checkpoint path at
`/tmp/sam_vit_l.pth`. (Issue #N+5 tracks proper env-var override; v0.18.0.)

```bash
curl -L -o /tmp/sam_vit_l.pth \
  https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth
```

Expected size: ~1.19 GB. Verify:

```bash
ls -lh /tmp/sam_vit_l.pth
# -rw-r--r--  1 user wheel 1.2G
```

Note: `/tmp` is volatile on macOS — the file may be cleaned on reboot. Consider
symlinking from a persistent location if you reboot frequently:

```bash
mkdir -p ~/.cache/vulca && \
  mv /tmp/sam_vit_l.pth ~/.cache/vulca/sam_vit_l.pth && \
  ln -s ~/.cache/vulca/sam_vit_l.pth /tmp/sam_vit_l.pth
```

## Step 4 — Restart MCP after dep install

Python caches failed module imports at process lifetime. After installing new
deps, the MCP server must be restarted before the new packages are visible to
the running MCP tools. Two options:

- **Claude Code:** run `/mcp` and reload/restart the `vulca` server, OR exit
  and re-enter the session.
- **Standalone vulca-mcp:** kill and restart the `vulca-mcp` process.

**If you skip this step**, `layers_split(mode="orchestrated")` will continue
returning cached import failures (`No module named 'segment_anything'` or
`cannot import name 'ImageNetInfo' from 'timm.data'`) even though the deps are
installed.

## Step 5 — Verify

```python
from mcp__vulca import layers_split
# ... call orchestrated mode with a minimal plan
```

First orchestrated call cold-starts the 4 loaders (SAM + DINO + SegFormer +
YOLO) — expect 3-4 seconds of warm-up before the first decompose. Subsequent
calls are cached until `unload_models()` or MCP restart.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `No module named 'segment_anything'` | MCP Python env missing sam-v1 dep | Step 2 into correct Python |
| `cannot import name 'ImageNetInfo' from 'timm.data'` | timm too old (<1.0) in MCP env | Step 2 reinstall + Step 4 restart |
| `FileNotFoundError: '/tmp/sam_vit_l.pth'` | SAM checkpoint not downloaded | Step 3 |
| Changes from `pip install` don't take effect | Python import cache | Step 4 restart |
| Orchestrated pipeline OOMs on MPS | 1024×1024 + 4 loaders tight fit | resize image to ≤1024 long edge, then decompose |
| Repeat decompose slowdown | Hot-cached model weights bloat RSS | call `unload_models()` between images |

## See also

- Issue #N+5 — SAM 4-integration convergence (retire hardcoded paths)
- Issue #N+6 — MCP-level dep-probe + startup capability report
