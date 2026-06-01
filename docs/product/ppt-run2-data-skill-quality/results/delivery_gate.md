# Delivery Gate

Status: not-run-public-blocked.

Public publishing is blocked until generated outputs exist, native render or cross-platform render inspection passes, asset provenance is complete, and human approval is recorded.

## Gate Checklist

| Gate | Status |
| --- | --- |
| Four generated arms exist under `outputs/` | blocked |
| Per-arm `trace_manifest.json` files exist and pass review | blocked |
| Native render inspection completed | blocked |
| Cross-platform render inspection completed if needed | blocked |
| Asset provenance complete | blocked |
| Editable text and native structure inspection completed | blocked |
| Human approval recorded | blocked |

Delivery status remains internal-only until every gate is unblocked.

## Release Decision Thresholds

- `internal only`: any generated arm, trace manifest, render check, provenance note, editability check, or human approval is missing.
- `demo candidate`: all four arms exist, trace manifests pass review, render inspection is complete, and the Run 2.0 arm scores at least 4 on `editability`, `asset_discipline`, and `render_risk`.
- `public blocked`: the default external status until human approval explicitly records that the generated deck, trace manifest, provenance, and render inspection are acceptable.
