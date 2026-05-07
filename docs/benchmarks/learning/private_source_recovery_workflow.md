# Private source recovery workflow

This workflow is for local or private environments that have access to real-user
source artifacts. It must not copy private materials into benchmark case logs,
reviewed source packets, or shared reports.

## Goal

The public repository dataset should keep private source material out of git.
After the public source-context packets are present, the remaining default
training report has two `no_source_context_for_required_source` gaps. Those gaps
are real-user cases that can be closed only by resolving private source refs to
local files at eval time.

## Command

Run the provider-free recovery eval with local search roots:

```bash
PYTHONPATH=src python3 scripts/real_source_context_recovery_eval.py \
  --repo-root . \
  --case-source-manifest docs/benchmarks/learning/combined_case_source_manifest_v1.json \
  --source-dependency-manifest docs/benchmarks/learning/real_source_dependency_label_manifest_v1.json \
  --artifact-search-root PATH_TO_PRIVATE_SOURCE_ARTIFACTS \
  --image-search-root PATH_TO_PRIVATE_SOURCE_IMAGES \
  --output-dir build/private_source_recovery_workflow/real_recovery_eval \
  --report build/private_source_recovery_workflow/real_recovery_eval/report.json \
  --max-recovered-source-context-gaps 0 \
  --min-fallback-agent-reduction 2 \
  --min-recovered-eval-cases 2
```

Use `--artifact-filename-alias PRIVATE_BASENAME=LOCAL_BASENAME` or
`--image-filename-alias PRIVATE_BASENAME=LOCAL_BASENAME` when a local recovered
directory or file uses a safe local basename that differs from the private ref
basename.

## Expected result

With the current reviewed real-user cases and a complete local private source
directory, the recovery eval should report:

- `Source context signals: 31 -> 35`
- `Dry-run fallback_agent_count: 7 -> 5`
- `Dry-run no_source_context_for_required_source: 2 -> 0`
- `Recovered eval cases: 2`
- `Thresholds: passed`

The remaining fallback count is not a source-context data gap. It is the current
agent-required or low-confidence routing boundary after source context is
available.

## Safety rules

- Do not commit generated private asset maps.
- Do not commit recovered source artifacts or source images.
- Do not paste private source refs into shared docs.
- Shared reports should include counts and case ids only, not local paths or raw
  source text.
- Private asset maps are local sidecars used only by recovery/audit/eval runs.
