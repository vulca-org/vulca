"""
NB2 (Nano Banana 2) Draft Provider 草稿代码
用于集成到 VULCA-Agent 的 Draft Agent

Model: gemini-3.1-flash-image-preview
依赖: pip install google-genai Pillow

注意: 这是草稿代码，需要适配到 VULCA-Agent 的 DraftProvider 接口
"""

import os
import io
import base64
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ============================================================
# 基础用法示例
# ============================================================

def basic_generation():
    """最简单的 NB2 图像生成"""
    from google import genai
    from google.genai import types

    client = genai.Client()  # 从 GOOGLE_API_KEY 环境变量读取

    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents="Chinese xieyi ink painting of bamboo expressing cosmic solitude",
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=types.ImageConfig(
                aspect_ratio="1:1",
                image_size="1K"
            ),
        )
    )

    for part in response.parts:
        if part.text:
            print(f"[NB2 Thinking]: {part.text[:200]}")
        elif image := part.as_image():
            image.save("output.png")
            print("Image saved to output.png")


# ============================================================
# 带 Thinking 控制的高质量生成
# ============================================================

def generation_with_thinking(prompt: str, thinking_level: str = "High"):
    """使用 thinking 机制的高质量生成"""
    from google import genai
    from google.genai import types

    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=types.ImageConfig(
                aspect_ratio="1:1",
                image_size="1K"
            ),
            thinking_config=types.ThinkingConfig(
                thinking_level=thinking_level,  # "minimal" | "High"
                include_thoughts=True
            ),
        )
    )

    thinking_text = ""
    result_image = None

    for part in response.parts:
        if part.text:
            thinking_text += part.text + "\n"
        elif image := part.as_image():
            result_image = image

    return result_image, thinking_text


# ============================================================
# 多轮编辑（利用 NB2 的 chat 能力）
# ============================================================

def multi_turn_editing():
    """使用 multi-turn chat 进行迭代编辑"""
    from google import genai
    from google.genai import types

    client = genai.Client()

    chat = client.chats.create(
        model="gemini-3.1-flash-image-preview",
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=types.ImageConfig(
                aspect_ratio="1:1",
                image_size="1K"
            ),
        )
    )

    # Round 1: 初始生成
    r1 = chat.send_message(
        "Chinese xieyi ink painting of mountains with mist, "
        "expressing the concept of 留白 (empty space as philosophy)"
    )
    img1 = _extract_image(r1)
    if img1:
        img1.save("round1.png")

    # Round 2: 文化修正（测试 NB2 能否理解 L3-L5 指令）
    r2 = chat.send_message(
        "The brushwork should be more expressive (意筆/yibi style). "
        "Reduce photorealistic details. "
        "The empty space should feel intentional, not just blank."
    )
    img2 = _extract_image(r2)
    if img2:
        img2.save("round2.png")

    # Round 3: 进一步修正
    r3 = chat.send_message(
        "Add subtle calligraphic elements suggesting cosmic solitude. "
        "The overall feeling should evoke 天人合一 (unity of heaven and humanity)."
    )
    img3 = _extract_image(r3)
    if img3:
        img3.save("round3.png")

    return [img1, img2, img3]


def _extract_image(response):
    """从响应中提取 PIL Image"""
    for part in response.parts:
        if image := part.as_image():
            return image
    return None


# ============================================================
# VULCA-Agent DraftProvider 接口草稿
# ============================================================

class NB2DraftProvider:
    """
    Nano Banana 2 作为 VULCA-Agent 的 Draft Provider

    需要适配到:
      wenxin-backend/app/prototype/agents/draft_agent.py
      wenxin-backend/app/prototype/pipeline/inpaint_provider.py

    接口:
      generate(prompt, n_candidates, evidence_pack) -> List[PIL.Image]
    """

    MODEL_ID = "gemini-3.1-flash-image-preview"

    def __init__(
        self,
        api_key: Optional[str] = None,
        image_size: str = "1K",
        aspect_ratio: str = "1:1",
        thinking_level: str = "High",
        use_grounding: bool = False,
    ):
        from google import genai
        from google.genai import types

        self.types = types
        self.image_size = image_size
        self.aspect_ratio = aspect_ratio
        self.thinking_level = thinking_level
        self.use_grounding = use_grounding

        key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not key:
            raise ValueError("GOOGLE_API_KEY not set")
        self.client = genai.Client(api_key=key)

    def generate(
        self,
        prompt: str,
        n_candidates: int = 4,
        evidence_pack: Optional[dict] = None,
    ) -> list:
        """
        生成 n 个候选图像

        Args:
            prompt: 基础 prompt
            n_candidates: 候选数量
            evidence_pack: VULCA EvidencePack (可选)

        Returns:
            List of PIL.Image objects
        """
        # 将 EvidencePack 融入 prompt
        enriched_prompt = self._enrich_prompt(prompt, evidence_pack)

        candidates = []
        for i in range(n_candidates):
            try:
                image, thinking = self._generate_one(enriched_prompt)
                if image:
                    candidates.append(image)
                    logger.info(
                        f"NB2 candidate {i+1}/{n_candidates} generated. "
                        f"Thinking: {thinking[:100]}..."
                    )
            except Exception as e:
                logger.warning(f"NB2 candidate {i+1} failed: {e}")

        return candidates

    def _enrich_prompt(self, prompt: str, evidence_pack: Optional[dict]) -> str:
        """将 EvidencePack 的文化约束融入 prompt"""
        if not evidence_pack:
            return prompt

        parts = [prompt]

        # 添加风格指令
        if style := evidence_pack.get("style_directives"):
            parts.append(f"Style requirements: {', '.join(style)}")

        # 添加锚定术语
        if anchors := evidence_pack.get("anchor_terms"):
            terms = [f"{t['term']} ({t.get('description', '')})" for t in anchors[:5]]
            parts.append(f"Cultural terms to incorporate: {'; '.join(terms)}")

        # 添加构图约束
        if composition := evidence_pack.get("composition_constraints"):
            parts.append(f"Composition: {composition}")

        # 添加禁忌警告
        if taboos := evidence_pack.get("taboo_warnings"):
            parts.append(f"AVOID: {', '.join(taboos)}")

        return ". ".join(parts)

    def _generate_one(self, prompt: str):
        """生成单张图像"""
        tools = []
        if self.use_grounding:
            tools.append({"google_search": {}})

        config = self.types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=self.types.ImageConfig(
                aspect_ratio=self.aspect_ratio,
                image_size=self.image_size,
            ),
            thinking_config=self.types.ThinkingConfig(
                thinking_level=self.thinking_level,
                include_thoughts=True,
            ),
        )
        if tools:
            config.tools = tools

        response = self.client.models.generate_content(
            model=self.MODEL_ID,
            contents=prompt,
            config=config,
        )

        thinking_text = ""
        result_image = None

        for part in response.parts:
            if part.text:
                thinking_text += part.text
            elif image := part.as_image():
                result_image = image

        return result_image, thinking_text

    def image_to_base64(self, image) -> str:
        """将 PIL Image 转为 base64（供 VULCA Critic 使用）"""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()


# ============================================================
# 快速验证脚本
# ============================================================

if __name__ == "__main__":
    import sys

    # 检查 API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("ERROR: Set GOOGLE_API_KEY environment variable")
        print("Get key from: https://aistudio.google.com/")
        sys.exit(1)

    # 测试 1: 基础生成
    print("=== Test 1: Basic generation ===")
    provider = NB2DraftProvider(image_size="0.5K", thinking_level="minimal")

    # VULCA-style cultural prompt
    test_prompt = (
        "Bada Shanren style ink painting of two fish, "
        "expressing cosmic solitude through minimalist brushwork"
    )

    # 模拟 EvidencePack
    mock_evidence = {
        "style_directives": ["xieyi style", "expressive brushwork", "留白"],
        "anchor_terms": [
            {"term": "意笔 (yibi)", "description": "meaning-laden brushwork"},
            {"term": "留白 (liu bai)", "description": "intentional empty space"},
        ],
        "composition_constraints": "Asymmetric composition with generous empty space",
        "taboo_warnings": ["photorealistic rendering", "Western perspective grid"],
    }

    images = provider.generate(
        test_prompt,
        n_candidates=2,
        evidence_pack=mock_evidence,
    )

    for i, img in enumerate(images):
        path = f"nb2_test_{i+1}.png"
        img.save(path)
        print(f"  Saved {path}: {img.size}")

    print(f"\n=== Generated {len(images)} candidates ===")
    print(f"=== Cost estimate: ~${len(images) * 0.045:.3f} (0.5K) ===")
