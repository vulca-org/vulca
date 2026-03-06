# Nano Banana 技术研究索引

> 整理日期：2026-02-27
> 用途：ACM MM 2026 论文 + VULCA-Agent 框架拓展

## 文件结构

```
nano-banana/
├── docs/
│   ├── 00-index.md              ← 本文件（总索引）
│   ├── 01-model-family.md       ← NB1/Pro/NB2 模型族谱
│   ├── 02-architecture.md       ← 核心架构深度解析
│   ├── 03-api-reference.md      ← API 参数 + 代码示例
│   └── 04-pricing.md            ← 定价 + 成本估算
├── architecture/
│   ├── 05-vulca-nb-comparison.md ← VULCA-Agent vs NB 对比分析
│   ├── 07-open-source-landscape.md ← 开源替代全景 (2026-02-27)
│   └── 08-nb2-reverse-engineering.md ← NB2 逆向工程 (2026-02-27)
├── comparison/
│   └── 06-generation-vs-evaluation.md ← Generation-side vs Evaluation-side
├── strategy/
│   └── 09-open-the-black-box.md ← ★ 核心：开源产品战略分析
├── code-examples/
│   └── nb2_provider_draft.py    ← NB2 Provider 草稿代码
└── api-reference/
    └── gemini-image-api.md      ← Gemini Image API 完整参考
```

## 关键结论（速查）

1. **NB2 = Gemini 3.1 Flash Image**，内部代号 GEMPIX 2
2. **混合架构**：LLM 推理（Gemini 3 Pro 脑）+ Diffusion（GemPix 2 手），通过 shared latent intent vector 连接
3. **5 阶段管线**：Plan → Generate → Review → Correct → Output（内部自纠正）
4. **NB1 是 autoregressive**：每张图生成 1,290 tokens，非纯 diffusion
5. **与 VULCA-Agent 正交互补**：NB 修的是 L1-L2（文字/构图），我们修的是 L3-L5（文化/哲学）
6. **API 价格**：NB2 1K=$0.067, 批量=$0.034（比 FLUX Together.ai ~$0.003 贵但质量高很多）

## 参考来源

- [Gemini API Image Generation 官方文档](https://ai.google.dev/gemini-api/docs/image-generation)
- [Gemini API Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Gemini 3 Developer Guide](https://ai.google.dev/gemini-api/docs/gemini-3)
- [fal.ai: NB2 API Developer Guide](https://fal.ai/learn/devs/nano-banana-2-api-developer-guide)
- [WaveSpeed: NB2 vs Pro](https://wavespeed.ai/blog/posts/nano-banana-2-vs-nano-banana-pro-whats-the-difference/)
- [Apiyi: NB2 Hands-on](https://help.apiyi.com/en/nano-banana-2-released-gemini-3-1-flash-image-en.html)
- [NB2 Complete Guide](https://nano-banana.io/posts/what-is-nano-banana-2)
- [Google Blog: NB2 Launch](https://blog.google/innovation-and-ai/technology/ai/nano-banana-2/)
- [Google Blog: Build with NB2](https://blog.google/innovation-and-ai/technology/developers-tools/build-with-nano-banana-2/)
- [Codecademy: NB1 Guide](https://www.codecademy.com/article/gemini-2-5-flash-image-nano-banana)
- [SellerPic: GemPix 2 Architecture](https://www.sellerpic.ai/blog/nano-banana-2)
- [Higgsfield: NB2 vs NB1](https://higgsfield.ai/blog/Nano-Banana-2-vs-Nano-Banana-1)
