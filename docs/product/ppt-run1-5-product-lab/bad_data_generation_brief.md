# Bad Data Generation Brief

Generate the bad-data arm as a negative control.

Use corrupted rules that remain structurally valid. The corrupted rules should still parse and should still produce a deck attempt, but they should degrade hierarchy, product-surface feel, primitive selection, or QA traceability enough for review to catch the failure.

The bad-data arm must not use malformed JSON, missing required files, or intentionally broken PPTX packaging. It must not rely on invalid_json, malformed_pptx, or missing_required_files as the failure mode.
