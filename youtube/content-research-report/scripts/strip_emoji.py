#!/usr/bin/env python3
"""Strip emoji and other problematic Unicode from Markdown before PDF conversion.

Usage:
    python3 strip_emoji.py input.md > cleaned.md
    # or in-place:
    python3 strip_emoji.py input.md --in-place
"""

import sys
import re


def strip_emoji(text: str) -> str:
    """Replace emoji characters with text equivalents or remove them."""
    replacements = {
        # Fire / hot indicators
        "\U0001f525": "",       # 🔥
        # Target / goal
        "\U0001f3af": "[TARGET] ",  # 🎯
        # Priority indicators
        "\U0001f534": "[HIGH] ",    # 🔴
        "\U0001f7e1": "[MED] ",     # 🟡
        "\U0001f7e2": "[LOW] ",     # 🟢
        # Video / media
        "\U0001f3ac": "[VIDEO] ",   # 🎬
        # Stars
        "\u2b50": "",           # ⭐
        # Arrows
        "\u2192": "->",         # →
        # Misc
        "\U0001f50d": "",       # 🔍
        "\U0001f4ca": "",       # 📊
        "\U0001f680": "",       # 🚀
        "\u2705": "",           # ✅
        "\u26a0\ufe0f": "",     # ⚠️
        "\u274c": "",           # ❌
        "\U0001f4a1": "",       # 💡
        "\U0001f440": "",       # 👀
        "\u270f\ufe0f": "",     # ✏️
        "\U0001f4dd": "",       # 📝
        "\u23f3": "",           # ⏳
        "\u2611\ufe0f": "",     # ☑️
    }

    # Apply known replacements
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Strip any remaining emoji and symbols (U+1F300-U+1FAFF, U+2600-U+27BF, U+2300-U+23FF, U+2B50, U+FE0F)
    text = re.sub(r'[\U0001f300-\U0001faff\u2600-\u27bf\u2300-\u23ff\ufe0f]', '', text)

    return text


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 strip_emoji.py <file.md> [--in-place]", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    in_place = "--in-place" in sys.argv

    with open(path, "r") as f:
        content = f.read()

    cleaned = strip_emoji(content)

    if in_place:
        with open(path, "w") as f:
            f.write(cleaned)
        print(f"Cleaned {path} in-place")
    else:
        sys.stdout.write(cleaned)