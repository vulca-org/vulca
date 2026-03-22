# Create Artwork

Create culturally-guided artwork through the VULCA pipeline (Scout -> Draft -> Critic -> Decide).

TRIGGER when: user says "create artwork", "generate art", "vulca create", "make a painting", or describes an artwork they want to create with cultural context.

## Instructions

When the user wants to create an artwork:

1. Identify the intent (what to create)
2. Identify the tradition (ask if unclear)
3. Determine provider: suggest "gemini" for real generation (requires GOOGLE_API_KEY), "mock" for testing
4. Call the `create_artwork` MCP tool
5. Present results:
   - Pipeline status and rounds completed
   - L1-L5 scores from the Critic
   - Decision rationale (accept/rerun/stop)
   - If the image was generated, describe it
6. If HITL mode is requested, explain the paused state and available actions (accept/refine/reject)

## Provider Options

- `gemini` / `nb2`: Google Gemini image generation (needs GOOGLE_API_KEY)
- `openai`: DALL-E 3 (needs OPENAI_API_KEY)
- `comfyui`: Local Stable Diffusion (needs running ComfyUI server)
- `mock`: Deterministic SVG placeholder (no API key needed)

## Example

User: "Create a Chinese ink wash landscape in the style of Ni Zan"

Response flow:
1. Call `create_artwork(intent="Chinese ink wash landscape in Ni Zan style, dry brush, sparse composition", tradition="chinese_xieyi", provider="gemini")`
2. Show pipeline progress (generate -> evaluate -> decide)
3. Present L1-L5 scores and rationale
4. If score < threshold, explain what the Critic found and what would improve on the next round
