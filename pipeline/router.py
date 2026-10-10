"""Former generator of block task files (legacy, permanently disabled).

It contained hard-coded prices without any opened source and overwrote the hand-maintained
files (docs/cost-estimates/blocks, pipeline/tasks). Owner rule: invented figures must not be written;
unknown values are written as 'not found'. Blocks are edited by hand; see docs/reports/unknowns-and-open-issues.md.
"""
import sys

sys.exit(
    "DISABLED: router.py is blocked and does not regenerate estimate blocks or task files "
    "(it held unsourced prices). Edit docs/cost-estimates/blocks/*.md by hand."
)
