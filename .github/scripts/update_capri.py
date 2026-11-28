"""Generates a 10s-switching Capri SVG banner and rotates its README.md section."""

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

SVG_WIDTH = 800
SVG_HEIGHT = 160
SWITCH_SECONDS = 10


@dataclass(frozen=True)
class CapriAnimation:
    """Represents a Capri character animation asset."""

    filename: str
    alt: str
    width: int = 120
    height: int = 120


ANIMATIONS: tuple[CapriAnimation, ...] = (
    CapriAnimation("idle.webp", "Capri idling and blinking", 120, 120),
    CapriAnimation("talk.webp", "Capri talking", 120, 120),
    CapriAnimation("tossed.webp", "Capri flailing while dragged", 120, 120),
    CapriAnimation("glitch.webp", "Capri glitching", 120, 120),
    CapriAnimation("sleep.webp", "Capri napping and booting back up", 120, 120),
    CapriAnimation("perch.webp", "Capri perching and blinking", 110, 110),
    CapriAnimation("perch-music.webp", "Capri swaying to music", 110, 110),
)

SLOTS: tuple[str, ...] = (
    "top_banner",
    "between_about_tech",
    "inside_tech_frameworks",
    "inside_tech_tools",
    "between_tech_fun",
    "bottom_banner",
)

ABOUT_ME_CONTENT = """### 📝 About Me
This Fella is a Computer Science student from the Philippines, currently learning the ropes of software development. I like turning small ideas into working tools, mostly through Python automation.

- 🐍 I like Building & Exploring Python automation scripts. Things such as file parsers, batch processor and small tools that take .txt/.csv input and turn repetitive tasks into one command.
- Currently learning other tech stacks such as React and Node.js to broaden my development skills.
- I have a bunch of projects in progress (currently private)
- 💡 Always experimenting with small automation ideas that solve a real (or fun) problems"""

LANGUAGES_SECTION = """### Languages & Markup
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Dart](https://img.shields.io/badge/Dart-0175C2?style=for-the-badge&logo=dart&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)"""

FRAMEWORKS_SECTION = """### Frameworks & Libraries
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)<br>
![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)<br>
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)"""

DATABASES_SECTION = """### Databases
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![MariaDB](https://img.shields.io/badge/MariaDB-003545?style=for-the-badge&logo=mariadb&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)"""

TOOLS_SECTION = """### Tools
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)
![VS Code](https://img.shields.io/badge/VS_Code-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)
![Antigravity](https://img.shields.io/badge/Antigravity-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Termux](https://img.shields.io/badge/Termux-000000?style=for-the-badge&logo=gnubash&logoColor=white)<br>
![Android Studio](https://img.shields.io/badge/Android_Studio-3DDC84?style=for-the-badge&logo=androidstudio&logoColor=white)
![Figma](https://img.shields.io/badge/Figma-F24E1E?style=for-the-badge&logo=figma&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)"""

FUN_FACTS_CONTENT = """### Fun facts
- 12 cats and 2 dogs to feed
- Love reading manhwa & manga
- 🎮 Play lots of gacha games
- I enjoy Termux tweaking"""


def fetch_webp_data_uri(filename: str) -> str:
    """Download a Capri WebP animation and return it as a base64 data URI."""
    url = f"{CAPRI_RAW_BASE}/{filename}"
    req = urllib.request.Request(url, headers={"User-Agent": "capri-roam-bot/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw_bytes = resp.read()
    encoded = base64.b64encode(raw_bytes).decode("ascii")
    return f"data:image/webp;base64,{encoded}"


def build_svg_banner() -> str:
    """Build an SVG that switches Capri's animation and X/Y position every 10s."""
    shuffled = list(ANIMATIONS)
    random.shuffle(shuffled)
    count = len(shuffled)
    total_duration = count * SWITCH_SECONDS

    css_rules: list[str] = []
    image_tags: list[str] = []

    for idx, anim in enumerate(shuffled):
        start_pct = (idx * 100.0) / count
        end_pct = ((idx + 1) * 100.0) / count
        x_pos = random.randint(20, SVG_WIDTH - anim.width - 20)
        y_pos = random.randint(5, SVG_HEIGHT - anim.height - 5)

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


def read_previous_slot(readme_text: str) -> str | None:
    """Extract the previous section slot from README.md."""
    match = STATE_PATTERN.search(readme_text)
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    return data.get("slot")


def pick_next_slot(prev_slot: str | None) -> str:
    """Pick a new README section slot, avoiding repeating the current one."""
    choices = [s for s in SLOTS if s != prev_slot]
    return random.choice(choices or SLOTS)


def render_banner_block() -> str:
    """Render the Markdown/HTML block for the roaming Capri SVG banner."""
    return (
        '<div align="center">\n'
        f'  <a href="{CAPRI_REPO_URL}" title="Capri by lachydotmcg/capri-desktop">\n'
        '    <img src="assets/capri-roam.svg" alt="Capri roaming across the profile" width="100%">\n'
        "  </a>\n"
        "</div>"
    )


def build_readme(slot: str) -> str:
    """Build the full README.md with the 10s-roaming Capri banner in the chosen slot."""
    banner = render_banner_block()
    parts: list[str] = []

    if slot == "top_banner":
        parts.append(banner)

    parts.append("---")
    parts.append(ABOUT_ME_CONTENT)
    parts.append("---")

    if slot == "between_about_tech":
        parts.append(banner)

    parts.append("## 💻 Tech Stack")
    parts.append(LANGUAGES_SECTION)

    if slot == "inside_tech_frameworks":
        parts.append(banner)

    parts.append(FRAMEWORKS_SECTION)
    parts.append(DATABASES_SECTION)

    if slot == "inside_tech_tools":
        parts.append(banner)

    parts.append(TOOLS_SECTION)
    parts.append("---")

    if slot == "between_tech_fun":
        parts.append(banner)

    parts.append(FUN_FACTS_CONTENT)

    if slot == "bottom_banner":
        parts.append(banner)

    state_json = json.dumps({"slot": slot, "interval_sec": SWITCH_SECONDS})
    parts.append(
        f'<div align="right"><sub>Capri companion art by '
        f'<a href="{CAPRI_REPO_URL}">lachydotmcg/capri-desktop</a></sub></div>\n'
        f"<!-- capri-state: {state_json} -->"
    )

    return "\n\n".join(parts) + "\n"


def main() -> None:
    """Generate the 10s-switching SVG banner and update README.md."""
    SVG_PATH.parent.mkdir(parents=True, exist_ok=True)
    svg_content = build_svg_banner()
    SVG_PATH.write_text(svg_content, encoding="utf-8")

    current_text = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""
    prev_slot = read_previous_slot(current_text)
    next_slot = pick_next_slot(prev_slot)
    README_PATH.write_text(build_readme(next_slot), encoding="utf-8")
    print(f"Updated Capri -> 10s SVG banner at slot={next_slot}")


if __name__ == "__main__":
    main()
