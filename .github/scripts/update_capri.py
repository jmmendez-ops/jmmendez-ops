"""Randomly rotates Capri's animation and position in the profile README."""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass
from pathlib import Path

CAPRI_REPO_URL = "https://github.com/lachydotmcg/capri-desktop"
CAPRI_RAW_BASE = (
    "https://raw.githubusercontent.com/lachydotmcg/capri-desktop/main/assets/readme"
)
STATE_PATTERN = re.compile(r"<!--\s*capri-state:\s*(\{.*?\})\s*-->")
README_PATH = Path(__file__).resolve().parents[2] / "README.md"


@dataclass(frozen=True)
class CapriAnimation:
    """Represents a Capri character animation asset."""

    filename: str
    alt: str
    width: int = 120


ANIMATIONS: tuple[CapriAnimation, ...] = (
    CapriAnimation("idle.webp", "Capri idling and blinking", 130),
    CapriAnimation("talk.webp", "Capri talking", 130),
    CapriAnimation("tossed.webp", "Capri flailing while dragged", 130),
    CapriAnimation("glitch.webp", "Capri glitching", 130),
    CapriAnimation("sleep.webp", "Capri napping and booting back up", 130),
    CapriAnimation("perch.webp", "Capri perching and blinking", 115),
    CapriAnimation("perch-music.webp", "Capri swaying to music", 115),
)

SLOTS: tuple[str, ...] = (
    "top_center",
    "top_left",
    "top_right",
    "about_left",
    "about_right",
    "tech_header",
    "tech_frameworks",
    "tech_tools",
    "fun_facts_right",
    "bottom_center",
    "bottom_right",
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


def read_previous_state(readme_text: str) -> tuple[str | None, str | None]:
    """Extract the previous animation filename and slot from README.md."""
    match = STATE_PATTERN.search(readme_text)
    if not match:
        return None, None
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None, None
    return data.get("animation"), data.get("slot")


def pick_next_state(
    prev_animation: str | None, prev_slot: str | None
) -> tuple[CapriAnimation, str]:
    """Pick a new animation and slot, guaranteeing both change on each switch."""
    anim_choices = [a for a in ANIMATIONS if a.filename != prev_animation]
    slot_choices = [s for s in SLOTS if s != prev_slot]
    return random.choice(anim_choices or ANIMATIONS), random.choice(slot_choices or SLOTS)


def render_capri_img(anim: CapriAnimation) -> str:
    """Render the linked Capri image tag."""
    src = f"{CAPRI_RAW_BASE}/{anim.filename}"
    return (
        f'<a href="{CAPRI_REPO_URL}" title="Capri by lachydotmcg/capri-desktop">'
        f'<img src="{src}" alt="{anim.alt}" width="{anim.width}">'
        f"</a>"
    )


def render_aligned_block(anim: CapriAnimation, align: str) -> str:
    """Render a standalone aligned Capri block."""
    return f'<div align="{align}">\n  {render_capri_img(anim)}\n</div>'


def render_side_by_side(left_html: str, right_html: str) -> str:
    """Render two blocks side-by-side using a borderless-friendly Markdown table."""
    return (
        "<table>\n"
        "  <tr>\n"
        f'    <td valign="top">\n\n{left_html}\n\n    </td>\n'
        f'    <td align="center" valign="middle" width="160">\n\n{right_html}\n\n    </td>\n'
        "  </tr>\n"
        "</table>"
    )


def build_readme(anim: CapriAnimation, slot: str) -> str:
    """Build the full README.md with Capri placed in the selected slot."""
    img_tag = render_capri_img(anim)
    parts: list[str] = []

    if slot in ("top_center", "top_left", "top_right"):
        align = slot.split("_", 1)[1]
        parts.append(render_aligned_block(anim, align))

    parts.append("---")

    if slot == "about_left":
        parts.append(
            "<table>\n"
            "  <tr>\n"
            f'    <td align="center" valign="middle" width="160">\n\n{img_tag}\n\n    </td>\n'
            f'    <td valign="top">\n\n{ABOUT_ME_CONTENT}\n\n    </td>\n'
            "  </tr>\n"
            "</table>"
        )
    elif slot == "about_right":
        parts.append(render_side_by_side(ABOUT_ME_CONTENT, img_tag))
    else:
        parts.append(ABOUT_ME_CONTENT)

    parts.append("---")

    if slot == "tech_header":
        parts.append(f'<img src="{CAPRI_RAW_BASE}/{anim.filename}" alt="{anim.alt}" width="{anim.width}" align="right">')

    parts.append("## 💻 Tech Stack")
    parts.append(LANGUAGES_SECTION)

    if slot == "tech_frameworks":
        parts.append(render_side_by_side(FRAMEWORKS_SECTION, img_tag))
    else:
        parts.append(FRAMEWORKS_SECTION)

    parts.append(DATABASES_SECTION)

    if slot == "tech_tools":
        parts.append(render_side_by_side(TOOLS_SECTION, img_tag))
    else:
        parts.append(TOOLS_SECTION)

    parts.append("---")

    if slot == "fun_facts_right":
        parts.append(render_side_by_side(FUN_FACTS_CONTENT, img_tag))
    else:
        parts.append(FUN_FACTS_CONTENT)

    if slot in ("bottom_center", "bottom_right"):
        align = slot.split("_", 1)[1]
        parts.append(render_aligned_block(anim, align))

    state_json = json.dumps({"animation": anim.filename, "slot": slot})
    parts.append(
        f'<div align="right"><sub>Capri companion art by '
        f'<a href="{CAPRI_REPO_URL}">lachydotmcg/capri-desktop</a></sub></div>\n'
        f"<!-- capri-state: {state_json} -->"
    )

    return "\n\n".join(parts) + "\n"


def main() -> None:
    """Update README.md with a newly chosen Capri animation and position."""
    current_text = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""
    prev_anim, prev_slot = read_previous_state(current_text)
    next_anim, next_slot = pick_next_state(prev_anim, prev_slot)
    updated_text = build_readme(next_anim, next_slot)
    README_PATH.write_text(updated_text, encoding="utf-8")
    print(f"Updated Capri -> animation={next_anim.filename}, slot={next_slot}")


if __name__ == "__main__":
    main()
