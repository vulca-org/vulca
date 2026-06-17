# Video Cards

Video cards record timestamped observations and pacing analysis only. They do not store full transcripts, screenshots, downloaded media, audio, or video frames.

Run 2.2 records broader audio/video/tutorial anchors in `../multimodal_database.json`. Video cards remain the video-specific layer; audio and transcript anchors must still be paraphrased design observations, never stored media or full transcript text.

Required fields: `schema_version`, `card_id`, `source_id`, `source_type`, `allowed_use`, `do_not_copy`, `timestamp_map`, `keyframe_descriptions`, `pacing_notes`, `transition_observations`, `derived_aesthetic_cards`.
