---
paths:
  - "**/*"
---

# Proactive Trigger Rules

此规则始终加载。指导 Claude 在对话中主动识别用户意图并触发对应能力。

## 核心原则

用户偏好自然语言交互，不想记命令。当用户的话匹配以下模式时，**自动执行对应行动**，不要问"要不要我运行 /xxx"。

## 意图 → 行动映射

### 工程类
| 用户说 | 自动做 |
|--------|--------|
| "提交前检查一下" / "准备提交了" / "查一下有没有问题" | 执行 /vulca-check 逻辑 |
| "跑一下测试" / "测试还过不过" | 执行 /vulca-test 逻辑 |
| "部署一下" / "上线" / "发布" | 执行 /vulca-deploy 逻辑 |
| "进化系统怎么样了" / "权重变了吗" | 执行 /vulca-evolve 逻辑 |

### 产品+增长类
| 用户说 | 自动做 |
|--------|--------|
| "现在什么情况" / "项目状态" / "今天做什么" | 执行 /vulca-brief 逻辑 |
| "Midjourney/DALL-E/Leonardo 最近..." / 任何竞品名 | spawn product-analyst 做竞品分析 |
| "下一步做什么" / "功能优先级" / "做什么最有价值" | spawn product-analyst 做优先级分析 |
| "怎么推广" / "怎么获取用户" / "增长" / "stars" | spawn growth-strategist 做增长分析 |
| "定位" / "我们和 X 的区别" / "优势是什么" | spawn growth-strategist 做定位验证 |

### 内容类
| 用户说 | 自动做 |
|--------|--------|
| "写一篇..." / "发推文" / "写博客" / "写文案" | spawn content-creator 生成内容 |
| "release notes" / "changelog" | spawn content-creator 写版本说明 |
| "这个功能怎么宣传" / "可以发到哪里" | spawn content-creator + growth-strategist |
| "准备 demo" / "演示脚本" | spawn content-creator 写 demo 脚本 |

### Phase 管理类
| 用户说 | 自动做 |
|--------|--------|
| "开始新阶段" / "开始 Phase X" | 执行 /vulca-phase start |
| "这个阶段完了" / "收尾" | 执行 /vulca-phase close |

## Stop 后行为

每次回复结束后（Stop hook 触发），主动提供一句简短建议：

1. **如果刚完成代码变更**: "这个变更可以转为 [博客/推文/demo]，要我帮你写吗？"
2. **如果刚完成分析**: "建议下一步 [具体行动]"
3. **如果刚完成测试**: "测试 [通过/有失败]，建议 [具体行动]"
4. **如果在讨论产品方向**: "总结：[一句话结论]。要我存到 memory 吗？"

## 多 Agent 协作模式

当任务需要多个视角时，自动编排：

### 模式 A：分析 → 审查
```
product-analyst 分析 → growth-strategist 审查补充 → 汇总给用户
```

### 模式 B：并行分析
```
product-analyst + growth-strategist 并行 → 汇总对比 → 给用户
```

### 模式 C：分析 → 内容
```
product-analyst 提取亮点 → content-creator 转化为内容 → 给用户审阅
```

## 报告持久化

所有 agent 产出的分析报告：
- **关键结论**（1-3 句）→ memory/ 中更新相关记录
- **完整报告** → `docs/reports/{type}-{date}-{topic}.md`
- **行动项** → 在回复中高亮告知用户
