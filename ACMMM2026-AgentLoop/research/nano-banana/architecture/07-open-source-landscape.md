# 开源 AR+Diffusion 模型全景 (2026-02-27 调研)

## 1. 可立即运行的统一生成+理解模型

| 模型 | 来源 | GitHub Stars | 参数 | 权重 | 架构 | 许可证 |
|------|------|-------------|------|------|------|--------|
| **Janus-Pro** | DeepSeek | ~17.7k | 1B/7B | ✅ HF | 解耦视觉编码 AR | MIT |
| **Emu3/3.5** | BAAI | ~2k/752 | 8B/34.1B | ✅ HF | 纯 AR next-token | Apache-2.0 |
| **Show-o/o2** | NUS ShowLab | ~1.9k | 1.3B/1.5B/7B | ✅ HF | **AR+Discrete Diffusion** (最接近 NB) | ICLR/NeurIPS 2025 |
| **BAGEL** | ByteDance Seed | ~3k+ | 14B(7B active) MoT | ✅ HF | MoT 统一模型 | 待确认 |
| **OmniGen/2** | VectorSpaceLab | ~4.3k | HF available | ✅ HF | 统一扩散; OmniGen2=AR+Diffusion | MIT |
| **Chameleon** | Meta FAIR | ~2.1k | 7B/30B | ✅ HF | 早期融合 VQ AR | 仅研究 |

## 2. 有自修正机制的模型

| 模型 | 自修正类型 | 来源 |
|------|-----------|------|
| **Infinity** | Bitwise self-correction (模型内部) | FoundationVision, CVPR 2025 Oral |
| **NB2** | Plan→Review→Correct (模型内部, 黑盒) | Google DeepMind |
| **SLD** | LLM-controlled 外部闭环 | UC Berkeley, CVPR 2024 |
| **T2I-Copilot** | 三 Agent 系统 (解析→生成→评估) | SHI-Labs, ICCV 2025 |
| **VULCA-Agent** | 四 Agent 系统 (Scout→Draft→Critic→Queen) | 我们 |

## 3. 不可用模型（仅论文/无权重）

| 模型 | 问题 |
|------|------|
| Transfusion (Meta) | 无官方权重, 仅 lucidrains 代码框架 |
| MARS (ByteDance) | 代码/权重均未正式发布 |

## 4. VLM Critic 候选

| 模型 | 最新版 | 参数范围 | 许可证 | 适合场景 |
|------|--------|---------|--------|---------|
| **InternVL** | 3.5 (2025-08) | 1B-241B(MoE) | Apache-2.0 | 重量级 Critic |
| **Qwen-VL** | Qwen3-VL (2025-09) | 2B-235B(MoE) | Apache-2.0 | 性价比最高 |
| **LLaVA** | OneVision 1.5 | 0.5B-72B | Apache-2.0 | 轻量 Critic |
| **GLM-4.5V** | 智谱 | 106B(12B active) | 开源 | 空间推理强 |

## 5. 开源 Plan→Generate→Review 流水线

| 项目 | 来源 | 架构 | 与 VULCA 差异 |
|------|------|------|--------------|
| **SLD** | CVPR 2024 | LLM→检测→分析→修正 | 无文化维度 |
| **RPG-DiffusionMaster** | ICML 2024 | MLLM 重写→区域扩散 | 无 Review 闭环 |
| **T2I-Copilot** | ICCV 2025 | 解析→生成→质量评估 | 无文化维度, 最完整的三 Agent |
| **Mini-DALLE3** | 社区 | LLM prompt rewriting | 实验性, 不完整 |

## 6. 其他 AR 视觉生成模型

| 模型 | GitHub | 参数 | 特点 |
|------|--------|------|------|
| VAR | FoundationVision/VAR | 310M-2B | NeurIPS 2024 Best Paper, next-scale prediction |
| Infinity | FoundationVision/Infinity | 多尺度 | CVPR 2025 Oral, **内置 bitwise self-correction** |
| LlamaGen | FoundationVision/LlamaGen | 111M-3.1B | 纯 Llama 架构做图像生成 |
| MMaDA | Gen-Verse/MMaDA | 8B | 统一多模态扩散, semi-AR |
| OpenUni | wusize/OpenUni | 1.1B/3.1B | 完全开源基线 |
| D-AR | ShowLab/D-AR | Llama backbone | 扩散重铸为 next-token |
