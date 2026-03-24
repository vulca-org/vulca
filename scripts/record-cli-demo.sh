#!/usr/bin/env bash
# VULCA CLI Demo Recording Script v0.4.0
#
# This script runs through VULCA's key features with visible output.
# Record it with any terminal recorder:
#
#   # Option 1: asciinema (recommended)
#   pip install asciinema && asciinema rec demo.cast -c "bash scripts/record-cli-demo.sh"
#   # Then convert: agg demo.cast vulca/assets/demo.gif --cols 90 --rows 28
#
#   # Option 2: VHS (charmbracelet)
#   vhs scripts/record-cli-demo.tape
#
#   # Option 3: Just run it and screen-record manually
#   bash scripts/record-cli-demo.sh

set -e
cd "$(dirname "$0")/.."

# Use the local venv vulca
VULCA="vulca/.venv/bin/vulca"

# Typing effect
type_cmd() {
    echo ""
    echo -n "$ "
    for ((i=0; i<${#1}; i++)); do
        echo -n "${1:$i:1}"
        sleep 0.03
    done
    echo ""
    sleep 0.3
}

pause() { sleep "${1:-1.5}"; }

clear
echo "  ╔══════════════════════════════════════════════════╗"
echo "  ║          VULCA v0.4.0 — Cultural Art Advisor     ║"
echo "  ║   Make any image generator culturally accurate   ║"
echo "  ╚══════════════════════════════════════════════════╝"
pause 2

# Scene 1: Version
type_cmd "vulca --version"
$VULCA --version
pause

# Scene 2: List traditions
type_cmd "vulca traditions"
$VULCA traditions
pause 2

# Scene 3: Evaluate (strict mode — the default)
type_cmd "vulca evaluate painting.jpg --mock -t chinese_xieyi"
$VULCA evaluate /dev/null --mock -t chinese_xieyi
pause 3

# Scene 4: Evaluate (reference mode — advisor, not judge)
type_cmd "vulca evaluate painting.jpg --mock -t chinese_xieyi --mode reference"
$VULCA evaluate /dev/null --mock -t chinese_xieyi --mode reference
pause 3

# Scene 5: Fusion mode (multi-tradition comparison)
type_cmd "vulca evaluate painting.jpg --mock -t chinese_xieyi,watercolor,western_academic --mode fusion"
$VULCA evaluate /dev/null --mock -t chinese_xieyi,watercolor,western_academic --mode fusion
pause 3

# Scene 6: Custom tradition
type_cmd "vulca tradition --init cyberpunk_ink"
$VULCA tradition --init cyberpunk_ink | head -20
echo "  ..."
pause 2

# Scene 7: Create with reference mode
type_cmd "vulca create '水墨山水' --provider mock --mode reference -t chinese_xieyi"
$VULCA create '水墨山水' --provider mock --mode reference -t chinese_xieyi
pause 2

# Scene 8: JSON output (show new fields)
type_cmd "vulca evaluate painting.jpg --mock --json | python3 -c \"import sys,json; d=json.load(sys.stdin); print('suggestions:', list(d['suggestions'].values())[:2]); print('deviation_types:', list(d['deviation_types'].values())[:2]); print('eval_mode:', d['eval_mode'])\""
$VULCA evaluate /dev/null --mock --json | python3 -c "import sys,json; d=json.load(sys.stdin); print('suggestions:', list(d['suggestions'].values())[:2]); print('deviation_types:', list(d['deviation_types'].values())[:2]); print('eval_mode:', d['eval_mode'])"
pause 2

echo ""
echo "  ──────────────────────────────────────────────────"
echo "  pip install vulca          # install"
echo "  vulca evaluate img.jpg     # evaluate any image"
echo "  vulca evaluate --mode reference  # advisor mode"
echo "  vulca tradition --init X   # create custom tradition"
echo "  ──────────────────────────────────────────────────"
echo ""
pause 3
