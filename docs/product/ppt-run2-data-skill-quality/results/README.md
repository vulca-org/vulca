# Results

Status: not-run-public-blocked.

Generated decks, contact sheets, previews, and layout JSON remain local under `outputs/` unless the user explicitly approves release packaging.

Results are empty until the four generation arms run, render inspection is recorded, and human approval gates are evaluated. This package must not claim that Run 2.0 won or is public-ready before those gates pass.

Each arm must include a persisted `trace_manifest.json` under `outputs/` before comparison. The manifest is the audit trail for runtime isolation, memory selection, density counts, deletion/routing decisions, native PPT object counts, raster-image limits, layout geometry checks, asset provenance, QA outcomes, and release-gate status.
