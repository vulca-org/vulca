---
paths:
  - "wenxin-moyun/src/**/*.tsx"
  - "wenxin-moyun/src/**/*.ts"
  - "wenxin-moyun/src/**/*.css"
---

# Digital Curator v2.1 Design System Rules

编辑前端文件时必须遵守以下设计系统规范。

## 色彩 Token

| Token | 值 | 用途 |
|-------|-----|------|
| Primary Blue | `#005ab4` | 主按钮、链接、活动态 |
| Bronze | `#C87F4A` | Scout agent 标识 |
| Sage Green | `#5F8A50` | Draft agent 标识 |
| Amber Gold | `#B8923D` | Critic agent 标识 |
| Coral Red | `#C65D4D` | Queen agent 标识 / 错误状态 |

### 背景与层叠

- Light 背景: `#f9f9ff` (Cool White)
- Dark 背景: `#0F0D0B` (Warm Black)
- Surface 层叠: `#f9f9ff` (base) → `#f2f3fd` (sections) → `#ffffff` (cards)
- 环境阴影: `rgba(28,28,25,0.06)`

### 禁止使用的颜色

以下硬编码颜色已被替换为设计系统 token，**不得再出现**:
- `#334155` → 使用 `text-on-surface` 或 CSS 变量
- `#FAF7F2` → 使用 `bg-surface-container-low` 或 CSS 变量
- `#1e293b` → 使用设计 token

## 字体规范

- **Noto Serif**: 标题和 ≥24px 文字
- **Inter**: 正文和 UI 元素 (<24px)
- 在 JSX 中设置 `fontFamily` 时，Noto Serif 用于 `h1-h4`、`text-2xl` 及以上

## 圆角与间距

- Cards: `rounded-2xl` (16px)
- Buttons: `rounded-3xl` (24px)
- Hero containers: `rounded-[48px]` (48px)

## No-Line Rule

**绝对禁止 1px 边框**。使用色调变化和负空间替代:
- 不要使用 `border`, `border-t`, `border-b` 等
- 用背景色差异区分区域
- 用 `shadow` 替代分隔线

## 交互规范

- 所有可点击元素最小触控目标: **44px** (`min-h-[44px] min-w-[44px]`)
- 使用 IOS 组件系统: `IOSButton`, `IOSCard`, `IOSToggle`, `IOSSlider`, `IOSAlert`

## NULL 安全

图片模型有意返回 NULL 分数:
```typescript
// 必须 null check
{score != null ? score.toFixed(1) : 'N/A'}

// API 数据必须 guard
if (data) Object.entries(data).map(...)
// 而不是直接 Object.entries(data).map(...)
```

## Canvas 布局

Canvas 是单一界面（无 Tab）:
- 三栏布局: AI Collective (w-80) | Artwork HUD (~70%) + Log (~18%) + Chat (~12%) | L1-L5 + Tags + Finalize
- 空闲态: 中央意图输入框 + 配置面板
- 运行态: 全出血艺术品大图 + Glass HUD + Intelligence Log
- 完成态: Finalize Artifact + Feedback + Confidence/Cost
