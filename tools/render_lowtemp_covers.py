from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CANVAS = (1440, 1920)
GOLD = (235, 184, 62)
WHITE = (250, 249, 244)
FONT = Path(r"C:\Windows\Fonts\msyhbd.ttc")
LOGO = ROOT / "brand" / "低温水獭_logo_gold.png"


def fnt(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT), size=size)


def centered(draw: ImageDraw.ImageDraw, y: int, text: str, size: int, fill=GOLD) -> None:
    font = fnt(size)
    box = draw.textbbox((0, 0), text, font=font, stroke_width=3)
    width = box[2] - box[0]
    draw.text(((CANVAS[0] - width) // 2, y), text, font=font, fill=fill,
              stroke_width=3, stroke_fill=(18, 13, 5))


def make_cover(source: Path, output: Path, lines: list[str], focus_x: int) -> None:
    src = Image.open(source).convert("RGB")
    # 只取已排版页面中未出现正文字幕的真人画面区域，避开旧页眉和字幕卡。
    crop_h = 930
    crop_w = round(crop_h * 1440 / 1300)
    left = max(0, min(src.width - crop_w, focus_x - crop_w // 2))
    photo = src.crop((left, 175, left + crop_w, 175 + crop_h))
    photo = photo.resize((1440, 1300), Image.Resampling.LANCZOS)
    photo = ImageEnhance.Contrast(photo).enhance(1.06)

    canvas = Image.new("RGBA", CANVAS, (9, 9, 8, 255))
    canvas.alpha_composite(photo.convert("RGBA"), (0, 0))
    overlay = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    px = overlay.load()
    for y in range(850, 1400):
        alpha = min(255, round(255 * (y - 850) / 550))
        for x in range(CANVAS[0]):
            px[x, y] = (7, 7, 6, alpha)
    canvas.alpha_composite(overlay)

    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rounded_rectangle((52, 48, 430, 112), radius=10, fill=(0, 0, 0, 145),
                           outline=(*GOLD, 190), width=2)
    draw.text((78, 62), "低温水獭 · 人物访谈", font=fnt(30), fill=GOLD)

    logo = Image.open(LOGO).convert("RGBA").resize((104, 104), Image.Resampling.LANCZOS)
    canvas.alpha_composite(logo, (1278, 42))

    draw.rounded_rectangle((506, 1308, 934, 1316), radius=4, fill=GOLD)
    sizes = [86, 102, 102]
    ys = [1380, 1510, 1660]
    for text, size, y in zip(lines, sizes, ys):
        centered(draw, y, text, size)

    draw.text((72, 1842), "LOW TEMPERATURE OTTER", font=fnt(25), fill=(185, 169, 125))
    draw.rounded_rectangle((1242, 1838, 1368, 1878), radius=20, fill=GOLD)
    draw.text((1270, 1845), "今日", font=fnt(24), fill=(18, 14, 6))

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, quality=95, subsampling=0, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*", default=[])
    args = parser.parse_args()
    jobs = [
        (
            "michelle",
            ROOT / "content" / "2026-09-15_Michelle-Yeoh_受伤与重启" / "成品" / "02.jpg",
            ROOT / "content" / "2026-09-15_Michelle-Yeoh_受伤与重启" / "封面.jpg",
            ["杨紫琼：", "全身打满石膏后", "我真的想过放弃"],
            520,
        ),
        (
            "jensen",
            ROOT / "content" / "2026-09-15_Jensen-Huang_创业与支撑" / "成品" / "02.jpg",
            ROOT / "content" / "2026-09-15_Jensen-Huang_创业与支撑" / "封面.jpg",
            ["黄仁勋：", "如果重来一次", "我不会创办英伟达"],
            540,
        ),
        (
            "taylor",
            ROOT / "content" / "2026-09-21_Taylor-Swift_拒绝与创造" / "成品" / "02.jpg",
            ROOT / "content" / "2026-09-21_Taylor-Swift_拒绝与创造" / "封面.jpg",
            ["泰勒·斯威夫特：", "那些没被选中的时刻", "后来都在帮我"],
            610,
        ),
        (
            "oprah",
            ROOT / "content" / "2026-09-21_Oprah-Winfrey_公开失败" / "成品" / "05.jpg",
            ROOT / "content" / "2026-09-21_Oprah-Winfrey_公开失败" / "封面.jpg",
            ["奥普拉：", "站在事业巅峰后", "我经历了最公开的失败"],
            710,
        ),
    ]
    for name, source, output, lines, focus_x in jobs:
        if args.only and name not in args.only:
            continue
        make_cover(source, output, lines, focus_x)
        print(output)


if __name__ == "__main__":
    main()
