# ComfyUI-VULCA

Cultural art evaluation and Brief-driven creative workflows for ComfyUI.

## Nodes

| Node | Description |
|------|-------------|
| **VULCA Brief** | Create a creative brief from text intent |
| **VULCA Concept** | Generate concept designs from a Brief |
| **VULCA Generate** | Generate artwork from a Brief |
| **VULCA Evaluate** | L1-L5 cultural evaluation |
| **VULCA Update** | Update Brief with natural language |

## Installation

1. Copy this folder to `ComfyUI/custom_nodes/comfyui-vulca/`
2. Install dependency: `pip install vulca>=0.7.0`
3. Restart ComfyUI

## Usage

Connect nodes in this order:
```
VULCA Brief → VULCA Concept → VULCA Generate → VULCA Evaluate
                                      ↑
                              VULCA Update (feedback loop)
```

## Requirements

- Python 3.10+
- `vulca>=0.7.0` (PyPI)
- ComfyUI (any recent version)
