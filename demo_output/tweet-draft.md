# X 推文草稿

## 主推文（版本 B：传统对比）

Same AI painting. 4 cultural traditions. Wildly different scores.

Chinese Xieyi (写意): 95% ✓ — correct brushwork, spacing, ink harmony
Japanese Traditional: 92% ✓ — shared East Asian ink tradition
Western Academic: 10% ✗ — wrong medium, no oil technique, no chiaroscuro
Islamic Geometric: 4% ✗ — zero symmetry, no tessellation, no arabesque

Art isn't "good" or "bad." It depends on which cultural lens you use.

pip install vulca — L1-L5 cultural evaluation for AI art.

Built on EMNLP 2025 research. Open source.
github.com/vulca-org/vulca

[附图: gemini_xieyi.jpg + GIF]

---

## Reply 1（技术细节）

How it works:

1. 13 cultural traditions with domain-specific terminology & taboos
2. L1-L5 scoring: Visual → Technical → Cultural → Critical → Philosophical
3. Each tradition weights dimensions differently:
   - Xieyi → L5 (philosophy) at 30%
   - Islamic Geometric → L2 (technical) at 30%
   - Brand Design → L2 (system adherence) at 30%

Works as CLI, Python SDK, or Claude Code MCP plugin.

Paper: aclanthology.org/2025.findings-emnlp/

## Reply 2（安装 + 快速体验）

Try it in 10 seconds:

```
pip install vulca
vulca evaluate painting.jpg --mock -t chinese_xieyi
```

Real scoring (needs Google API key, free tier works):

```
export GOOGLE_API_KEY=your-key
vulca evaluate your-artwork.jpg -t chinese_xieyi
```

Claude Code users:
```
claude plugin marketplace add vulca-org/vulca-plugin
claude plugin install vulca
```

## 中文版（知乎/小红书）

同一张 AI 水墨画，4 个文化传统评价，分数天差地别：

写意画标准：95% ✓ — 笔法、留白、墨色层次都对
日本传统画：92% ✓ — 东亚书画共通性高
西方学院派：10% ✗ — 不是油画，没有明暗法
伊斯兰几何：4% ✗ — 零对称，零镶嵌

艺术没有绝对的"好"或"坏"，取决于你用哪个文化视角来看。

这就是为什么 AI 生成的"中国画"经常不对——它不理解文化维度。

我做了一个开源工具 VULCA，用 L1-L5 五层文化评分框架评价任何 AI 生成的艺术作品。

pip install vulca
基于我们的 EMNLP 2025 论文。

#AI #文化AI #中国画 #开源
