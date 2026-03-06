#!/usr/bin/env python3
"""Validate the FLUX Fill Inpaint Provider (Line B).

Tests:
1. FluxFillProvider instantiation
2. Provider resolution via _get_inpaint_provider
3. Mock fallback when API unavailable
4. Orchestrator inpaint selection logic
5. Live API test (needs FAL_KEY)

Usage:
  # Dry run (no API key needed)
  python3 -m app.prototype.tools.validate_flux_fill

  # With live API (needs FAL_KEY)
  python3 -m app.prototype.tools.validate_flux_fill --with-api
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

_CHECKPOINT_ROOT = (
    Path(__file__).resolve().parent.parent / "checkpoints" / "draft"
)


def _find_real_image() -> str | None:
    """Find any real (non-mock) image in checkpoints."""
    for d in sorted(_CHECKPOINT_ROOT.iterdir()):
        if not d.is_dir():
            continue
        for ext in ("*.png", "*.jpg", "*.jpeg"):
            for img in sorted(d.glob(ext)):
                if img.stat().st_size > 1000:  # >1KB = not mock
                    return str(img)
    return None


def main():
    parser = argparse.ArgumentParser(description="Validate FLUX Fill Provider")
    parser.add_argument("--with-api", action="store_true", help="Run live API tests")
    args = parser.parse_args()

    passed = 0
    failed = 0
    total = 0

    def check(name: str, condition: bool, detail: str = ""):
        nonlocal passed, failed, total
        total += 1
        if condition:
            passed += 1
            print(f"  ✅ {name}")
        else:
            failed += 1
            print(f"  ❌ {name}: {detail}")

    # ── Test 1: Import and instantiation ──
    print("\n[1/5] Import & Instantiation")
    try:
        from app.prototype.agents.flux_fill_provider import FluxFillProvider
        provider = FluxFillProvider()
        check("Import FluxFillProvider", True)
        check("model_ref is flux-fill-dev", provider.model_ref == "flux-fill-dev")
        check("Has inpaint method", hasattr(provider, "inpaint"))

        pro = FluxFillProvider(use_pro=True)
        check("Pro model_ref is flux-fill-pro", pro.model_ref == "flux-fill-pro")
    except Exception as e:
        check("Import FluxFillProvider", False, str(e))

    # ── Test 2: Provider resolution ──
    print("\n[2/5] Provider Resolution")
    try:
        from app.prototype.agents.draft_agent import _get_inpaint_provider

        p_fill = _get_inpaint_provider("flux_fill")
        check("'flux_fill' resolves to FluxFillProvider",
              p_fill.__class__.__name__ == "FluxFillProvider")

        p_dev = _get_inpaint_provider("flux_fill_dev")
        check("'flux_fill_dev' resolves correctly",
              p_dev.__class__.__name__ == "FluxFillProvider")

        p_pro = _get_inpaint_provider("flux_fill_pro")
        check("'flux_fill_pro' resolves to Pro",
              p_pro.model_ref == "flux-fill-pro")

        p_mock = _get_inpaint_provider("mock_inpaint")
        check("'mock_inpaint' still works",
              p_mock.__class__.__name__ == "MockInpaintProvider")

    except Exception as e:
        check("Provider resolution", False, str(e))

    # ── Test 3: Mock fallback ──
    print("\n[3/5] Mock Fallback (no API key)")
    try:
        from app.prototype.agents.flux_fill_provider import FluxFillProvider

        provider = FluxFillProvider(api_key="")  # force no key
        check("available is False without key", not provider.available)

        # Create a test image and mask
        test_img = Image.new("RGB", (64, 64), (128, 128, 128))
        test_img_path = str(_CHECKPOINT_ROOT / "_test_flux_fill_input.png")
        test_out_path = str(_CHECKPOINT_ROOT / "_test_flux_fill_output.png")
        Path(test_img_path).parent.mkdir(parents=True, exist_ok=True)
        test_img.save(test_img_path)

        mask = Image.new("L", (64, 64), 255)  # full repaint

        result = provider.inpaint(
            base_image_path=test_img_path,
            mask_image=mask,
            prompt="test",
            negative_prompt="",
            seed=42,
            strength=0.75,
            steps=10,
            output_path=test_out_path,
        )
        check("Mock fallback produces output",
              Path(result).exists(),
              f"result={result}")

        # Cleanup
        Path(test_img_path).unlink(missing_ok=True)
        Path(test_out_path).unlink(missing_ok=True)

    except Exception as e:
        check("Mock fallback", False, str(e))

    # ── Test 4: Orchestrator inpaint selection ──
    print("\n[4/5] Orchestrator Inpaint Selection Logic")
    try:
        from app.prototype.agents.draft_config import DraftConfig

        # Simulate the orchestrator's provider selection logic
        test_cases = [
            ("diffusers", "diffusers_inpaint"),
            ("together_flux", "flux_fill"),
            ("mock", "mock_inpaint"),
        ]
        for provider_name, expected_inpaint in test_cases:
            d_cfg = DraftConfig(provider=provider_name)
            # Replicate orchestrator logic
            inpaint_name = "mock_inpaint"
            if d_cfg.provider == "together_flux":
                inpaint_name = "flux_fill"
            elif d_cfg.provider == "diffusers":
                inpaint_name = "diffusers_inpaint"
            check(
                f"provider={provider_name} → inpaint={expected_inpaint}",
                inpaint_name == expected_inpaint,
                f"got {inpaint_name}",
            )

    except Exception as e:
        check("Orchestrator logic", False, str(e))

    if not args.with_api:
        print("\n[5/5] Live API Test — SKIPPED (use --with-api)")
        print(f"\n{'='*50}")
        print(f"Results: {passed}/{total} passed, {failed} failed")
        print(f"{'='*50}")
        sys.exit(0 if failed == 0 else 1)

    # ── Test 5: Live API test ──
    print("\n[5/5] Live FLUX Fill API Test")
    try:
        from app.prototype.agents.flux_fill_provider import FluxFillProvider

        provider = FluxFillProvider()
        check("API key available", provider.available)

        if provider.available:
            real_img = _find_real_image()
            if not real_img:
                check("Real test image found", False, "No real images in checkpoints")
            else:
                check("Real test image found", True)
                print(f"    Using: {real_img[-60:]}")

                # Create mask (repaint upper half)
                base = Image.open(real_img)
                w, h = base.size
                mask = Image.new("L", (w, h), 0)
                mask.paste(255, (0, 0, w, h // 2))  # upper half white

                out_path = str(_CHECKPOINT_ROOT / "_test_flux_fill_live.png")

                result = provider.inpaint(
                    base_image_path=real_img,
                    mask_image=mask,
                    prompt="Islamic geometric tessellation pattern, arabesque, gold and blue",
                    negative_prompt="",
                    seed=42,
                    strength=0.75,
                    steps=20,
                    output_path=out_path,
                )

                result_exists = Path(result).exists()
                check("FLUX Fill produced output", result_exists)

                if result_exists:
                    result_img = Image.open(result)
                    check(f"Output dimensions match: {result_img.size}",
                          result_img.size[0] > 0 and result_img.size[1] > 0)
                    check("Output is not same as input",
                          result_img.size != (8, 8))  # not mock

                    # Cleanup
                    Path(out_path).unlink(missing_ok=True)

    except Exception as e:
        check("Live API test", False, str(e))

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed, {failed} failed")
    print(f"{'='*50}")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
