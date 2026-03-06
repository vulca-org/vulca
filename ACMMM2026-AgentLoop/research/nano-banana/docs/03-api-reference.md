# Nano Banana API 完整参考

## 1. 环境准备

### 安装
```bash
pip install google-genai
```

### 认证
```python
import os
from google import genai

# 方式 1：环境变量
os.environ["GOOGLE_API_KEY"] = "your-api-key"
client = genai.Client()

# 方式 2：直接传递
client = genai.Client(api_key="your-api-key")
```

---

## 2. 模型 ID 速查

| 模型 | Model ID | 备注 |
|------|----------|------|
| NB2 | `gemini-3.1-flash-image-preview` | **推荐使用** |
| NB Pro | `gemini-3-pro-image-preview` | 最高质量 |
| NB1 | `gemini-2.5-flash-image` | 旧版，仍可用 |

---

## 3. 文本生成图像（Text-to-Image）

### 基础用法
```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents="Chinese xieyi ink painting of bamboo expressing cosmic solitude",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
    )
)

# 解析响应
for part in response.parts:
    if part.text:
        print(part.text)
    elif image := part.as_image():
        image.save("output.png")  # PIL Image 对象
```

### 完整配置
```python
response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents="Your prompt here",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],

        # 图像配置
        image_config=types.ImageConfig(
            aspect_ratio="16:9",    # 见下方支持列表
            image_size="2K"         # "0.5K" | "1K" | "2K" | "4K"
        ),

        # Thinking 配置（NB2/Pro 支持）
        thinking_config=types.ThinkingConfig(
            thinking_level="High",       # "minimal" | "High"
            include_thoughts=True        # 返回推理过程
        ),

        # Web Grounding（可选）
        tools=[{"google_search": {}}],

        # 安全设置（可选）
        # safety_settings=...
    )
)
```

### 支持的宽高比
```
"1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1",
"4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9"
```

### 支持的分辨率
```
"0.5K" (512px)  — 仅 Flash 模型
"1K"   (1024px) — 所有模型
"2K"   (2048px) — 所有模型
"4K"   (4096px) — NB2 / Pro
```

**注意**：必须使用大写 "K"，如 "1K" 而非 "1k"。

---

## 4. 图像编辑（Image Editing）

### 基于文本指令编辑现有图像
```python
from PIL import Image

# 加载原始图像
original = Image.open("input.jpg")

response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents=[
        "Add traditional Chinese seal stamp in the bottom-right corner",
        original  # PIL Image 对象
    ],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
    )
)

for part in response.parts:
    if image := part.as_image():
        image.save("edited.png")
```

---

## 5. 多轮对话编辑（Multi-Turn Editing）

```python
# 使用 chat 接口进行迭代编辑
chat = client.chats.create(
    model="gemini-3.1-flash-image-preview",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
    )
)

# 第一轮：生成
response1 = chat.send_message("Chinese xieyi painting of mountains with mist")
img1 = None
for part in response1.parts:
    if image := part.as_image():
        img1 = image
        image.save("round1.png")

# 第二轮：编辑
response2 = chat.send_message("Add a solitary scholar figure in the foreground")
for part in response2.parts:
    if image := part.as_image():
        image.save("round2.png")

# 第三轮：进一步修改
response3 = chat.send_message("Make the mist thicker and add calligraphy text '山高水长'")
for part in response3.parts:
    if image := part.as_image():
        image.save("round3.png")
```

**关键**：Multi-turn 通过 **thought signatures**（加密推理表示）在轮次间保持上下文。官方 SDK 自动处理。

---

## 6. 参考图像（Reference Images）

```python
ref_image1 = Image.open("style_reference.jpg")
ref_image2 = Image.open("composition_reference.jpg")

response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents=[
        "Create a new painting in the style of the first image, "
        "with the composition layout of the second image",
        ref_image1,
        ref_image2
    ],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
    )
)
```

**参考图像上限**：
| 模型 | 物体图像 | 角色图像 | 总计 |
|------|---------|---------|------|
| NB2 (Flash) | 10 | 4 | 14 |
| NB Pro | 6 | 5 | 11 |

---

## 7. Web Grounding（搜索增强）

```python
response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents="A realistic photo of the Forbidden City in winter snow",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        tools=[{"google_search": {}}]  # 启用搜索
    )
)
```

NB2 独有功能：**Image Search Grounding** — 不仅搜索文本，还搜索图像参考。

---

## 8. 响应格式

### 响应结构
```python
response.parts  # List of Part objects

# Part 类型：
part.text            # str: 文本内容（可能包含 thinking）
part.as_image()      # PIL.Image: 图像内容
part.thought         # str: 中间推理步骤（if include_thoughts=True）
part.thought_signature  # bytes: 加密推理表示（多轮用）
```

### REST API 响应（JSON）
```json
{
  "candidates": [{
    "content": {
      "parts": [
        {"text": "Here's the generated image..."},
        {"inlineData": {
          "mimeType": "image/png",
          "data": "<base64-encoded-image>"
        }}
      ]
    }
  }]
}
```

---

## 9. 批量处理（Batch API）

```python
# 批量模式：24小时内完成，价格减半
batch_response = client.batches.create(
    model="gemini-3.1-flash-image-preview",
    requests=[
        {"contents": "Prompt 1", ...},
        {"contents": "Prompt 2", ...},
        # ...
    ]
)
```

批量定价：所有分辨率均为标准价格的 50%。

---

## 10. Rate Limits

| Tier | RPM | TPM |
|------|-----|-----|
| Free | 2 | 32K |
| Paid | 100+ | 视 tier |

---

## 11. 最佳实践

### Prompt 编写
1. **描述场景，不要罗列关键词**：
   - ✗ "bamboo, ink, Chinese, xieyi"
   - ✓ "A Chinese xieyi ink painting of bamboo swaying in autumn wind, with expressive brushstrokes conveying cosmic solitude"
2. **文字渲染**：用引号包裹文字，指定位置
   - ✓ `"Write 'Hello World' centered at the top"`
3. **每张图限 3-5 个文字元素**
4. **使用标准字体描述获得最佳结果**

### 成本优化
1. 先用 0.5K/1K 生成多个变体
2. 选出最佳候选后再以目标分辨率重新生成
3. 批量模式半价

### 错误处理
```python
try:
    response = client.models.generate_content(...)
    for part in response.parts:
        if image := part.as_image():
            image.save("output.png")
            break
    else:
        print("No image in response — may have been filtered by safety")
except Exception as e:
    print(f"Generation failed: {e}")
```
