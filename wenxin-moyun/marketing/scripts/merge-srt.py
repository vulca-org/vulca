#!/usr/bin/env python3
"""Merge word-level SRT files into sentence-level subtitles.

Edge TTS SubMaker produces word-by-word SRT entries. This script
merges them into readable sentence-level subtitles using the
narration source text as a guide.

Usage:
    python3 marketing/scripts/merge-srt.py
"""

import re
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NARRATION_DIR = os.path.join(SCRIPT_DIR, '..', 'narration')
AUDIO_DIR = os.path.join(SCRIPT_DIR, '..', 'exports', 'audio')

VIDEOS = ['v1-home', 'v2-editor', 'v3-creation', 'v4-hitl', 'v5-build', 'v6-gallery', 'v7-admin']


def time_to_ms(t: str) -> int:
    """Convert HH:MM:SS,mmm to milliseconds."""
    h, m, rest = t.split(':')
    s, ms = rest.split(',')
    return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)


def ms_to_time(ms: int) -> str:
    """Convert milliseconds to HH:MM:SS,mmm."""
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'


def parse_srt(path: str) -> list[tuple[int, int, int, str]]:
    """Parse SRT file into list of (index, start_ms, end_ms, text)."""
    entries = []
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read().strip()

    blocks = re.split(r'\n\n+', content)
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        try:
            idx = int(lines[0])
        except ValueError:
            continue
        time_match = re.match(
            r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})',
            lines[1],
        )
        if not time_match:
            continue
        start = time_to_ms(time_match.group(1))
        end = time_to_ms(time_match.group(2))
        text = ' '.join(lines[2:]).strip()
        entries.append((idx, start, end, text))

    return entries


def extract_sentences(narration_path: str) -> list[str]:
    """Extract spoken sentences from narration markdown file."""
    sentences = []
    with open(narration_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip metadata lines
            if not line or line.startswith('#') or line.startswith('**') or line == '---':
                continue
            # Remove timestamp prefix [0:00]
            line = re.sub(r'^\[[\d:]+\]\s*', '', line)
            if not line:
                continue
            # Split into sentences at . ? ! followed by space or end of string
            parts = re.split(r'(?<=[.!?])\s+', line)
            for part in parts:
                part = part.strip()
                if part:
                    sentences.append(part)

    return sentences


def count_spoken_words(text: str) -> int:
    """Count spoken words (exclude standalone punctuation like em dashes)."""
    words = text.split()
    # Filter out standalone punctuation (—, –, -, etc.)
    words = [w for w in words if re.search(r'[a-zA-Z0-9]', w)]
    return len(words)


def merge_srt(video_name: str) -> None:
    """Merge word-level SRT into sentence-level for one video."""
    narration_path = os.path.join(NARRATION_DIR, f'{video_name}-narration.md')
    srt_path = os.path.join(AUDIO_DIR, f'{video_name}-voiceover.srt')

    if not os.path.exists(narration_path):
        print(f'  ⚠ Narration not found: {narration_path}')
        return
    if not os.path.exists(srt_path):
        print(f'  ⚠ SRT not found: {srt_path}')
        return

    sentences = extract_sentences(narration_path)
    entries = parse_srt(srt_path)

    print(f'  Narration sentences: {len(sentences)}')
    print(f'  SRT word entries: {len(entries)}')

    # Count total spoken words in narration
    total_narration_words = sum(count_spoken_words(s) for s in sentences)
    print(f'  Narration words: {total_narration_words}, SRT entries: {len(entries)}')

    if abs(total_narration_words - len(entries)) > 5:
        print(f'  ⚠ Word count mismatch! Narration={total_narration_words} vs SRT={len(entries)}')
        print(f'    Will adjust to fit available SRT entries.')

    merged = []
    srt_idx = 0

    for i, sentence in enumerate(sentences):
        n = count_spoken_words(sentence)

        if srt_idx >= len(entries):
            print(f'  ⚠ Ran out of SRT entries at sentence {i+1}: "{sentence[:50]}..."')
            break

        # Don't overshoot
        remaining_entries = len(entries) - srt_idx
        remaining_sentences = len(sentences) - i
        if n > remaining_entries and remaining_sentences <= 1:
            n = remaining_entries
        elif n > remaining_entries:
            n = max(1, remaining_entries // remaining_sentences)

        if n <= 0:
            break

        start_ms = entries[srt_idx][1]
        end_ms = entries[srt_idx + n - 1][2]

        # Ensure minimum 1 second display time for readability
        if end_ms - start_ms < 1000 and srt_idx + n < len(entries):
            end_ms = max(end_ms, start_ms + 1000)

        merged.append((len(merged) + 1, start_ms, end_ms, sentence))
        srt_idx += n

    # Handle remaining SRT entries
    if srt_idx < len(entries):
        remaining_words = [e[3] for e in entries[srt_idx:]]
        remaining_text = ' '.join(remaining_words)
        if remaining_text.strip():
            start_ms = entries[srt_idx][1]
            end_ms = entries[-1][2]
            merged.append((len(merged) + 1, start_ms, end_ms, remaining_text + '.'))
            print(f'  ⚠ {len(entries) - srt_idx} leftover SRT entries appended as final subtitle')

    # Backup original SRT
    backup_path = srt_path + '.word-level.bak'
    if not os.path.exists(backup_path):
        import shutil
        shutil.copy2(srt_path, backup_path)
        print(f'  Backup: {backup_path}')

    # Write merged SRT
    with open(srt_path, 'w', encoding='utf-8') as f:
        for idx, start, end, text in merged:
            f.write(f'{idx}\n')
            f.write(f'{ms_to_time(start)} --> {ms_to_time(end)}\n')
            f.write(f'{text}\n\n')

    print(f'  ✓ Merged: {len(entries)} word entries → {len(merged)} sentence subtitles')

    # Print preview
    for idx, start, end, text in merged[:3]:
        duration = (end - start) / 1000
        print(f'    [{ms_to_time(start)[:8]}] ({duration:.1f}s) {text[:60]}{"..." if len(text) > 60 else ""}')
    if len(merged) > 3:
        print(f'    ... ({len(merged) - 3} more)')


def main():
    print('=== Merging Word-Level SRT → Sentence-Level ===\n')
    for video in VIDEOS:
        print(f'▸ {video}')
        merge_srt(video)
        print()
    print('✓ All SRT files merged.')
    print('\nTo re-compose videos with new subtitles:')
    print('  bash marketing/scripts/compose-all.sh')


if __name__ == '__main__':
    main()
