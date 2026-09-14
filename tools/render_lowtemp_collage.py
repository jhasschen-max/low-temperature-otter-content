import importlib.util
from pathlib import Path

from PIL import ImageDraw


SKILL_SCRIPT = Path(
    r"F:\CodexHome\skills\native-subtitle-quote-image\scripts\native_subtitle_stitch.py"
)

spec = importlib.util.spec_from_file_location("native_subtitle_stitch", SKILL_SCRIPT)
stitch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stitch)


def draw_lowtemp_subtitle(image, text, y_center, font_path, font_size, max_width):
    draw = ImageDraw.Draw(image)
    size = font_size
    font = stitch.load_subtitle_font(font_path, size, text)
    stroke = max(2, size // 18)
    box = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
    if box[2] - box[0] > max_width:
        raise SystemExit(
            f"台词过长，请拆句或缩短；为保持统一字号不会自动缩小：{text!r}"
        )
    text_width = box[2] - box[0]
    text_height = box[3] - box[1]
    x = (image.width - text_width) // 2 - box[0]
    y = y_center - text_height // 2 - box[1]

    band_padding = max(12, round(size * 0.24))
    band_top = max(0, round(y_center - text_height / 2 - band_padding))
    band_bottom = min(image.height, round(y_center + text_height / 2 + band_padding))
    overlay = ImageDraw.Draw(image, "RGBA")
    overlay.rectangle((0, band_top, image.width, band_bottom), fill=(0, 0, 0, 184))

    draw = ImageDraw.Draw(image)
    draw.text(
        (x, y),
        text,
        font=font,
        fill="white",
        stroke_width=stroke,
        stroke_fill="black",
    )


stitch.draw_scripted_subtitle = draw_lowtemp_subtitle
stitch.main()
