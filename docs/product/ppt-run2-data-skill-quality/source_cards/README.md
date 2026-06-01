# Source Cards

Each JSON file is one original analysis card derived from a public reference. Store observations and derived design rules only. Do not store copied layouts, screenshots, logos, full article text, full transcripts, or proprietary assets.

Run 2.2 adds `../multimodal_database.json` upstream of these cards. Source cards should remain compact source-specific translations; the multimodal database records cross-modal anchors across text, image references, video, audio, transcript, and interaction observations.

Required fields: `schema_version`, `card_id`, `source_id`, `source_type`, `allowed_use`, `do_not_copy`, `observed_move`, `why_it_works`, `ppt_translation`, `quality_risk`.
