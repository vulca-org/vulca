# VULCA v0.4.0 CLI Demo — VHS tape file
# Install VHS: go install github.com/charmbracelet/vhs@latest
# Run: vhs scripts/record-cli-demo.tape

Output vulca/assets/demo.gif
Set Shell bash
Set FontSize 16
Set Width 1000
Set Height 600
Set Padding 20
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms

Type "# VULCA v0.4.0 — Cultural Art Advisor"
Enter
Sleep 1s

Type "vulca --version"
Enter
Sleep 1.5s

Type "# Evaluate artwork (strict mode — judge)"
Enter
Type "vulca evaluate painting.jpg --mock -t chinese_xieyi"
Enter
Sleep 4s

Type "# Reference mode — advisor, not judge"
Enter
Type "vulca evaluate painting.jpg --mock -t chinese_xieyi --mode reference"
Enter
Sleep 4s

Type "# Fusion mode — compare across traditions"
Enter
Type "vulca evaluate painting.jpg --mock -t chinese_xieyi,watercolor,western_academic --mode fusion"
Enter
Sleep 4s

Type "# Create your own tradition"
Enter
Type "vulca tradition --init cyberpunk_ink | head -15"
Enter
Sleep 3s

Type "# Create artwork (reference mode — no forced cultural correction)"
Enter
Type 'vulca create "水墨山水" --provider mock --mode reference -t chinese_xieyi'
Enter
Sleep 3s

Type "# pip install vulca  |  github.com/vulca-org/vulca"
Enter
Sleep 3s
