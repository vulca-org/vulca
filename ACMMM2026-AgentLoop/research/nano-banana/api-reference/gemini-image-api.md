# Gemini Image API 完整参考

> 来源: https://ai.google.dev/gemini-api/docs/image-generation
> 日期: 2026-02-27

## 可用模型

| 模型 | ID | 上下文 (in/out) | 特点 |
|------|-----|-----------------|------|
| NB2 | `gemini-3.1-flash-image-preview` | 128k/32k | 速度+质量均衡 |
| NB Pro | `gemini-3-pro-image-preview` | 65k/32k | 最高质量 |
| NB1 | `gemini-2.5-flash-image` | 1M/32k | 快速原型 |
| Gemini 2.0 Flash | `gemini-2.0-flash` | 1M/8k | 基础图像能力 |

## API 端点

### Python SDK
```python
from google import genai
from google.genai import types

client = genai.Client(api_key="YOUR_KEY")
response = client.models.generate_content(model=MODEL_ID, ...)
```

### REST API
```
POST https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent
Header: x-goog-api-key: YOUR_KEY
Content-Type: application/json
```

## GenerateContentConfig 参数

```python
types.GenerateContentConfig(
    # 必须包含 IMAGE 才能生成图像
    response_modalities=['TEXT', 'IMAGE'],

    # 图像配置
    image_config=types.ImageConfig(
        aspect_ratio="1:1",     # 16 种宽高比
        image_size="1K"         # "0.5K"|"1K"|"2K"|"4K"
    ),

    # Thinking 配置
    thinking_config=types.ThinkingConfig(
        thinking_level="High",      # "minimal"|"low"|"medium"|"high"
        include_thoughts=True       # 返回推理文本
    ),

    # 工具
    tools=[
        {"google_search": {}},      # Web + Image search grounding
    ],

    # 温度 (默认 1.0, 修改可能导致循环或质量下降)
    temperature=1.0,

    # 安全设置
    safety_settings=[...],
)
```

## 响应结构

```python
response.parts  # List[Part]

# Part 类型:
part.text              # str: 文本 (可含 thinking)
part.as_image()        # PIL.Image: 生成的图像
part.thought           # str: 中间推理步骤
part.thought_signature # bytes: 加密推理表示 (多轮用)
part.inline_data       # Raw data (REST API)
  .mime_type           # "image/png"
  .data                # base64 string
```

## 功能矩阵

| 功能 | NB2 | NB Pro | NB1 |
|------|-----|--------|-----|
| Text-to-Image | ✅ | ✅ | ✅ |
| Image Editing | ✅ | ✅ | ✅ |
| Multi-turn Chat | ✅ | ✅ | ✅ |
| Reference Images (max) | 14 | 11 | ~5 |
| Thinking Control | ✅ | ✅ | 隐式 |
| Web Grounding | ✅ (text+image) | ✅ (text) | ✅ (text) |
| 4K Output | ✅ | ✅ | ❌ |
| 0.5K Output | ✅ | ❌ | ❌ |
| Batch API | ✅ | ✅ | ✅ |
| SynthID Watermark | ✅ | ✅ | ✅ |

## 速率限制

| Tier | RPM | TPM | 备注 |
|------|-----|-----|------|
| Free | 2 | 32K | 仅测试用 |
| Pay-as-you-go | ~100 | ~1M | 视具体 tier |
| Enterprise | 自定义 | 自定义 | 需联系 |

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| "lowercase resolution" | 用了 "1k" | 改为 "1K" |
| 无图像返回 | 安全过滤器触发 | 调整 prompt 或 safety_settings |
| 429 Too Many Requests | 超出速率限制 | 等待或升级 tier |
| thought_signature error | 多轮中签名丢失 | 使用官方 SDK 自动处理 |

## Thought Signatures 机制

- Gemini 3 模型在多轮对话中使用 **加密推理表示** (thought signatures)
- 这些签名在轮次间传递，保持推理上下文
- 官方 SDK 自动处理（透明）
- REST API 需要手动传递 `thought_signature` 字段
- 对 image generation 是 **必须的** (strict validation)

## SynthID 水印

- 所有生成图像自动包含 SynthID 数字水印
- 不可见（不影响图像质量）
- 用于标识 AI 生成内容
- 无法通过 API 禁用
