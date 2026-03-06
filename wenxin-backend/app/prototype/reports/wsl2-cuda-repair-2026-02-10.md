# WSL2 CUDA Repair Report (2026-02-10)

## Scope
- Recover broken backend Python environment after interrupted install/shutdown.
- Rebuild V2 prototype runtime dependencies.
- Verify CUDA visibility in WSL2 for local V2 workflow.

## Completed Repairs
- Rebuilt backend venv and repointed project link:
  - `wenxin-backend/venv -> /home/yhryzy/.venvs/wenxin-backend-v2-venv`
- Installed CUDA PyTorch stack:
  - `torch==2.6.0+cu124`
  - `torchvision==0.21.0+cu124`
  - `torchaudio==2.6.0+cu124`
- Installed V2 core packages:
  - `litellm==1.81.9`, `langgraph==1.0.8`, `langgraph-checkpoint==4.0.0`
  - `diffusers==0.36.0`, `accelerate==1.12.0`, `safetensors==0.6.2`, `peft==0.18.1`
  - `faiss-cpu==1.13.2`, `sentence-transformers==5.2.2`, `gradio==6.5.0`
- Installed observability/eval packages:
  - `crewai==1.2.0`, `langfuse==3.9.0`, `deepeval==3.7.2`
- Restored backend startup prerequisites:
  - `python-jose[cryptography]==3.5.0`, `passlib[bcrypt]==1.7.4`, `bcrypt==4.0.1`,
    `email-validator==2.2.0`, `aiosmtplib==3.0.2`

## Validation Results
- `validate_draft_refine.py`: **28/28 passed**
- `validate_scout_faiss.py`: **29/29 passed** (with offline HF cache)
- `validate_orchestrator.py`: **48/48 passed** (with offline HF cache)
- `uvicorn app.main:app` startup: **success** (see `/tmp/v2_uvicorn2.log`)

## Current Blocker (Host-Level)
- `nvidia-smi` in WSL currently returns:
  - `Failed to initialize NVML: N/A`
- PyTorch reports:
  - `torch.cuda.is_available() == False`
  - Error 304 (`OS call failed or operation not supported on this OS`)
- This is a WSL GPU bridge/runtime state issue (not Python dependency issue).

## Re-Test After User Actions (2026-02-11)
- User already executed:
  - `wsl --shutdown`
  - `wsl --update`
- Re-test results:
  - `nvidia-smi`: still `Failed to initialize NVML: N/A`
  - `torch.cuda.is_available()`: still `False`
  - `validate_draft_refine.py`: still **28/28 passed** (CPU path healthy)
- Additional diagnostics:
  - `/etc/fstab` invalid `H:` mount is now commented.
  - `dmesg` still shows dxg ioctl failures (`dxgkio_query_adapter_info: -22`).
  - This confirms app/runtime layer is healthy; blocker remains host-side WSL GPU bridge.

## Required Next Step (Outside Python)
Run in Windows PowerShell:

```powershell
wsl --shutdown
```

Then reopen WSL and verify:

```bash
nvidia-smi
cd <project-root>/wenxin-backend
venv/bin/python - <<'PY'
import torch
print(torch.__version__)
print(torch.cuda.is_available(), torch.cuda.device_count())
if torch.cuda.is_available():
    print(torch.cuda.get_device_name(0))
PY
```

If NVML still fails after `wsl --shutdown`, run the following host recovery sequence:

```powershell
# Admin PowerShell
Restart-Service LxssManager
wsl --shutdown
wsl --update --web-download
```

Then reboot Windows once and retest.

## Notes
- First run of FAISS/SentenceTransformer can be DNS-sensitive. For stable offline runs:
  - `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`
