# VULCA Layers V2 Demo — decompose, edit, composite
Output "assets/demo/v2/vhs-layers.gif"
Set FontSize 18
Set Width 1000
Set Height 650
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms
Set Padding 20
Set Shell "bash"

Type "# VULCA Layers V2 — Full-canvas RGBA layer editing"
Enter
Sleep 1s

# Analyze
Type `vulca layers analyze artwork.png`
Enter
Sleep 2s
Type "#   [0] background_paper (background)"
Enter
Type "#   [1] distant_mountains (subject)"
Enter
Type "#   [2] mist_and_clouds (effect)"
Enter
Type "#   [3] midground_landscape (subject)"
Enter
Type "#   [4] pavilion_and_pine_trees (subject)"
Enter
Type "#   [5] calligraphy_and_seals (text)"
Enter
Sleep 2s

# Split
Type `vulca layers split artwork.png -o ./layers/ --mode extract`
Enter
Sleep 2s
Type "#   6 layers extracted → full-canvas RGBA PNGs"
Enter
Sleep 1s

# Edit operations
Type "# Layer editing: 7 operations"
Enter
Sleep 500ms
Type `vulca layers add ./layers/ --name "glow" --z-index 6 --content-type effect`
Enter
Sleep 1s
Type `vulca layers toggle ./layers/ --layer mist_and_clouds --visible false`
Enter
Sleep 1s
Type `vulca layers lock ./layers/ --layer background_paper`
Enter
Sleep 1s

# Redraw
Type "# Redraw via img2img"
Enter
Type `vulca layers redraw ./layers/ --layer pavilion_and_pine_trees -i "add autumn colors"`
Enter
Sleep 2s

# Composite
Type `vulca layers composite ./layers/ -o final.png`
Enter
Sleep 1s
Type "#   Composite: final.png (blend modes: normal + screen + multiply)"
Enter
Sleep 2s

# Export
Type `vulca layers export ./layers/ -o ./export.psd`
Enter
Sleep 1s
Type "#   Exported: 6 full-canvas PNGs + manifest.json"
Enter
Sleep 2s
