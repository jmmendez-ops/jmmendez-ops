"""Generates a 10s-switching Capri companion SVG and builds the profile README."""

from __future__ import annotations

import base64
import json
import random
import re
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

SVG_WIDTH = 200
SVG_HEIGHT = 180
SWITCH_SECONDS = 10


@dataclass(frozen=True)
class CapriAnimation:
    """Represents a Capri character animation asset."""

    filename: str
    alt: str
    width: int = 135
    height: int = 135


ANIMATIONS: tuple[CapriAnimation, ...] = (
    CapriAnimation("idle.webp", "Capri hanging out and blinking", 135, 135),
    CapriAnimation("glitch.webp", "Capri glitching", 135, 135),
    CapriAnimation("sleep.webp", "Capri napping and booting back up", 135, 135),
    CapriAnimation("perch.webp", "Capri perching on your window", 125, 125),
    CapriAnimation("perch-music.webp", "Capri swaying to your music", 125, 125),
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
    """Build a compact SVG that switches Capri's animation and offset every 10s."""
    shuffled = list(ANIMATIONS)
    random.shuffle(shuffled)
    count = len(shuffled)
    total_duration = count * SWITCH_SECONDS

    css_rules: list[str] = []
    image_tags: list[str] = []

    for idx, anim in enumerate(shuffled):
        start_pct = (idx * 100.0) / count
        end_pct = ((idx + 1) * 100.0) / count
        max_x = max(10, SVG_WIDTH - anim.width - 10)
        max_y = max(10, SVG_HEIGHT - anim.height - 10)
        x_pos = random.randint(10, max_x)
        y_pos = random.randint(10, max_y)

        if idx == 0:
            keyframes = (
                f"0%, {end_pct - 0.01:.2f}% {{ opacity: 1; }}\n"
                f"      {end_pct:.2f}%, 100% {{ opacity: 0; }}"
            )
        else:
            keyframes = (
                f"0%, {start_pct - 0.01:.2f}% {{ opacity: 0; }}\n"
                f"      {start_pct:.2f}%, {end_pct - 0.01:.2f}% {{ opacity: 1; }}\n"
                f"      {end_pct:.2f}%, 100% {{ opacity: 0; }}"
            )

        css_rules.append(
            f"    @keyframes capri-step-{idx} {{\n"
            f"      {keyframes}\n"
            f"    }}\n"
            f"    .capri-{idx} {{\n"
            f"      opacity: 0;\n"
            f"      animation: capri-step-{idx} {total_duration}s steps(1, end) infinite;\n"
            f"    }}"
        )

        data_uri = fetch_webp_data_uri(anim.filename)
        image_tags.append(
            f'  <image class="capri-{idx}" x="{x_pos}" y="{y_pos}" '
            f'width="{anim.width}" height="{anim.height}" href="{data_uri}" />'
        )

    styles = "\n".join(css_rules)
    images = "\n".join(image_tags)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" width="{SVG_WIDTH}" height="{SVG_HEIGHT}">\n'
        f"  <style>\n{styles}\n  </style>\n"
        f"{images}\n"
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


def build_readme(side: str) -> str:
    """Build the profile README with Capri floating right/left beside the intro.

    Uses align="right" or align="left" on the img tag — the only GitHub-safe
    way to float an image beside text without leaking raw HTML tags.
    """
    capri_align = "right" if side == "hero_right" else "left"

    # Float Capri beside the intro text using a plain aligned img.
    # GitHub renders markdown after a floating img correctly.
    capri_float = (
        f'<a href="{CAPRI_REPO_URL}" title="Capri by lachydotmcg/capri-desktop">'
        f'<img src="assets/capri-roam.svg" alt="Capri companion" width="200" align="{capri_align}">'
        f"</a>"
    )

    hero_section = f"""{capri_float}

## 👋 Hey, I'm John Paulo Mendez

`@jmmendez-ops` · CS Student · Philippines 🇵🇭

> Turning small ideas into working tools, mostly through Python automation.

- 🐍 Building & exploring **Python automation scripts** — file parsers, batch processors, `.txt`/`.csv` CLI tools
- ⚡ Broadening my stack with **React** and **Node.js**
- 🔒 Several **private projects** in progress
- 💡 Always experimenting with small ideas that solve real (or fun) problems

<br clear="{capri_align}">"""

    tech_stack_section = """\
## 💻 Tech Stack

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

    fun_facts_section = """\
## ✨ Beyond the Terminal

- 🐾 **12 cats and 2 dogs** to feed
- 📖 Love reading **manhwa & manga**
- 🎮 Play lots of **gacha games**
- 📱 Enjoy **Termux** tweaking"""

    state_json = json.dumps({"side": side, "interval_sec": SWITCH_SECONDS})
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
