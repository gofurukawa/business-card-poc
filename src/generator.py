#!/usr/bin/env python3
"""
Business Card Generator
Generates PNG business card images from JSON layout specifications.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


# ============================================================================
# Exceptions
# ============================================================================


class CardGeneratorError(Exception):
    """Base exception for card generator."""

    pass


class FontNotFoundError(CardGeneratorError):
    """Raised when required font cannot be found."""

    pass


# ============================================================================
# Configuration
# ============================================================================

FONT_FILES = {
    "gothic": {
        "light": ["NotoSansJP-Light.ttf", "NotoSansJP-Light.otf"],
        "regular": ["NotoSansJP-Regular.ttf", "NotoSansJP-Regular.otf"],
        "bold": ["NotoSansJP-Bold.ttf", "NotoSansJP-Bold.otf"],
    },
    "mincho": {
        "light": ["NotoSerifJP-Light.ttf", "NotoSerifJP-Light.otf"],
        "regular": ["NotoSerifJP-Regular.ttf", "NotoSerifJP-Regular.otf"],
        "bold": ["NotoSerifJP-Bold.ttf", "NotoSerifJP-Bold.otf"],
    },
}


@dataclass
class CardConfig:
    """Configuration for card generation."""

    dpi: int = 300
    font_paths: list[Path] = field(default_factory=lambda: [Path("fonts")])

    @property
    def mm_to_px_ratio(self) -> float:
        """Conversion ratio from mm to pixels."""
        return self.dpi / 25.4

    def mm_to_px(self, mm: float) -> int:
        """Convert millimeters to pixels."""
        return round(mm * self.mm_to_px_ratio)

    def pt_to_px(self, pt: float) -> int:
        """Convert points to pixels."""
        return round(pt * self.dpi / 72)


# ============================================================================
# Font Management
# ============================================================================


class FontManager:
    """Manages font loading and caching."""

    def __init__(self, config: CardConfig):
        self.config = config
        self._cache: dict[tuple, ImageFont.FreeTypeFont] = {}

    def _find_font_file(self, category: str, weight: str) -> Path | None:
        """Search for font file in configured paths."""
        candidates = FONT_FILES.get(category, {}).get(weight, [])
        for font_path in self.config.font_paths:
            for filename in candidates:
                full_path = font_path / filename
                if full_path.exists():
                    return full_path
        return None

    def get_font(
        self, category: str, size_pt: float, weight: str = "regular"
    ) -> ImageFont.FreeTypeFont:
        """Get font with caching. Raises FontNotFoundError if font not found."""
        cache_key = (category, size_pt, weight)
        if cache_key not in self._cache:
            font_path = self._find_font_file(category, weight)
            if font_path is None:
                searched_paths = ", ".join(str(p) for p in self.config.font_paths)
                raise FontNotFoundError(
                    f"Font not found: {category}/{weight}. "
                    f"Searched in: {searched_paths}"
                )
            size_px = self.config.pt_to_px(size_pt)
            self._cache[cache_key] = ImageFont.truetype(str(font_path), size_px)
        return self._cache[cache_key]


# ============================================================================
# Placeholder Substitution
# ============================================================================

PLACEHOLDER_PATTERN = re.compile(r"\{\{(\w+)\}\}")


def substitute_placeholders(text: str, values: dict[str, str]) -> str:
    """Replace {{KEY}} placeholders with values."""

    def replacer(match: re.Match) -> str:
        key = match.group(1)
        return values.get(key, match.group(0))

    return PLACEHOLDER_PATTERN.sub(replacer, text)


# ============================================================================
# Element Renderers
# ============================================================================


def render_text_element(
    draw: ImageDraw.ImageDraw,
    element: dict[str, Any],
    config: CardConfig,
    font_manager: FontManager,
    placeholders: dict[str, str],
) -> None:
    """Render a text element."""
    content = substitute_placeholders(element["content"], placeholders)
    font_spec = element["font"]

    font = font_manager.get_font(
        font_spec["category"],
        font_spec["size_pt"],
        font_spec.get("weight", "regular"),
    )

    x_px = config.mm_to_px(element["position"]["x_mm"])
    y_px = config.mm_to_px(element["position"]["y_mm"])

    align = element.get("align", "left")
    if align in ("center", "right"):
        bbox = draw.textbbox((0, 0), content, font=font)
        text_width = bbox[2] - bbox[0]
        if align == "center":
            x_px -= text_width // 2
        else:  # right
            x_px -= text_width

    color = font_spec.get("color", "#000000")
    draw.text((x_px, y_px), content, font=font, fill=color)


# ============================================================================
# Main Generator
# ============================================================================


class CardGenerator:
    """Generates business card images from JSON layouts."""

    def __init__(self, config: CardConfig | None = None):
        self.config = config or CardConfig()
        self.font_manager = FontManager(self.config)

    def load_layout(self, path: Path) -> dict[str, Any]:
        """Load and parse JSON layout file."""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def render(
        self,
        layout: dict[str, Any],
        output_path: Path,
        placeholders: dict[str, str] | None = None,
    ) -> None:
        """Render layout to PNG image."""
        placeholders = placeholders or {}

        # Create image
        card_spec = layout["card"]
        width_px = self.config.mm_to_px(card_spec["width_mm"])
        height_px = self.config.mm_to_px(card_spec["height_mm"])
        background = card_spec.get("background", "#FFFFFF")

        image = Image.new("RGB", (width_px, height_px), background)
        draw = ImageDraw.Draw(image)

        # Render elements
        for element in layout.get("elements", []):
            element_type = element.get("type")
            if element_type == "text":
                render_text_element(
                    draw, element, self.config, self.font_manager, placeholders
                )

        # Save output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, "PNG")
        print(f"Generated: {output_path}")


# ============================================================================
# CLI
# ============================================================================


def parse_set_args(set_args: list[str]) -> dict[str, str]:
    """Parse --set KEY="value" arguments."""
    result = {}
    for arg in set_args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            result[key] = value.strip('"').strip("'")
    return result


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate business card images from JSON layouts"
    )
    parser.add_argument("template", type=Path, help="JSON layout template")
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("output/card.png"), help="Output PNG file path"
    )
    parser.add_argument(
        "--set",
        action="append",
        default=[],
        dest="set_args",
        metavar='KEY="value"',
        help="Set placeholder value (can be used multiple times)",
    )
    parser.add_argument("--font-path", type=Path, help="Custom font directory path")
    parser.add_argument(
        "--dpi", type=int, default=300, help="Output resolution (default: 300)"
    )

    args = parser.parse_args()

    # Configure font paths
    font_paths = [Path("fonts")]
    if args.font_path:
        font_paths.insert(0, args.font_path)

    config = CardConfig(dpi=args.dpi, font_paths=font_paths)

    # Generate
    try:
        generator = CardGenerator(config)
        layout = generator.load_layout(args.template)
        placeholders = parse_set_args(args.set_args)

        generator.render(layout, args.output, placeholders)
        return 0
    except FontNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
