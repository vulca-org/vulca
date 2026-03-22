# Evaluate Artwork

Evaluate an artwork image on L1-L5 cultural dimensions using VULCA.

TRIGGER when: user says "evaluate this artwork", "score this image", "check cultural accuracy", "vulca evaluate", provides an image file path and asks for feedback, or asks about cultural quality of an image.

## Instructions

When the user wants to evaluate an artwork:

1. Identify the image source (file path, URL, or ask the user)
2. Identify the tradition (ask if not specified, suggest based on context)
3. Call the `evaluate_artwork` MCP tool with the image path, tradition, and optionally `view: "detailed"` for full rationales
4. Present results clearly:
   - Overall score and tradition
   - L1-L5 dimension breakdown with scores
   - Key rationales (what's good, what needs improvement)
   - Actionable recommendations
5. If the score is low, suggest specific improvements based on the tradition's terminology and taboos

## Available Traditions

Cultural: chinese_xieyi, chinese_gongbi, japanese_traditional, islamic_geometric, watercolor, african_traditional, south_asian, western_academic
Design: contemporary_art, photography, brand_design, ui_ux_design

## Example

User: "Evaluate this ink painting for Chinese xieyi tradition"

Response flow:
1. Call `evaluate_artwork(image_path="painting.jpg", tradition="chinese_xieyi", view="detailed", format="markdown")`
2. Present the L1-L5 scores with rationale
3. Highlight cultural strengths/weaknesses
4. Suggest improvements using xieyi-specific terminology (e.g., "improve 留白", "strengthen 气韵生动")
