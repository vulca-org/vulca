# VULCA Studio Demo — Brief-driven creative session
Output "assets/demo/v2/vhs-studio.gif"
Set FontSize 18
Set Width 1000
Set Height 650
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms
Set Padding 20
Set Shell "bash"

Type "# VULCA Studio — Brief-driven creative collaboration"
Enter
Sleep 1s

Type `vulca studio "Cyberpunk ink wash, neon pavilions in misty mountains" --provider gemini --auto`
Enter
Sleep 2s

Type "#"
Enter
Type "# VULCA Studio — session 0c2a9198"
Enter
Type "#   Suggested styles: chinese_xieyi"
Enter
Type "#   Style detected: chinese_xieyi (50%), cyberpunk (50%)"
Enter
Sleep 1s

Type "#"
Enter
Type "#   [Concept] 4 concepts generated (831-921KB each)"
Enter
Type "#     1. c1.jpg (904KB)"
Enter
Type "#     2. c2.jpg (921KB)"
Enter
Type "#     3. c3.jpg (831KB)"
Enter
Type "#     4. c4.jpg (860KB)"
Enter
Sleep 2s

Type "#"
Enter
Type "#   [Generate] Creating artwork via gemini..."
Enter
Sleep 1s

Type "#   [Evaluate] L1-L5 (based on your Brief):"
Enter
Type "#     L1 ███████████████████░ 95%"
Enter
Type "#     L2 ██████████████████░░ 90%"
Enter
Type "#     L3 █████████████████░░░ 85%"
Enter
Type "#     L4 ████████████████████ 100%"
Enter
Type "#     L5 ███████████████████░ 95%"
Enter
Sleep 2s

Type "#   Score target reached (93%). → Accepted!"
Enter
Sleep 2s

Type "# Step-by-step alternative:"
Enter
Type `vulca brief ./project -i "Cyberpunk shanshui" -m "epic-futuristic"`
Enter
Sleep 500ms
Type `vulca brief-update ./project "Add more negative space"`
Enter
Sleep 500ms
Type `vulca concept ./project -n 4 --provider gemini`
Enter
Sleep 500ms
Type `vulca concept ./project --select 1`
Enter
Sleep 2s
