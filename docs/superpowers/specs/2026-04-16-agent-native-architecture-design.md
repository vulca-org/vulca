# Agent-Native Architecture Design (Option C — Strict Variant)

**Date:** 2026-04-16  
**Status:** Approved  
**Goal:** Transform Vulca's MCP tool surface from 29 overlapping tools to ~20 atomic, non-overlapping tools. Agent drives all creative decisions; Vulca provides hands + eyes.

## Principle

Every MCP tool must be either:
- **A primitive** — does one thing, returns structured data, no hidden loops or decisions
- **A thin convenience wrapper** — calls 1-2 primitives, documented as such, zero hidden logic

If a tool contains a loop, a threshold check, or a VLM call that makes a creative decision, it violates the agent-native contract.

## Tool Surface (20 tools)

### Generate (3)
| Tool | Description | Changes |
|------|-------------|---------|
| `generate_image` | **NEW.** Single image from prompt. No loop, no evaluate. | Add |
| `create_artwork` | Thin wrapper: generate + evaluate in one call. No DecideNode, no rerun loop. Returns image + scores. Agent decides retry. | Refactor |
| `inpaint_artwork` | Single inpaint result. | Already done (Task 5) |

### Observe (2)
| Tool | Description | Changes |
|------|-------------|---------|
| `view_image` | **NEW.** Returns base64 thumbnail for agent inspection. | Add |
| `evaluate_artwork` | L1-L5 cultural scoring. Always full JSON. | Already done (Task 4) |

### Traditions (3)
| Tool | Description | Changes |
|------|-------------|---------|
| `list_traditions` | List all traditions with weights. | Keep |
| `get_tradition_guide` | Full tradition data + tradition_layers (from Task 10). | Enhance |
| `search_traditions` | **NEW.** Cross-tradition tag search over terminology, taboos, aliases. | Add |

### Layers (8)
| Tool | Description | Changes |
|------|-------------|---------|
| `layers_split` | Decompose image into RGBA layers. | Keep |
| `layers_list` | **NEW.** Structured layer inventory from manifest. | Add |
| `layers_edit` | Add/remove/reorder/toggle/lock/merge/duplicate layers. | Keep |
| `layers_redraw` | Img2img redraw of specific layers. | Keep |
| `layers_transform` | Spatial transforms (move, scale, rotate, opacity). | Keep |
| `layers_composite` | Reassemble layers into flat image. | Keep |
| `layers_export` | Export as PNG dir or PSD. | Keep |
| `layers_evaluate` | Per-layer L1-L5 scoring. | Keep |

### Workflow (3)
| Tool | Description | Changes |
|------|-------------|---------|
| `brief_parse` | Parse intent + mood into structured brief JSON. Stateless. | Replace studio_create_brief + studio_update_brief |
| `generate_concepts` | Generate N concept images from prompt. Stateless. | Replace studio_generate_concepts |
| `archive_session` | Archive brief + selected image + feedback. Triggers digestion. | Replace studio_accept |

### Infrastructure (1)
| Tool | Description | Changes |
|------|-------------|---------|
| `sync_data` | Cloud sync. | Keep |

## Deletions (11 tools removed)

| Tool | Reason |
|------|--------|
| `vulca_layered_create` | Agent plans layers itself via get_tradition_guide + generate_image per layer |
| `vulca_layers_retry` | Agent retries individual layers via layers_redraw |
| `resume_artwork` | Agent drives loop, no HITL pause/resume needed |
| `analyze_layers` | Overlaps layers_split; agent uses view_image + layers_list |
| `layers_regenerate` | = generate_image + layers_composite |
| `get_evolution_status` | Internal metric, not agent-facing |
| `studio_create_brief` | Replaced by brief_parse |
| `studio_update_brief` | Replaced by brief_parse (agent passes updated intent) |
| `studio_generate_concepts` | Replaced by generate_concepts |
| `studio_select_concept` | Deleted — agent picks from generate_concepts results |
| `studio_accept` | Replaced by archive_session |

## create_artwork Refactor

Before (brain logic):
```
generate → evaluate → decide → [loop if score < threshold] → return
```

After (thin wrapper):
```
generate → evaluate → return {image_path, scores, rationales, cost_usd}
```

Agent receives scores and decides: accept, retry with feedback, or edit layers.

## search_traditions Spec

```python
@mcp.tool()
async def search_traditions(
    tags: list[str],
    limit: int = 5,
) -> dict:
    """Search across all cultural traditions by keyword tags.

    Searches: tradition names, display names, terminology (term + aliases + translations),
    taboo trigger patterns, style keywords.

    Args:
        tags: Keywords to search for (e.g. ["ink wash", "留白", "negative space"]).
        limit: Max results per tradition. Default 5.

    Returns:
        matches: List of {tradition, matched_terms[], relevance_score, summary}.
    """
```

## Studio Decomposition

Old 5-step stateful flow → 3 stateless primitives:

| Old | New | Key change |
|-----|-----|-----------|
| `studio_create_brief(intent, mood, project_dir)` | `brief_parse(intent, mood)` | No filesystem, returns JSON |
| `studio_update_brief(project_dir, instruction)` | Agent calls `brief_parse` again with updated intent | Deleted |
| `studio_generate_concepts(project_dir, count, provider)` | `generate_concepts(prompt, count, provider)` | No project_dir dependency |
| `studio_select_concept(project_dir, index)` | Deleted | Agent picks from list |
| `studio_accept(project_dir)` | `archive_session(brief, image_path, feedback)` | Explicit params, no filesystem lookup |
