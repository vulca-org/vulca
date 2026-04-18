# 3 版小红书文案 · 选一个发 (Post #2 · Trump)

## Version A · 短直接（推荐首发）

```
我让 Claude 把 Donald Trump 的 3 张照片都拆了 👀

重点是 Butler 2024 抬拳头那张 —
一张 387×258 的新闻照，Claude 识出 6 个独立主体
Trump + 3 个特工 + 美国国旗 + 蓝天
全自动 · 零人工抠图

#donaldtrump #trump #特朗普 #butler2024 #AI拆图 #AI艺术
#claudecode #AIGC #新闻摄影 #计算机视觉
```

## Version B · 技术感

```
Butler PA 2024 · Claude Code 配合 Vulca SDK 自动拆层

shooting: 6 主体（Trump + 3 特工 + 国旗 + 天空）
mugshot:  8 层（含完整五官解剖）
portrait: 12 层（椭圆办公室 + 国旗）

agent 驱动：Claude 读图 → 写 JSON plan
→ Vulca 跑 YOLO+DINO+SAM+SegFormer
→ 结果回到 Claude 核查 flags

对 Butler 那张的 4 人拥挤场景，agent 自己切到 sam_bbox
用 bbox hint 把重叠的特工分开 — 这才是 agent-native

#trump #donaldtrump #butler2024 #AI艺术 #计算机视觉
#claudecode #AIGC #开源项目
```

## Version C · 悬念式

```
Butler 2024 那张 Trump 抬拳头的照片
除了 Trump 自己，你能数出几个主体？

→ 滑到第 4 张看全答案
→ 再滑到第 6 张看 mugshot 的五官拆解

#trump #donaldtrump #butler2024 #特朗普 #mugshot
#AI拆图 #AI艺术 #AIGC #claudecode
```

---

# 发布 checklist

- [ ] 封面 (01-cover.png) — Butler 抬拳头 + "我让 Claude 把 Trump 拆了"
- [ ] 9 张按顺序上传
- [ ] Version A 首发（最短，突出 Butler 6 主体）
- [ ] 发布时间 19:00-22:00
- [ ] 首 2h 盯评论，前 24h 不改

# 内容叙事 (v2 · Butler-heavy)

1. **01 cover** — Butler 抬拳头 + "我让 Claude 把 Trump 拆了"
2. **02 Butler 2024 原图** — 全图展示（让用户看到源头）
3. **03 shooting · Trump** — 单独拆出抬拳头的 Trump
4. **04 shooting 多主体** — Trump hero + 3 特工 + 国旗并排
5. **05 mugshot · 人物** — 2023 Georgia mugshot 拆出人
6. **06 mugshot · 五官解剖** — 6 宫格：皮肤 / 头发 / 眼 / 鼻 / 嘴 / 耳
7. **07 portrait · 人物** — 椭圆办公室照压轴，说明流程对任何照都管用
8. **08 怎么做到的** — Claude Code + Vulca 四步流程
9. **09 数据总结** — 47 张 · 485 层 · 零人工

# 封面点击率关键

- Butler 抬拳头是近 50 年最有记忆点的新闻摄影之一
- "我让 Claude 把 Trump 拆了" 双钩子（AI 圈 + 政治圈）
- KPI: 收藏 ≥ 点赞 = 找对受众
