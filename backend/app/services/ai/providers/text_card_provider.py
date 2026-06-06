"""
Renders @runtimeemotions-style text cards:
- Black background, monospace font
- ALL_CAPS words syntax-highlighted in rotating colors
- </> divider + @handle footer
"""
import io
import re
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from app.core.exceptions import ProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)

SIZE = 1080
PAD = 90
BG = (8, 8, 8)
TEXT_COLOR = (200, 200, 200)
DIM_COLOR = (100, 100, 100)
HANDLE = "@devopsemotions"
TAGLINE = "// Follow for more"

# Syntax-highlight palette (matches @runtimeemotions color scheme)
HIGHLIGHT_COLORS = [
    (224, 108, 117),  # red
    (152, 195, 121),  # green
    (97,  175, 239),  # blue
    (198, 120, 221),  # purple
    (86,  182, 194),  # cyan
    (229, 192, 123),  # orange/yellow
]

# Font search paths (Render = Ubuntu; local Mac)
_FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/UbuntuMono-B.ttf",
    "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
    "/Library/Fonts/Courier New Bold.ttf",
]

_FONT_PATHS_REGULAR = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
    "/Library/Fonts/Courier New.ttf",
]


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    paths = _FONT_PATHS if bold else _FONT_PATHS_REGULAR
    for path in paths:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


# Pre-assign a color to each distinct ALL_CAPS word seen so far
_color_cache: dict[str, tuple] = {}
_color_idx = 0


def _get_color(word: str) -> tuple:
    global _color_idx
    if word not in _color_cache:
        _color_cache[word] = HIGHLIGHT_COLORS[_color_idx % len(HIGHLIGHT_COLORS)]
        _color_idx += 1
    return _color_cache[word]


def _is_highlight(word: str) -> bool:
    clean = re.sub(r"[^A-Za-z0-9_]", "", word)
    return len(clean) >= 2 and clean == clean.upper() and not clean.isdigit()


def _wrap_text(text: str, max_chars: int = 32) -> list[str]:
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        wrapped = textwrap.wrap(paragraph, width=max_chars) or [""]
        lines.extend(wrapped)
    return lines


def _draw_line(draw: ImageDraw.ImageDraw, line: str, x: int, y: int,
               font: ImageFont.FreeTypeFont, char_w: int) -> None:
    """Draw one line with per-word coloring."""
    tokens = re.split(r"(\s+)", line)
    cx = x
    for token in tokens:
        if not token:
            continue
        if token.strip() == "":
            cx += int(len(token) * char_w)
            continue
        color = _get_color(token) if _is_highlight(token) else TEXT_COLOR
        draw.text((cx, y), token, font=font, fill=color)
        bbox = font.getbbox(token)
        cx += bbox[2] - bbox[0]


class TextCardProvider:
    name = "textcard"

    async def generate(self, prompt: str, width: int = 1080, height: int = 1080) -> bytes:
        # `prompt` here is the joke_text, not an image prompt
        global _color_cache, _color_idx
        _color_cache = {}
        _color_idx = 0

        try:
            img = Image.new("RGB", (SIZE, SIZE), BG)
            draw = ImageDraw.Draw(img)

            lines = _wrap_text(prompt, max_chars=34)

            # Choose font size based on line count
            n = len(lines)
            font_size = 52 if n <= 4 else 46 if n <= 6 else 40 if n <= 8 else 34
            font = _load_font(font_size, bold=True)
            small_font = _load_font(28, bold=False)

            # Measure character width for spacing
            bbox = font.getbbox("M")
            char_w = bbox[2] - bbox[0]
            line_h = int((bbox[3] - bbox[1]) * 1.6)

            # Total text block height
            total_h = len(lines) * line_h
            start_y = (SIZE - total_h) // 2 - 60

            # Draw each line centered
            for i, line in enumerate(lines):
                if not line:
                    continue
                bbox_line = font.getbbox(line) if line else (0, 0, 0, 0)
                line_w = bbox_line[2] - bbox_line[0]
                lx = (SIZE - line_w) // 2
                ly = start_y + i * line_h
                _draw_line(draw, line, lx, ly, font, char_w)

            # Divider  </> ————
            divider_y = start_y + total_h + 50
            sep_color = (60, 60, 60)
            tag_text = "</>"
            tag_bbox = small_font.getbbox(tag_text)
            tag_w = tag_bbox[2] - tag_bbox[0]
            cx = SIZE // 2
            draw.text((cx - tag_w // 2, divider_y), tag_text, font=small_font, fill=DIM_COLOR)
            line_y = divider_y + (tag_bbox[3] - tag_bbox[1]) // 2
            draw.line([(PAD, line_y), (cx - tag_w // 2 - 20, line_y)], fill=sep_color, width=1)
            draw.line([(cx + tag_w // 2 + 20, line_y), (SIZE - PAD, line_y)], fill=sep_color, width=1)

            # Footer
            footer_y = divider_y + 50
            handle_bbox = small_font.getbbox(HANDLE)
            handle_w = handle_bbox[2] - handle_bbox[0]
            draw.text(((SIZE - handle_w) // 2, footer_y), HANDLE, font=small_font, fill=DIM_COLOR)
            tag_bbox2 = small_font.getbbox(TAGLINE)
            tag_w2 = tag_bbox2[2] - tag_bbox2[0]
            draw.text(((SIZE - tag_w2) // 2, footer_y + 38), TAGLINE, font=small_font, fill=(70, 70, 70))

            buf = io.BytesIO()
            img.save(buf, format="PNG", optimize=True)
            buf.seek(0)
            image_bytes = buf.read()
            logger.info("TextCard image rendered", lines=len(lines), bytes=len(image_bytes))
            return image_bytes

        except Exception as e:
            raise ProviderError(self.name, str(e))
