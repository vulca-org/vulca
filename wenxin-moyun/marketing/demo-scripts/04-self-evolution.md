# Demo Script #4: Self-Evolution — Frozen Model, Evolving Context (45s)

> **Duration**: 45 seconds
> **Mode**: Terminal + Browser split-screen
> **Audience**: AI researchers, ML engineers, technical audience
> **Key Message**: The evaluator learns from every session — not by retraining the model, but by evolving the context (MemRL pattern)

---

## Pre-Recording Checklist

- [ ] Open terminal (dark theme, large font ~16pt, e.g., JetBrains Mono)
- [ ] Open https://vulcaart.art in Chrome alongside terminal (50/50 split)
- [ ] Backend API accessible (production or local `localhost:8001`)
- [ ] Install `jq` for JSON pretty-printing
- [ ] Pre-test all curl commands to ensure they return data
- [ ] Screen recorder: 1080p, 30fps minimum
- [ ] Terminal prompt set to something clean (e.g., `vulca $`)

---

## Shot-by-Shot Script

### [0:00–0:05] Opening — Split Screen Setup

**Screen**: Split layout — left: terminal (dark), right: browser (Canvas Run mode)

**Action**:
- Terminal shows clean prompt
- Browser shows Canvas in Run mode with a previous session's results visible (radar chart + candidates)

**Annotation**:
- Left side: `Terminal — API Access`
- Right side: `VULCA Canvas — Run Mode`

**Voice-over cue**: "Your evaluator never stops learning. Let me show you what that means."

---

### [0:05–0:10] Check Current Digestion Status

**Screen**: Terminal

**Action**: Type and execute:
```bash
curl -s https://vulca-api.onrender.com/api/v1/digestion/status | jq '.traditions'
```

**Output** (formatted by jq):
```json
{
  "chinese_xieyi": {
    "session_count": 47,
    "cultural_context": 0.25,
    "technique": 0.20,
    "creativity": 0.20,
    "emotion": 0.15,
    "innovation": 0.20
  },
  "japanese_ukiyo_e": {
    "session_count": 31,
    "cultural_context": 0.22,
    ...
  }
}
```

**Annotation**: Highlight `"cultural_context": 0.25` with a box: `Current weight — about to change`

**Voice-over cue**: "Current state: cultural context weighted at 0.25 for Chinese Xieyi."

---

### [0:10–0:12] Pause on Initial Weights

**Screen**: Terminal showing the JSON output

**Action**: Hold shot. Cursor blinks.

**Annotation**: Arrow pointing to weights: `These weights evolved from user sessions, not manual tuning`

**Voice-over cue**: "These weights weren't set by hand. They evolved from 47 real sessions."

---

### [0:12–0:18] Trigger Digestion Cycle

**Screen**: Terminal

**Action**: Type and execute:
```bash
curl -s -X POST https://vulca-api.onrender.com/api/v1/digestion/run | jq
```

**Output** (animated line by line as jq renders):
```json
{
  "status": "completed",
  "cycle_id": "dig-2026-03-09-001",
  "actions": [
    {
      "type": "weight_shift",
      "tradition": "chinese_xieyi",
      "dimension": "cultural_context",
      "old_value": 0.25,
      "new_value": 0.28,
      "reason": "systematically_low scores detected"
    },
    {
      "type": "pattern_detected",
      "pattern": "technique_ceiling",
      "affected_traditions": ["japanese_ukiyo_e"],
      "recommendation": "increase technique threshold"
    }
  ],
  "clusters_found": 2,
  "concepts_crystallized": 1
}
```

**Annotation**:
- Box around `"weight_shift"`: `Automatic weight adjustment`
- Box around `"pattern_detected"`: `Cross-tradition pattern discovery`
- Box around `"concepts_crystallized": 1`: `New cultural concept emerged!`

**Voice-over cue**: "One API call. The digestion system analyzes all sessions, detects patterns, shifts weights, and discovers new cultural concepts."

---

### [0:18–0:24] Examine the Evolution Actions

**Screen**: Terminal (same output, scrolling to highlight key parts)

**Action**:
- (0:18–0:20) Cursor highlights `"old_value": 0.25` → `"new_value": 0.28`
- (0:20–0:22) Cursor highlights `"reason": "systematically_low scores detected"`
- (0:22–0:24) Cursor highlights `"concepts_crystallized": 1`

**Annotation**:
- `0.25 → 0.28: The system learned that cultural context was underweighted`
- `Not retraining. Evolving context.`

**Voice-over cue**: "Cultural context weight shifted from 0.25 to 0.28. The system detected it was systematically underweighting culture. No retraining — just smarter context."

---

### [0:24–0:30] Get Evolution Report

**Screen**: Terminal

**Action**: Type and execute:
```bash
curl -s https://vulca-api.onrender.com/api/v1/digestion/report | jq '.patterns'
```

**Output**:
```json
[
  {
    "pattern": "systematically_low",
    "dimension": "cultural_context",
    "traditions": ["chinese_xieyi", "indian_miniature"],
    "avg_gap": -0.12,
    "action_taken": "weight_increase"
  },
  {
    "pattern": "technique_ceiling",
    "dimension": "technique",
    "traditions": ["japanese_ukiyo_e"],
    "avg_gap": 0.05,
    "action_taken": "threshold_adjustment"
  }
]
```

**Annotation**: `Patterns detected across traditions — the system sees what humans might miss`

**Voice-over cue**: "The evolution report shows cross-tradition patterns. Chinese Xieyi and Indian miniature both had systematically low cultural context scores. The system caught it."

---

### [0:30–0:35] Browser — Emerged Concepts

**Screen**: Browser (right side) — RunConfigForm

**Action**:
1. (0:30–0:32) Click on the run configuration area
2. (0:32–0:34) Scroll to or click "Emerged Concepts" section/tag
3. (0:34–0:35) A new concept card appears: e.g., `"silk_road_fusion"` — a concept that emerged from clustering sessions that blend Chinese and Central Asian motifs

**Annotation**:
- Arrow to emerged concept: `This concept didn't exist yesterday`
- Subtitle: `Emerged from user session clustering`

**Voice-over cue**: "Back in the UI — a new cultural concept has emerged. 'Silk Road Fusion' — discovered by clustering similar sessions. This concept didn't exist yesterday."

---

### [0:35–0:40] Inject into Cultural Intent

**Screen**: Browser — RunConfigForm

**Action**:
1. (0:35–0:37) Click on the emerged concept tag to select it
2. (0:37–0:39) The concept gets injected into the Cultural Intent field
3. (0:39–0:40) The IntentBar updates to reflect the new cultural context

**Annotation**: `Select emerged concept → Inject into next evaluation`

**Voice-over cue**: "Click to inject it into your next evaluation. The system's discoveries become your creative tools."

---

### [0:40–0:45] Closing

**Screen**: Split view — terminal output + browser with injected concept

**Action**: Hold on both screens

**Annotation** (center, large text):
- Line 1: `Frozen Model. Evolving Context.`
- Line 2: `Your evaluator learns from every session.`
- Bottom: `vulcaart.art` + `Open Source`

**Voice-over cue**: "Frozen model. Evolving context. Your evaluator never stops learning — and it never needs retraining."

---

## Post-Production Notes

- **Terminal styling**: Use a dark theme with syntax-highlighted JSON (green keys, white values, yellow strings)
- **Split screen**: 50/50, terminal slightly wider if needed for JSON readability
- **Typing effect**: Consider recording terminal at natural speed, then 1.5x for long commands
- **Key moment**: The weight shift reveal at [0:18–0:24] is the conceptual climax — hold and emphasize
- **Export**: MP4 1080p, consider keeping horizontal only (terminal doesn't work well in 9:16)

---

## Companion Social Post — Teaser

### English (Twitter/X)

**Title**: Your evaluator never stops learning. Frozen model. Evolving context.

**Tweet** (278 chars):

```
Your evaluator never stops learning.

Not by retraining. By evolving context.

→ Digestion system analyzes all sessions
→ Detects cross-cultural patterns
→ Shifts evaluation weights automatically
→ Crystallizes new cultural concepts

Frozen model. Evolving context.

vulcaart.art
```

**Image**: `exports/video-v5-research.png`

---

### 中文 (Twitter/X)

**标题**: 你的评估器永不停止学习。冻结模型，进化上下文。

**推文** (275 字符):

```
你的评估器永不停止学习。

不是重新训练，而是进化上下文。

→ 消化系统分析所有会话
→ 检测跨文化模式
→ 自动调整评估权重
→ 结晶新的文化概念

冻结模型，进化上下文。这就是 MemRL 模式。

vulcaart.art

#CulturalAI #VULCA #自进化AI
```

**配图**: `exports/video-v5-research.png`
