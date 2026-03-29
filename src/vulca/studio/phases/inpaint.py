"""InpaintPhase -- partial region redraw with Gemini blend."""
from __future__ import annotations

import base64
import json
import logging
import re
from pathlib import Path

from PIL import Image

logger = logging.getLogger("vulca.studio")


def crop_region(image_path: str, bbox: dict, *, output_dir: str = "") -> str:
    """Crop a region from image based on percentage bbox. Returns path to cropped image."""
    img = Image.open(image_path)
    x_px = int(img.width * bbox["x"] / 100)
    y_px = int(img.height * bbox["y"] / 100)
    w_px = int(img.width * bbox["w"] / 100)
    h_px = int(img.height * bbox["h"] / 100)

    cropped = img.crop((x_px, y_px, x_px + w_px, y_px + h_px))

    out_dir = Path(output_dir) if output_dir else Path(image_path).parent
    out_path = out_dir / f"crop_{Path(image_path).stem}.png"
    cropped.save(str(out_path))
    return str(out_path)


class InpaintPhase:
    """Handles region detection, cropping, repainting, and blending."""

    def build_repaint_prompt(self, *, instruction: str, tradition: str) -> str:
        """Build prompt for repainting a cropped region."""
        parts = [
            "You are repainting a specific region of an artwork.",
            "The full original artwork is provided for context.",
            "The cropped region to repaint is provided separately.",
            f"Tradition/style to maintain: {tradition}",
            f"Instruction: {instruction}",
            "",
            "Generate a replacement for this region that:",
            "1. Matches the style, color palette, and technique of the surrounding artwork",
            "2. Applies the user's instruction",
            "3. Will blend seamlessly when placed back into the original",
            "Output the repainted region at the same dimensions as the crop.",
        ]
        return "\n".join(parts)

    def build_blend_prompt(self, *, bbox: dict) -> str:
        """Build prompt for seamless blending."""
        return (
            f"Seamlessly blend this repainted region back into the original artwork. "
            f"Region position: top-left at ({bbox['x']}%, {bbox['y']}%), "
            f"size ({bbox['w']}% x {bbox['h']}%) of the image. "
            f"Ensure smooth color and texture transitions at all edges. No visible seams. "
            f"Output the complete blended artwork."
        )

    async def detect_region(self, image_path: str, description: str, *, api_key: str = "") -> dict:
        """Use VLM to resolve NL region description to bounding box."""
        import os
        import litellm
        from vulca._image import load_image_base64

        img_b64, mime = await load_image_base64(image_path)
        model = os.environ.get("VULCA_VLM_MODEL", "gemini/gemini-2.5-flash")

        resp = await litellm.acompletion(
            model=model,
            messages=[
                {"role": "system", "content": (
                    "Given this image, identify the bounding box for the region described. "
                    "Return ONLY a JSON object: "
                    '{"x": <int 0-100>, "y": <int 0-100>, "w": <int 1-100>, "h": <int 1-100>} '
                    "where values are percentages of image dimensions. x,y is top-left corner."
                )},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}},
                    {"type": "text", "text": f"Region: {description}"},
                ]},
            ],
            max_tokens=256,
            temperature=0.1,
            api_key=api_key or os.environ.get("GOOGLE_API_KEY", ""),
            timeout=30,
        )

        text = resp.choices[0].message.content.strip()
        match = re.search(r'\{[^}]+\}', text)
        if not match:
            raise ValueError(f"Could not parse bbox from VLM response: {text}")

        raw = json.loads(match.group())
        bbox = {
            "x": max(0, min(100, int(raw.get("x", 0)))),
            "y": max(0, min(100, int(raw.get("y", 0)))),
            "w": max(5, min(100, int(raw.get("w", 50)))),
            "h": max(5, min(100, int(raw.get("h", 50)))),
        }
        return bbox

    async def repaint(
        self,
        original_path: str,
        crop_path: str,
        *,
        instruction: str,
        tradition: str = "default",
        count: int = 4,
        output_dir: str = "",
        api_key: str = "",
    ) -> list[str]:
        """Generate repaint variants for the cropped region."""
        import os
        from vulca.providers import get_image_provider

        prompt = self.build_repaint_prompt(instruction=instruction, tradition=tradition)

        ref_b64 = ""
        try:
            ref_b64 = base64.b64encode(Path(original_path).read_bytes()).decode()
        except Exception:
            pass

        provider = get_image_provider("gemini", api_key=api_key or os.environ.get("GOOGLE_API_KEY", ""))
        out_dir = Path(output_dir) if output_dir else Path(original_path).parent
        out_dir.mkdir(parents=True, exist_ok=True)

        paths: list[str] = []
        for i in range(count):
            try:
                result = await provider.generate(
                    f"{prompt}\n\nVariant {i+1} of {count}.",
                    reference_image_b64=ref_b64,
                )
                ext = "png" if "png" in result.mime else "jpg"
                filepath = out_dir / f"repaint_v{i+1}.{ext}"
                filepath.write_bytes(base64.b64decode(result.image_b64))
                paths.append(str(filepath))
            except Exception as exc:
                logger.debug("Repaint variant %d failed: %s", i + 1, exc)

        return paths

    async def blend(
        self,
        original_path: str,
        repaint_path: str,
        *,
        bbox: dict,
        output_path: str = "",
        api_key: str = "",
    ) -> str:
        """Blend repainted region back into original via Gemini."""
        import os
        from vulca.providers import get_image_provider

        prompt = self.build_blend_prompt(bbox=bbox)
        ref_b64 = base64.b64encode(Path(original_path).read_bytes()).decode()

        provider = get_image_provider("gemini", api_key=api_key or os.environ.get("GOOGLE_API_KEY", ""))

        result = await provider.generate(
            prompt,
            reference_image_b64=ref_b64,
        )

        out = (
            Path(output_path)
            if output_path
            else Path(original_path).parent / f"blended_{Path(original_path).name}"
        )
        ext = "png" if "png" in result.mime else "jpg"
        if not str(out).endswith(ext):
            out = out.with_suffix(f".{ext}")
        out.write_bytes(base64.b64decode(result.image_b64))
        return str(out)


def is_coordinate_string(region: str) -> bool:
    """Check if region string looks like coordinates (4 comma-separated numbers)."""
    parts = [p.strip() for p in region.split(",")]
    if len(parts) != 4:
        return False
    return all(p.lstrip("-").isdigit() for p in parts)


def parse_region_coordinates(region: str) -> dict:
    """Parse 'x,y,w,h' coordinate string to bbox dict. All values 0-100, w/h >= 5."""
    parts = [int(p.strip()) for p in region.split(",")]
    if len(parts) != 4:
        raise ValueError(f"Expected 4 values (x,y,w,h), got {len(parts)}")

    x, y, w, h = parts
    for name, val in [("x", x), ("y", y), ("w", w), ("h", h)]:
        if val < 0 or val > 100:
            raise ValueError(f"{name}={val} out of range 0-100")
    if w < 5 or h < 5:
        raise ValueError(f"Region too small: w={w}, h={h} (minimum 5%)")

    return {"x": x, "y": y, "w": w, "h": h}
