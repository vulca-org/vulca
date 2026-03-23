# X 推文草稿（最终版）

## 主推文

Same model (Gemini). Same topic (dragon in mountains). One difference: cultural guidance.

Left: raw prompt → "Asian-style painting" → colorful dragon, cherry blossoms, mixed traditions
Right: VULCA pipeline → xieyi tradition constraints → pure ink wash, proper spacing, correct technique

Cultural accuracy scores:

                Raw    VULCA-guided
L3 Cultural:   30% →  97%  (+67 pts)
L5 Philosophy: 40% →  97%  (+57 pts)
L2 Technical:  70% →  92%  (+22 pts)
Overall:       89% →  98%

"Looks Asian" ≠ culturally correct.

pip install vulca — open source, built on EMNLP 2025 research.

[附图: 左右对比 raw_mixed.jpg vs vulca_guided.jpg]
[附图: demo GIF]

---

## Reply 1 — 传统对比（同一张图 4 个文化评价）

Same VULCA-guided painting, 4 different cultural traditions:

Chinese Xieyi (写意): 98% ✓ — correct tradition
Japanese Traditional: 92% ✓ — shared East Asian ink heritage
Western Academic: 10% ✗ — wrong medium entirely
Islamic Geometric: 4% ✗ — zero symmetry or tessellation

Art isn't "good" or "bad." It depends on which cultural lens you use.

---

## Reply 2 — 技术细节

How VULCA works:

1. Scout: resolves "dragon painting" → chinese_xieyi tradition
2. Draft: injects 6 cultural terms (披麻皴, 气韵生动, 留白...) + 2 taboos into prompt
3. Critic: L1-L5 scoring with tradition-specific guidance
4. Decide: accept if score > threshold, else re-generate with critique

13 cultural traditions, each with domain-specific terminology & taboos.
Same engine handles Chinese ink wash, Islamic geometry, and UI/UX design.

github.com/vulca-org/vulca

---

## Reply 3 — 安装

Try it in 10 seconds (no API key needed):

```
pip install vulca
vulca evaluate painting.jpg --mock -t chinese_xieyi
```

Real VLM scoring:
```
export GOOGLE_API_KEY=your-key
vulca evaluate your-art.jpg -t chinese_xieyi
```

Claude Code users:
```
claude plugin marketplace add vulca-org/vulca-plugin
claude plugin install vulca
```

Paper: aclanthology.org/2025.findings-emnlp/

---

## 中文版（知乎/小红书/微博）

同一个 Gemini 模型，同一个主题（山水龙），唯一区别：有没有文化指导。

左图：裸 prompt "Asian style painting" → 彩色龙 + 樱花 + 中日混搭
右图：VULCA 写意约束 → 纯水墨、留白30%+、正确皴法

文化准确性评分：

              裸生成   VULCA引导
文化语境(L3):  30%  →  97%  (+67分)
哲学审美(L5):  40%  →  97%  (+57分)
技法执行(L2):  70%  →  92%  (+22分)
总分:          89%  →  98%

"看起来像中国画" ≠ 文化正确。

VULCA 用 L1-L5 五层文化评分框架，注入写意术语（披麻皴、气韵生动、留白）和禁忌，让任何生成模型在文化维度上变好。

pip install vulca | 开源 | 基于 EMNLP 2025 论文
github.com/vulca-org/vulca

#AI #文化AI #中国画 #水墨 #开源
