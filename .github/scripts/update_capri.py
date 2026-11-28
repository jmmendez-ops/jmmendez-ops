"""Generates a 10s-switching Capri companion SVG and builds the profile README."""

from __future__ import annotations

import base64
import html
import json
import random
import re
import textwrap
import urllib.request
from dataclasses import dataclass
from pathlib import Path

CAPRI_REPO_URL = "https://github.com/lachydotmcg/capri-desktop"
CAPRI_RAW_BASE = (
    "https://raw.githubusercontent.com/lachydotmcg/capri-desktop/main/assets/readme"
)
STATE_PATTERN = re.compile(r"<!--\s*capri-state:\s*(\{.*?\})\s*-->")

REPO_ROOT = Path(__file__).resolve().parents[2]
README_PATH = REPO_ROOT / "README.md"
SVG_PATH = REPO_ROOT / "assets" / "capri-roam.svg"

SVG_WIDTH = 260
SVG_HEIGHT = 250
SWITCH_SECONDS = 10


@dataclass(frozen=True)
class CapriState:
    """Represents a Capri desktop state with animation and short speech line."""

    filename: str
    lines: tuple[str, ...]
    width: int = 210
    height: int = 210


CAPRI_STATES: tuple[CapriState, ...] = (
    CapriState(
        "talk.webp",
        ("Hey choom!", "Net's been quiet...", "Looking sharp, choom."),
        210,
        210,
    ),
    CapriState(
        "idle.webp",
        ("Hanging out.", "Watching your commits.", "Need a Python script?"),
        210,
        210,
    ),
    CapriState(
        "perch.webp",
        ("Perching here.", "Nice view, choom.", "Don't mind me."),
        200,
        200,
    ),
    CapriState(
        "perch-music.webp",
        ("Good pick, choom.", "Vibing to music...", "Catching the beat."),
        200,
        200,
    ),
    CapriState(
        "sleep.webp",
        ("Night night...", "Power-saving mode.", "Zzz..."),
        210,
        210,
    ),
    CapriState(
        "glitch.webp",
        ("[glitching...]", "[signal static]", "[reconnecting...]"),
        210,
        210,
    ),
)

SIDE_SLOTS: tuple[str, ...] = ("hero_right", "hero_left")


def fetch_webp_data_uri(filename: str) -> str:
    """Download a Capri WebP animation and return it as a base64 data URI."""
    url = f"{CAPRI_RAW_BASE}/{filename}"
    req = urllib.request.Request(url, headers={"User-Agent": "capri-roam-bot/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw_bytes = resp.read()
    encoded = base64.b64encode(raw_bytes).decode("ascii")
    return f"data:image/webp;base64,{encoded}"


def build_svg_widget() -> str:
    """Build a transparent Capri companion SVG with a minimal speech pill."""
    states = list(CAPRI_STATES)
    random.shuffle(states)
    count = len(states)
    total_duration = count * SWITCH_SECONDS
    slot_pct = 100.0 / count

    css_rules: list[str] = []
    state_groups: list[str] = []

    for idx, state in enumerate(states):
        start_pct = idx * slot_pct
        end_pct = (idx + 1) * slot_pct

        if idx == 0:
            kf = (
                f"0%, {end_pct - 0.01:.2f}% {{ opacity: 1; }}\n"
                f"      {end_pct:.2f}%, 100% {{ opacity: 0; }}"
            )
        else:
            kf = (
                f"0%, {start_pct - 0.01:.2f}% {{ opacity: 0; }}\n"
                f"      {start_pct:.2f}%, {end_pct - 0.01:.2f}% {{ opacity: 1; }}\n"
                f"      {end_pct:.2f}%, 100% {{ opacity: 0; }}"
            )

        css_rules.append(
            f"    @keyframes c{idx} {{ {kf} }}\n"
            f"    .c{idx} {{ opacity: 0; animation: c{idx} {total_duration}s steps(1,end) infinite; }}"
        )

        line_text = random.choice(state.lines)
        img_x = (SVG_WIDTH - state.width) // 2 + random.randint(-8, 8)
        img_y = 34 + random.randint(0, 6)
        data_uri = fetch_webp_data_uri(state.filename)
        accent = "#fd004f" if state.filename == "glitch.webp" else "#01f76d"

        state_groups.append(
            f'  <g class="c{idx}">\n'
            f'    <rect x="28" y="4" width="204" height="24" rx="12" '
            f'fill="#120e19" stroke="{accent}" stroke-width="1.2" />\n'
            f'    <text x="130" y="20" text-anchor="middle" fill="#ece8f1" '
            f'font-family="\'Share Tech Mono\', Consolas, monospace" font-size="11">'
            f"{html.escape(line_text)}</text>\n"
            f'    <image x="{img_x}" y="{img_y}" width="{state.width}" height="{state.height}" href="{data_uri}" />\n'
            f"  </g>"
        )

    styles = "\n".join(css_rules)
    groups = "\n".join(state_groups)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" width="{SVG_WIDTH}" height="{SVG_HEIGHT}">\n'
        f"  <style>\n{styles}\n  </style>\n"
        f"{groups}\n"
        f"</svg>\n"
    )


def read_previous_side(readme_text: str) -> str | None:
    """Extract the previous Capri side placement from README.md."""
    match = STATE_PATTERN.search(readme_text)
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    return data.get("side")


def pick_next_side(prev_side: str | None) -> str:
    """Alternate or pick a Capri placement beside the name/intro."""
    choices = [s for s in SIDE_SLOTS if s != prev_side]
    return random.choice(choices or SIDE_SLOTS)


ICON_BASE = "https://api.iconify.design/lucide"


def icon(name: str, color: str = "58a6ff", size: int = 16) -> str:
    """Return a crisp Lucide SVG icon tag for GitHub Markdown."""
    return (
        f'<img src="{ICON_BASE}/{name}.svg?color=%23{color}" '
        f'width="{size}" height="{size}" align="absmiddle" alt="{name}">'
    )


def build_readme(side: str) -> str:
    """Build the profile README with Capri floating right beside the intro.

    Uses ### (H3) instead of ## (H2) in the hero so GitHub's H2 bottom border
    never cuts across the floated Capri companion image, and uses Lucide icons
    instead of emojis.
    """
    capri_float = (
        '<img src="assets/capri-roam.svg" alt="Capri desktop companion" width="250" align="right">'
    )

    hero_section = f"""{capri_float}

### {icon("terminal", "58a6ff", 20)} Hey, I'm John Paulo Mendez

`@jmmendez-ops` · CS Student · Philippines

*Turning small ideas into working tools, mostly through Python automation.*

- {icon("bot", "3fb950")} Building & exploring **Python automation scripts** — file parsers, batch processors, `.txt`/`.csv` CLI tools
- {icon("zap", "d29922")} Broadening my stack with **React** and **Node.js**
- {icon("lock", "a371f7")} Several **private projects** in progress
- {icon("lightbulb", "e3b341")} Always experimenting with small ideas that solve real (or fun) problems

<br clear="right">"""

    tech_stack_section = f"""\
## {icon("cpu", "58a6ff", 22)} Tech Stack

### Languages & Markup
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Dart](https://img.shields.io/badge/Dart-0175C2?style=for-the-badge&logo=dart&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

### Frameworks & Libraries
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)

### Databases
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![MariaDB](https://img.shields.io/badge/MariaDB-003545?style=for-the-badge&logo=mariadb&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

### Tools
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)
![VS Code](https://img.shields.io/badge/VS_Code-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)
![Antigravity](https://img.shields.io/badge/Antigravity-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Termux](https://img.shields.io/badge/Termux-000000?style=for-the-badge&logo=gnubash&logoColor=white)
![Android Studio](https://img.shields.io/badge/Android_Studio-3DDC84?style=for-the-badge&logo=androidstudio&logoColor=white)
![Figma](https://img.shields.io/badge/Figma-F24E1E?style=for-the-badge&logo=figma&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)"""

    fun_facts_section = f"""\
## {icon("sparkles", "a371f7", 22)} Beyond the Terminal

- {icon("paw-print", "f778ba")} **12 cats and 2 dogs** to feed
- {icon("book-open", "58a6ff")} Love reading **manhwa & manga**
- {icon("gamepad-2", "a371f7")} Play lots of **gacha games**
- {icon("smartphone", "3fb950")} Enjoy **Termux** tweaking"""

    state_json = json.dumps({"side": "hero_right", "interval_sec": SWITCH_SECONDS})
    footer = (
        f'<div align="right"><sub>Capri companion art by '
        f'<a href="{CAPRI_REPO_URL}">lachydotmcg/capri-desktop</a></sub></div>\n'
        f"<!-- capri-state: {state_json} -->"
    )

    return "\n\n".join(
        [hero_section, tech_stack_section, fun_facts_section, footer]
    ) + "\n"


def main() -> None:
    """Generate the 10s-switching Capri SVG widget and update README.md."""
    SVG_PATH.parent.mkdir(parents=True, exist_ok=True)
    SVG_PATH.write_text(build_svg_widget(), encoding="utf-8")

    current_text = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""
    prev_side = read_previous_side(current_text)
    next_side = pick_next_side(prev_side)
    README_PATH.write_text(build_readme(next_side), encoding="utf-8")
    print(f"Updated profile -> Capri beside intro ({next_side})")


if __name__ == "__main__":
    main()
