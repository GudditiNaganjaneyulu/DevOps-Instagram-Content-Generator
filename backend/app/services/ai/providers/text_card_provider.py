"""
Renders @runtimeemotions / Runtime.xFeelings style text cards.
- Black background, monospace font
- ALL_CAPS words syntax-highlighted
- Each line individually centered
- Blank lines between stanzas create breathing room
- </> divider + @handle footer
"""
import io
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from app.core.exceptions import ProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)

SIZE = 1080
PAD = 80
BG = (8, 8, 8)
TEXT_COLOR = (210, 210, 210)
DIM_COLOR = (90, 90, 90)
SEP_COLOR = (50, 50, 50)
HANDLE = "@devopsemotions"
TAGLINE = "// Follow for more"

HIGHLIGHT_COLORS = [
    (224, 108, 117),  # red
    (152, 195, 121),  # green
    (97,  175, 239),  # blue
    (198, 120, 221),  # purple
    (86,  182, 194),  # cyan
    (229, 192, 123),  # orange
]

SPEAKER_COLOR  = (130, 130, 130)   # dim gray for "Manager:", "DevOps:" labels
CODE_COLOR     = (86,  182, 194)   # cyan for code commands (chmod, kubectl, terraform)

# Unix/cloud commands that should render in code color
CODE_COMMANDS = {
    "chmod", "kubectl", "terraform", "docker", "git", "sudo",
    "rm", "curl", "helm", "ansible", "vagrant", "pip", "npm",
}

_BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/UbuntuMono-B.ttf",
    "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
    "/Library/Fonts/Courier New Bold.ttf",
]
_REGULAR_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
    "/Library/Fonts/Courier New.ttf",
]


def _load_font(size: int, bold: bool = True):
    for path in (_BOLD_PATHS if bold else _REGULAR_PATHS):
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _is_highlight(word: str) -> bool:
    core = re.sub(r"[^A-Za-z0-9]", "", word)
    return len(core) >= 2 and core == core.upper() and not core.isdigit()


def _word_color(word: str, color_map: dict) -> tuple:
    key = re.sub(r"[^A-Z0-9]", "", word.upper())
    if key not in color_map:
        color_map[key] = HIGHLIGHT_COLORS[len(color_map) % len(HIGHLIGHT_COLORS)]
    return color_map[key]


def _text_width(font, text: str) -> int:
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def _draw_line_centered(draw, line: str, y: int, font, color_map: dict,
                        line_type: str = "normal") -> None:
    total_w = _text_width(font, line)
    x = (SIZE - total_w) // 2

    # Speaker labels ("Manager:") — render entirely in dim gray
    if line_type == "speaker":
        draw.text((x, y), line, font=font, fill=SPEAKER_COLOR)
        return

    # Code lines — first token gets CODE_COLOR, rest get syntax highlight
    for token in re.split(r"(\s+)", line):
        if not token:
            continue
        if token.strip() == "":
            x += _text_width(font, token)
            continue
        token_lower = token.lower().rstrip(":").rstrip()
        if token_lower in CODE_COMMANDS:
            color = CODE_COLOR
        elif _is_highlight(token):
            color = _word_color(token, color_map)
        else:
            color = TEXT_COLOR
        draw.text((x, y), token, font=font, fill=color)
        x += _text_width(font, token)


_SPEAKER_RE  = re.compile(r"^[A-Za-z][A-Za-z0-9 ]{1,24}:\s*$")   # "Manager:" alone on a line
_CODE_LINE_RE = re.compile(r"^(chmod|kubectl|terraform|docker|git|sudo|rm -|helm|curl)\b")


def _line_type(text: str) -> str:
    """Returns 'speaker', 'code', or 'normal'."""
    if _SPEAKER_RE.match(text):
        return "speaker"
    if _CODE_LINE_RE.match(text.lower()):
        return "code"
    return "normal"


def _parse_lines(prompt: str) -> list:
    """Returns list of (text, is_blank, line_type)."""
    raw = re.split(r"\\n|\n", prompt.strip())
    result = []
    prev_type = "normal"
    for raw_line in raw:
        stripped = raw_line.strip()
        if not stripped:
            result.append(("", True, "blank"))
            prev_type = "blank"
            continue
        ltype = _line_type(stripped)
        # Auto-gap before a new speaker if no blank already
        if ltype == "speaker" and result and prev_type not in ("blank", "speaker"):
            result.append(("", True, "blank"))
        result.append((stripped, False, ltype))
        prev_type = ltype
    return result


class TextCardProvider:
    name = "textcard"

    async def generate(self, prompt: str, width: int = 1080, height: int = 1080) -> bytes:
        try:
            parsed = _parse_lines(prompt)
            real_lines = [t for t, blank, _ in parsed if not blank]
            n = len(real_lines)
            max_len = max(len(l) for l in real_lines) if real_lines else 20

            # Font size
            if n <= 4 and max_len <= 26:
                font_size = 60
            elif n <= 5 and max_len <= 30:
                font_size = 54
            elif n <= 7 and max_len <= 34:
                font_size = 48
            elif n <= 9:
                font_size = 42
            else:
                font_size = 36

            font = _load_font(font_size, bold=True)
            small_font = _load_font(26, bold=False)

            sample_bbox = font.getbbox("Mg")
            cap_h = sample_bbox[3] - sample_bbox[1]
            line_h = int(cap_h * 1.85)        # normal line spacing
            blank_h = int(cap_h * 1.0)        # stanza gap (shorter than full line)

            # Calculate total height
            total_h = 0
            for _, is_blank, _ in parsed:
                total_h += blank_h if is_blank else line_h

            start_y = (SIZE - total_h - 160) // 2

            img = Image.new("RGB", (SIZE, SIZE), BG)
            draw = ImageDraw.Draw(img)
            color_map: dict = {}

            y = start_y
            for text, is_blank, ltype in parsed:
                if is_blank:
                    y += blank_h
                    continue
                _draw_line_centered(draw, text, y, font, color_map, ltype)
                y += line_h

            # Divider </> ———
            div_y = y + 44
            tag = "</>"
            tag_bbox = small_font.getbbox(tag)
            tag_w = tag_bbox[2] - tag_bbox[0]
            tag_h = tag_bbox[3] - tag_bbox[1]
            cx = SIZE // 2
            draw.text((cx - tag_w // 2, div_y), tag, font=small_font, fill=DIM_COLOR)
            mid_y = div_y + tag_h // 2
            draw.line([(PAD, mid_y), (cx - tag_w // 2 - 24, mid_y)], fill=SEP_COLOR, width=1)
            draw.line([(cx + tag_w // 2 + 24, mid_y), (SIZE - PAD, mid_y)], fill=SEP_COLOR, width=1)

            # Footer
            footer_y = div_y + tag_h + 28
            handle_w = _text_width(small_font, HANDLE)
            draw.text(((SIZE - handle_w) // 2, footer_y), HANDLE, font=small_font, fill=DIM_COLOR)
            tagline_w = _text_width(small_font, TAGLINE)
            draw.text(((SIZE - tagline_w) // 2, footer_y + 36), TAGLINE,
                      font=small_font, fill=(60, 60, 60))

            buf = io.BytesIO()
            img.save(buf, format="PNG", optimize=True)
            buf.seek(0)
            image_bytes = buf.read()
            logger.info("TextCard rendered", lines=n, font_size=font_size, bytes=len(image_bytes))
            return image_bytes

        except Exception as e:
            raise ProviderError(self.name, str(e))
