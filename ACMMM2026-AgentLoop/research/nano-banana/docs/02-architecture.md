# Nano Banana 核心架构深度解析

## 1. NB1 架构：Autoregressive Multimodal

### 1.1 不是纯 Diffusion

NB1 的最重要技术发现：它是 **autoregressive**（自回归），不是纯 diffusion。

```
传统 Diffusion (SD, FLUX, Imagen):
  Noise → 逐步去噪 → Image

NB1 Autoregressive:
  Prompt → Token₁ → Token₂ → ... → Token₁₂₉₀ → Decode → Image
```

每张图像被表示为 ~1,290 tokens，模型像生成文本一样逐 token 预测，然后解码成像素。

### 1.2 Multimodal Diffusion Transformer (MMDiT)

- **参数量**：450M - 8B（Sparse MoE，依任务缩放）
- **处理块**：15-38 blocks
- **训练**：多模态联合训练（文本+图像+音频+视频+代码），非后嫁接
- **MoE 机制**：不同参数子集为不同任务（文本理解 vs 图像生成 vs 编辑）激活

### 1.3 Thinking 机制（NB1 原始版本）

NB1 已经有 implicit thinking：
- 在生成前会产生 "interim images"（中间试探图）
- 测试构图和逻辑
- 这些中间图不计费
- 但这个 thinking 是黑盒的，用户无法观察或控制

---

## 2. NB Pro 架构：Deep Inference

### 2.1 双组件设计

```
┌──────────────┐     ┌──────────────┐
│  Gemini 3    │     │   GemPix     │
│  Pro 推理层   │────→│  Diffusion   │
│  (Brain)     │     │  Head (Hand) │
└──────────────┘     └──────────────┘
       ↕                    ↕
  理解 prompt           渲染像素
  空间关系规划           纹理细节
  光照物理推理           色彩一致性
  创意意图解析           风格执行
```

### 2.2 Deep Inference Mode

NB Pro "thinks through" generation：
1. **空间关系推理**：物体相对位置、遮挡、透视
2. **光照物理**：光源方向、阴影投射、反射
3. **构图规则**：三分法、黄金比例、视觉引导线
4. **创意意图**：区分字面 vs 隐喻、风格 vs 内容

这个过程需要 8-12 秒，但质量显著优于 NB1。

---

## 3. NB2 架构：Plan-Evaluate-Improve Loop

### 3.1 核心创新：Shared Latent Intent Vector

NB2 的架构突破是在 LLM 推理层和 Diffusion 执行层之间建立了 **shared latent intent vector**（共享隐意图向量）：

```
┌─────────────────────────────────────────────────┐
│              Shared Latent Intent Vector          │
│   ┌─────────┐                    ┌─────────┐    │
│   │ Gemini  │◄──── latent ─────►│ GemPix  │    │
│   │ 3 Pro   │    intent bridge   │    2    │    │
│   │ (Brain) │                    │ (Hand)  │    │
│   └─────────┘                    └─────────┘    │
│    LLM推理:                      Diffusion执行:  │
│    - Prompt 解析                 - 像素合成       │
│    - 空间规划                    - 纹理渲染       │
│    - 逻辑验证                    - 风格执行       │
│    - 错误检测                    - 分辨率缩放     │
└─────────────────────────────────────────────────┘
```

**latent intent vector 的作用**：
- 不是简单的 text embedding 传递
- 而是将 LLM 的推理状态（理解了什么、规划了什么、验证了什么）编码为连续向量
- Diffusion Head 在去噪过程中受此向量引导
- LLM 可以在 Diffusion 生成中途 "读回" 中间结果并调整 vector

### 3.2 五阶段生成管线

```
┌─────────────────────────────────────────────────────────────┐
│                     NB2 Generation Pipeline                  │
│                                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐               │
│  │ ① PLAN   │──→│ ② GENERATE│──→│ ③ REVIEW │               │
│  │          │   │          │   │          │               │
│  │ 解析prompt│   │ GemPix 2 │   │ LLM验证  │               │
│  │ 构图规划  │   │ Diffusion│   │ vs Plan  │               │
│  │ 空间布局  │   │ Head执行 │   │          │               │
│  │ 文字布局  │   │          │   │          │               │
│  │ 技术约束  │   │          │   │          │               │
│  └──────────┘   └──────────┘   └────┬─────┘               │
│                                      │                      │
│                              通过？──┼──→ ⑤ OUTPUT         │
│                                │     │                      │
│                                ✗     │                      │
│                                ▼     │                      │
│                          ┌──────────┐│                      │
│                          │④ CORRECT ││                      │
│                          │          ││                      │
│                          │ 定向反馈  ││                      │
│                          │ "文字错误"││                      │
│                          │ "空间不对"││                      │
│                          └────┬─────┘│                      │
│                               │      │                      │
│                               └──→ ② │(loop back)          │
│                                      │                      │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 各阶段技术细节

#### ① Planning Phase

**输入**：用户 prompt + 可选参考图像 + thinking config
**处理**：
- LLM 推理层解析 prompt 意图（字面 vs 隐喻）
- 创建 **structured generation plan**：
  - 必需文字元素及其位置
  - 空间关系图（前景/中景/背景/相对位置）
  - 视觉层次（主体/辅助/背景）
  - 技术约束（分辨率/宽高比/风格）
- 如果启用 web grounding：Google Search 检索真实世界参考

**Thinking 控制参数**：
```python
thinking_config=types.ThinkingConfig(
    thinking_level="High",       # "minimal" | "High"
    include_thoughts=True        # 返回中间推理文本
)
```
- `minimal`：快速规划，适合简单 prompt
- `High`：深度推理，复杂场景/精确文字/多角色

#### ② Generation Phase

**执行者**：GemPix 2 Diffusion Head
**输入**：latent intent vector（来自 Plan）
**过程**：
- 基于 plan 中的 latent intent 进行有引导的扩散过程
- 可能采用 "latent-space + learned upscaler" 架构：
  - 先生成低分辨率布局（draft）
  - 然后通过 learned super-resolution 提升到目标分辨率
- 不同分辨率的时间开销：
  - 1K: baseline
  - 2K: 1.5-2x
  - 4K: 2-3x

#### ③ Review Phase

**执行者**：LLM 推理层
**检查项**：
- **文字正确性**：逐字符比对 plan 中的文字 vs 生成的文字
- **空间关系**：物体位置是否符合 plan
- **构图逻辑**：如镜面反射中的元素是否正确翻转
- **技术约束**：宽高比、分辨率是否达标

**关键技术**：Review 不是像素级比较，而是 LLM 对生成图像进行 **语义验证**。模型 "看" 生成的图像，判断其是否满足 plan 的语义要求。

#### ④ Correction Phase

**触发条件**：Review 发现不匹配
**反馈类型**（示例）：
- "文字写的是 'Logn' 不是 'Login'" → 文字重绘
- "人物 A 应该在左边但出现在右边" → 空间重排
- "光源方向与投影不一致" → 光照修正
- "解剖标签指向了错误的结构" → 标注修正

**机制**：定向修复反馈 → 修改 latent intent vector → 回到 ② 重新生成
**注意**：这不是简单的 "重新随机生成"，而是带有 **定向反馈** 的修正循环。

#### ⑤ Output Phase

- 最终图像 + SynthID 水印
- 可选返回 thinking 过程（中间推理文本）
- 中间试探图不计费

### 3.4 Thinking vs Non-Thinking 对比

| 维度 | thinking_level=minimal | thinking_level=High |
|------|----------------------|-------------------|
| 速度 | ~2-4s | ~5-10s |
| 规划深度 | 基础构图 | 完整空间+逻辑+文字规划 |
| Review 轮数 | 0-1 | 1-3 |
| 文字准确率 | ~80% | ~94% |
| 适用场景 | 简单图像、快速原型 | 复杂场景、精确文字、多角色 |

### 3.5 与 NB1/Pro 的架构差异

| 维度 | NB1 | NB Pro | NB2 |
|------|-----|--------|-----|
| 推理-生成连接 | 隐式（端到端训练） | 分离但串行 | **shared latent vector** |
| 自纠正 | 隐式（interim images） | Deep Inference | **显式 Plan→Review→Correct** |
| 纠正反馈 | 无（黑盒） | 模糊（"think through"） | **定向**（"文字是X不是Y"） |
| 用户可观察 | ✗ | 有限 | ✅ include_thoughts=True |
| 循环次数 | 未知 | 未知 | 可控（thinking_level） |

---

## 4. 关键技术洞察

### 4.1 Autoregressive vs Diffusion 的意义

NB1 用 autoregressive 生成图像 token 的意义：
- **优势**：可以像文本一样进行 "推理" — token 级别的依赖关系天然支持逻辑一致性
- **优势**：天然支持 interleaved text+image 生成（同一个 decoder）
- **劣势**：1,290 tokens 的瓶颈限制了空间分辨率（需要 upscaler）
- **劣势**：sequential 生成较慢（无法并行去噪）

NB2 可能用了混合方案：autoregressive 生成高层 plan + diffusion 执行低层像素。

### 4.2 Shared Latent Intent Vector 的技术含义

这个设计意味着：
1. LLM 和 Diffusion Head **不是**简单的 pipeline 串行（prompt → embedding → 生成）
2. 而是通过 **共享隐空间** 双向通信
3. LLM 可以在 Diffusion 过程中 "看到" 中间结果并调整引导
4. 这实现了真正的 "generation-time reasoning"，而非 "pre-generation planning"

### 4.3 Self-Correction 的局限性

NB2 的自纠正能力**有明确的边界**：

**能纠正的**（训练数据中有的知识）：
- 文字拼写错误
- 空间布局不合理
- 光照物理不一致
- 解剖结构错误
- 标签对应错误

**不能纠正的**（训练数据中缺失的知识）：
- ❌ 伊斯兰艺术中的具象禁忌（aniconism）
- ❌ 中国写意画的意笔原则（yibi）
- ❌ 日本浮世绘的特定技法约束
- ❌ 非洲传统艺术的象征体系
- ❌ 特定文化禁忌和敏感题材

**原因**：Review 阶段的 LLM 使用的是与 Generation 相同的训练权重。如果训练数据不包含某项文化知识，self-review 也无法发现违规。这就是为什么 **外部文化路由（VULCA-Agent）不可替代**。

---

## 5. 开放问题

1. **NB2 的 Diffusion Head 具体架构是什么？** — 公开信息中未提及是 U-Net、DiT 还是其他
2. **latent intent vector 的维度和编码方式？** — 无技术论文披露
3. **Review 阶段如何 "看" 生成的图像？** — 是 VLM 式的图像理解，还是通过 latent space 直接检查？
4. **Correct 阶段的具体机制？** — 是修改 noise schedule、调整 attention map，还是完全重新生成？
5. **Google 是否会发布 NB2 的技术论文？** — 截至 2026-02-27 尚未发表
