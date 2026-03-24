---
paths:
  - "vulca/tests/**/*.py"
  - "wenxin-backend/tests/**/*.py"
  - "wenxin-moyun/tests/**/*.spec.ts"
  - "wenxin-moyun/tests/**/*.test.ts"
---

# Testing Rules

编写或修改测试时必须遵守以下规则。

## 核心原则: 测试功能，不测存在

```typescript
// 错误 — 只验证元素存在（假绿）
await expect(page.locator('.submit-btn')).toBeVisible();

// 正确 — 验证功能可用
await page.locator('.submit-btn').click();
await expect(page.locator('.success-message')).toBeVisible();
```

这个教训来自 95 个 E2E 全绿但产品有 5 个致命 bug 的事故。

## 测试命令

| 层级 | 命令 | 说明 |
|------|------|------|
| SDK 单测 | `cd vulca && .venv/bin/python -m pytest tests/ -v` | 276 tests |
| Backend 单测 | `cd wenxin-backend && python3 -m pytest tests/ -v` | 1067 tests |
| Frontend 类型 | `cd wenxin-moyun && npm run type-check` | TypeScript 验证 |
| Frontend lint | `cd wenxin-moyun && npm run lint` | ESLint 验证 |
| E2E | `cd wenxin-moyun && npm run test:e2e` | 95 tests, 需后端 |
| E2E smoke | `cd wenxin-moyun && npm run test:e2e -- --grep="user-journey"` | 10 tests |

## 测试执行顺序

1. **SDK tests** — 最快，核心逻辑
2. **Backend tests** — API 层
3. **Frontend type-check + lint** — 静态检查
4. **E2E** — 最慢，需要后端运行

## E2E 注意事项

- E2E 测试**需要后端运行** (`uvicorn app.main:app --port 8001`)
- CI 跑 Playwright 时没有后端，部分测试会 mock
- 新增 E2E 测试时必须包含功能验证步骤（click → assert result），不仅是 `toBeVisible()`

## 测试账户

```
Demo: demo / demo123
Admin: admin / admin123
```

这些账户由 `init_db.py` 创建。**不要在测试中硬编码其他密码**。

## Mock 模式

SDK/CLI/Backend 全部支持 mock 模式（无需 API key）:
```python
# SDK
result = vulca.evaluate("image.png", mock=True)
result = vulca.create("水墨山水", provider="mock")

# CLI
vulca evaluate image.png --mock
vulca create "水墨山水" --provider mock
```

写新测试时优先使用 mock 模式，避免消耗 API quota。

## 常见陷阱

1. **Vite 缓存导致测试失败**: 运行 `npm run dev:clean` 清除缓存
2. **CORS 错误实际是 500**: 先看后端日志
3. **TypeScript 模块错误**: 在测试文件中本地定义类型作为临时方案
4. **分数 NULL**: 图片模型有意返回 NULL 分数，测试中使用 `!= null` 判断
