from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CANVAS = (1440, 1920)
GOLD = (231, 181, 65)
IVORY = (246, 243, 235)
SERIF = Path(r"C:\Windows\Fonts\NotoSerifSC-VF.ttf")
LOGO = ROOT / "brand" / "低温水獭_logo_gold.png"


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(SERIF), size=size)


def portrait_crop(source: Image.Image, focus_x: float) -> Image.Image:
    target_w, target_h = 1440, 1450
    ratio = target_w / target_h
    src = source.convert("RGB")
    if src.width / src.height > ratio:
        crop_w = round(src.height * ratio)
        center = round(src.width * focus_x)
        left = max(0, min(src.width - crop_w, center - crop_w // 2))
        src = src.crop((left, 0, left + crop_w, src.height))
    else:
        crop_h = round(src.width / ratio)
        top = max(0, (src.height - crop_h) // 2)
        src = src.crop((0, top, src.width, top + crop_h))
    return src.resize((target_w, target_h), Image.Resampling.LANCZOS)


def centered(draw: ImageDraw.ImageDraw, text: str, y: int, size: int, fill: tuple[int, int, int]) -> None:
    fnt = font(size)
    box = draw.textbbox((0, 0), text, font=fnt, stroke_width=2)
    width = box[2] - box[0]
    draw.text(
        ((CANVAS[0] - width) // 2, y),
        text,
        font=fnt,
        fill=fill,
        stroke_width=2,
        stroke_fill=(5, 5, 4),
    )


def render(source: Path, output: Path, lines: list[tuple[str, int, tuple[int, int, int]]], focus_x: float) -> None:
    image = Image.open(source).convert("RGB")
    photo = portrait_crop(image, focus_x)
    photo = ImageEnhance.Contrast(photo).enhance(1.10)
    photo = ImageEnhance.Color(photo).enhance(0.82)
    photo = ImageEnhance.Brightness(photo).enhance(0.73)

    canvas = Image.new("RGBA", CANVAS, (7, 7, 6, 255))
    canvas.alpha_composite(photo.convert("RGBA"), (0, 0))

    veil = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    px = veil.load()
    for y in range(CANVAS[1]):
        top = 92 if y < 240 else 0
        bottom = 0 if y < 680 else min(255, round((y - 680) / 660 * 255))
        alpha = max(top, bottom)
        if alpha:
            for x in range(CANVAS[0]):
                px[x, y] = (4, 4, 3, alpha)
    canvas.alpha_composite(veil)

    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rounded_rectangle((152, 1330, 452, 1337), radius=4, fill=GOLD)
    logo = Image.open(LOGO).convert("RGBA").resize((104, 104), Image.Resampling.LANCZOS)
    canvas.alpha_composite(logo, (1272, 50))

    ys = [1390, 1530, 1680]
    for (text, size, color), y in zip(lines, ys):
        centered(draw, text, y, size, color)

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, quality=95, subsampling=0, optimize=True)


def main() -> None:
    jobs = [
        (
            ROOT / "content" / "2026-09-22_JK-Rowling_失败与重建" / "frames" / "02.png",
            ROOT / "content" / "2026-09-22_JK-Rowling_失败与重建" / "封面.jpg",
            [("失败，", 116, IVORY), ("会帮你", 126, IVORY), ("看清自己", 132, GOLD)],
            0.50,
        ),
        (
            ROOT / "content" / "2026-09-22_Brene-Brown_脆弱与勇敢" / "frames" / "08.png",
            ROOT / "content" / "2026-09-22_Brene-Brown_脆弱与勇敢" / "封面.jpg",
            [("脆弱，", 116, IVORY), ("是另一种", 126, IVORY), ("勇敢", 132, GOLD)],
            0.50,
        ),
    ]
    for source, output, lines, focus_x in jobs:
        render(source, output, lines, focus_x)
        print(output)


if __name__ == "__main__":
    main()
