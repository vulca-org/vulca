# VULCA Tools Demo — 5 algorithmic analysis tools, zero API cost
Output "assets/demo/v2/vhs-tools.gif"
Set FontSize 18
Set Width 1000
Set Height 600
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms
Set Padding 20
Set Shell "bash"

Type "# VULCA Tools — 5 analysis tools, zero API cost"
Enter
Sleep 1s

Type `vulca tools run brushstroke_analyze --image artwork.png -t chinese_xieyi`
Enter
Sleep 1s
Type "#   Brushstroke energy (0.87) aligns with chinese_xieyi's expressive style."
Enter
Type "#   Visible, dynamic strokes consistent with tradition. Confidence: 0.90"
Enter
Sleep 2s

Type `vulca tools run whitespace_analyze --image artwork.png -t chinese_xieyi`
Enter
Sleep 1s
Type "#   Whitespace (32.8%) is within the chinese_xieyi ideal range (30%-55%)."
Enter
Type "#   Distribution: top_heavy — aligns with tradition. Confidence: 0.75"
Enter
Sleep 2s

Type `vulca tools run composition_analyze --image artwork.png -t chinese_xieyi`
Enter
Sleep 1s
Type "#   Rule-of-thirds alignment (0.75), left_heavy asymmetry"
Enter
Type "#   Aligns with chinese_xieyi's preference for asymmetric, dynamic arrangements."
Enter
Sleep 2s

Type `vulca tools run color_gamut_check --image artwork.png -t chinese_xieyi`
Enter
Sleep 1s
Type "#   Compliance: 98.2% — within tradition color gamut."
Enter
Sleep 2s

Type `vulca tools run color_correct --image artwork.png -t chinese_xieyi --mode suggest`
Enter
Sleep 1s
Type "#   Suggestion: reduce saturation by 5% for more traditional ink wash feel."
Enter
Sleep 2s

Type "# All 5 tools: OpenCV + NumPy only. No API key needed."
Enter
Sleep 2s
