---
name: vulca-write
description: VULCA 内容生成 — 博客、社媒文案、demo 脚本、changelog、学术宣传
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - Agent
  - WebSearch
---

# /vulca-write — 内容生成

## 实时上下文
!`cd /home/yhryzy/projects/website && echo "Recent commits (content source):" && git log --oneline -10 2>/dev/null && echo "---Existing content:" && ls -t docs/reports/*.md 2>/dev/null | head -5 || echo "  None"`

将技术成果转化为多渠道内容。

## 用法

```
/vulca-write                          # 根据最近变更自动推荐内容类型
/vulca-write --blog "主题"            # 技术博客
/vulca-write --tweet "主题"           # Twitter/X 推文线程
/vulca-write --reddit "主题"          # Reddit 帖子
/vulca-write --release                # Release Notes
/vulca-write --demo "场景"            # Demo 脚本
/vulca-write --academic "主题"        # 学术宣传
/vulca-write --wechat "主题"          # 微信公众号文章
```

## 自动触发条件

当用户自然语言提到以下话题时自动触发（无需 /vulca-write）：
- "写一篇..."、"发一条推文"、"写个博客"
- "这个功能怎么宣传"、"帮我写文案"
- "准备 release notes"、"写 changelog"
- "这个可以发到哪里"

## 执行步骤

### 1. 素材收集
```bash
git log --oneline -10                # 最近变更
git diff --stat HEAD~3 HEAD          # 近期工作量
```
- 读取当前 Phase 状态
- 读取 memory/ 了解项目叙事

### 2. 内容生成（spawn content-creator agent）

提供：
- 素材（变更列表、功能描述、技术细节）
- 目标渠道和受众
- 品牌调性要求
- 已有内容（避免重复）

### 3. 输出

内容文件写入 `docs/reports/`：
- 博客: `blog-{date}-{slug}.md`
- 社媒: `social-{date}-{platform}.md`
- 学术: `academic-{date}-{topic}.md`
- Demo: `demo-{date}-{topic}.md`
- Release: `release-{version}.md`

### 4. 反馈

输出完成后提示用户：
- 内容摘要（前 3 行）
- 文件位置
- 建议的发布渠道和时间
- "需要调整语气/长度/角度吗？"
