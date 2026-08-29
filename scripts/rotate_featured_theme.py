#!/usr/bin/env python3
"""Rotate the featured Omarchy theme in the profile README."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

START_MARKER = "<!-- featured-theme:start -->"
END_MARKER = "<!-- featured-theme:end -->"
ANCHOR_DATE = date(2026, 8, 29)


@dataclass(frozen=True)
class Theme:
    name: str
    slug: str
    description: str

    @property
    def repository_url(self) -> str:
        return f"https://github.com/nibra180/omarchy-{self.slug}-theme"

    @property
    def preview_url(self) -> str:
        return f"https://raw.githubusercontent.com/nibra180/omarchy-{self.slug}-theme/main/preview.png"


THEMES = (
    Theme(
        "Pripyat",
        "pripyat",
        "Soot-black green, concrete haze, oxidized steel, and radiation-yellow accents, inspired by HBO's *Chernobyl*.",
    ),
    Theme("Sequoia", "sequoia", "Forest shadow, sequoia bark, and meadow gold"),
    Theme("Highlands", "highlands", "Charcoal crags, Scots pine, and lichen light"),
    Theme("Yellowstone", "yellowstone", "Volcanic brown, geothermal blue, and sulfur gold"),
)


def featured_theme(day: date) -> Theme:
    return THEMES[(day - ANCHOR_DATE).days % len(THEMES)]


def render_card(theme: Theme) -> str:
    return (
        f"[![{theme.name} desktop preview]({theme.preview_url})]({theme.repository_url})\n\n"
        f"**[{theme.name}]({theme.repository_url})**<br><sub>{theme.description}</sub>"
    )


def render_other_themes(featured: Theme) -> str:
    others = [theme for theme in THEMES if theme != featured]
    previews = " | ".join(
        f"[![{theme.name} desktop preview]({theme.preview_url})]({theme.repository_url})"
        for theme in others
    )
    alignment = " | ".join(":---:" for _ in others)
    labels = " | ".join(
        f"**[{theme.name}]({theme.repository_url})**<br><sub>{theme.description}</sub>"
        for theme in others
    )
    return f"| {previews} |\n| {alignment} |\n| {labels} |"


def render_section(day: date) -> str:
    featured = featured_theme(day)
    return "\n".join(
        (
            START_MARKER,
            "### Featured theme",
            "",
            render_card(featured),
            "",
            "### More themes",
            "",
            render_other_themes(featured),
            END_MARKER,
        )
    )


def update_readme(path: Path, day: date) -> bool:
    content = path.read_text()
    start = content.find(START_MARKER)
    end = content.find(END_MARKER)
    if start == -1 or end == -1 or end < start:
        raise RuntimeError(f"Missing or invalid featured-theme markers in {path}")

    end += len(END_MARKER)
    updated = content[:start] + render_section(day) + content[end:]
    if updated == content:
        return False

    path.write_text(updated)
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=date.fromisoformat, help="UTC date override in YYYY-MM-DD format")
    parser.add_argument("--readme", type=Path, default=Path(__file__).resolve().parents[1] / "README.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    day = args.date or datetime.now(timezone.utc).date()
    changed = update_readme(args.readme, day)
    print(f"Featured theme: {featured_theme(day).name} ({day.isoformat()})")
    print("README updated" if changed else "README already current")


if __name__ == "__main__":
    main()
