---
name: vulca
description: Cultural art evaluation and guided creation — L1-L5 scoring across 15+ traditions with actionable improvement suggestions
metadata:
  openclaw:
    requires:
      bins: ["vulca"]
---

# VULCA — Cultural Art Advisor

Evaluate AI-generated artwork for cultural accuracy and get actionable improvement suggestions using L1-L5 dimension scoring across 15+ art traditions.

## When to Use

- User wants to evaluate an image for cultural accuracy
- User asks about art quality, cultural fidelity, or tradition alignment
- User wants to create culturally-guided artwork
- User mentions traditions like "Chinese ink wash", "Islamic geometric", "Japanese ukiyo-e"

## Evaluate an Image

Use the `exec` tool to run:

```bash
vulca evaluate <image_path> --tradition <tradition_name> --mode reference
```

Available traditions: chinese_xieyi, chinese_gongbi, japanese_traditional, islamic_geometric, western_academic, watercolor, african_traditional, south_asian, contemporary_art, photography, brand_design, ui_ux_design

Example:
```bash
vulca evaluate painting.jpg --tradition chinese_xieyi --mode reference
```

## Create Artwork with Cultural Guidance

```bash
vulca create "水墨山水" --tradition chinese_xieyi --provider mock
```

## Studio Mode (Interactive Creative Session)

For a full creative collaboration session:
```bash
vulca brief ./project --intent "赛博朋克水墨山水" --mood serene
vulca concept ./project --count 4 --mock
vulca concept ./project --select 1
```

## List Available Traditions

```bash
vulca traditions
```

## Get Tradition Guide

```bash
vulca tradition chinese_xieyi
```
