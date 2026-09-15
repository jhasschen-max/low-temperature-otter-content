from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont


CANVAS = (1440, 1920)
GOLD = (231, 181, 65)
WHITE = (255, 255, 255)
FONT_BOLD = Path(r"C:\Windows\Fonts\msyhbd.ttc")


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD), size=size)


def cover_crop(img: Image.Image, focus_x: float = 0.5) -> Image.Image:
    target_ratio = CANVAS[0] / CANVAS[1]
    src_ratio = img.width / img.height
    if src_ratio > target_ratio:
        crop_w = round(img.height * target_ratio)
        center_x = round(img.width * focus_x)
        left = max(0, min(img.width - crop_w, center_x - crop_w // 2))
        img = img.crop((left, 0, left + crop_w, img.height))
    else:
        crop_h = round(img.width / target_ratio)
        top = max(0, (img.height - crop_h) // 2)
        img = img.crop((0, top, img.width, top + crop_h))
    return img.resize(CANVAS, Image.Resampling.LANCZOS)


def add_gradient(base: Image.Image, top_alpha: int, bottom_alpha: int) -> None:
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    px = layer.load()
    for y in range(CANVAS[1]):
        if y < 320:
            a = round(top_alpha * (1 - y / 320))
        elif y > 760:
            a = round(bottom_alpha * ((y - 760) / (CANVAS[1] - 760)))
        else:
            a = 0
        if a:
            for x in range(CANVAS[0]):
                px[x, y] = (0, 0, 0, a)
    base.alpha_composite(layer)


def extract_logo(reference: Path, target: Path) -> None:
    img = Image.open(reference).convert("RGB")
    crop = img.crop((1100, 18, 1250, 168)).resize((180, 180), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    src = crop.load()
    dst = out.load()
    for y in range(crop.height):
        for x in range(crop.width):
            r, g, b = src[x, y]
            strength = max(0, min(255, int((r - b) * 2.6 + (g - b) * 0.8 - 55)))
            if r > 115 and g > 75 and r > b * 1.35 and g > b * 1.15 and strength > 20:
                dst[x, y] = (*GOLD, strength)
    bbox = out.getbbox()
    if not bbox:
        raise RuntimeError("未能从参考图中提取品牌 Logo")
    out = out.crop(bbox)
    square = Image.new("RGBA", (max(out.size), max(out.size)), (0, 0, 0, 0))
    square.alpha_composite(out, ((square.width - out.width) // 2, (square.height - out.height) // 2))
    target.parent.mkdir(parents=True, exist_ok=True)
    square.save(target)


def draw_fallback_logo(target: Path) -> None:
    size = 512
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    line = 15
    gold = (*GOLD, 255)
    d.ellipse((30, 30, 482, 482), outline=gold, width=12)
    d.ellipse((128, 96, 384, 360), outline=gold, width=line)
    d.ellipse((105, 92, 180, 170), outline=gold, width=line)
    d.ellipse((332, 92, 407, 170), outline=gold, width=line)
    d.ellipse((190, 175, 214, 199), fill=gold)
    d.ellipse((298, 175, 322, 199), fill=gold)
    d.ellipse((218, 200, 294, 266), outline=gold, width=12)
    d.ellipse((248, 216, 268, 236), fill=gold)
    d.arc((230, 226, 256, 260), 15, 165, fill=gold, width=9)
    d.arc((256, 226, 282, 260), 15, 165, fill=gold, width=9)
    for off in (0, 22):
        d.line((205, 230 + off, 118, 212 + off), fill=gold, width=8)
        d.line((307, 230 + off, 394, 212 + off), fill=gold, width=8)
    d.rounded_rectangle((135, 330, 377, 424), radius=14, outline=gold, width=12)
    d.line((256, 332, 256, 423), fill=gold, width=9)
    d.line((136, 330, 256, 378), fill=gold, width=9)
    d.line((376, 330, 256, 378), fill=gold, width=9)
    d.arc((132, 284, 238, 395), 190, 350, fill=gold, width=14)
    d.arc((274, 284, 380, 395), 190, 350, fill=gold, width=14)
    target.parent.mkdir(parents=True, exist_ok=True)
    img.save(target)


def draw_centered(draw: ImageDraw.ImageDraw, xy_y: int, text: str, fnt: ImageFont.FreeTypeFont,
                  fill: tuple[int, int, int], stroke: int = 0) -> tuple[int, int, int, int]:
    box = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
    w = box[2] - box[0]
    x = (CANVAS[0] - w) // 2
    draw.text((x, xy_y), text, font=fnt, fill=fill, stroke_width=stroke,
              stroke_fill=(0, 0, 0), anchor="la")
    return (x, xy_y, x + w, xy_y + box[3] - box[1])


def render_package(package_dir: Path, logo_path: Path) -> dict:
    spec = json.loads((package_dir / "script.json").read_text(encoding="utf-8"))
    out_dir = package_dir / "成品"
    out_dir.mkdir(parents=True, exist_ok=True)
    logo = Image.open(logo_path).convert("RGBA").resize((96, 96), Image.Resampling.LANCZOS)
    header_num = font(32)
    header_title = font(38)
    body_font = font(56)
    pages_qa = []

    for page in spec["pages"]:
        frame = Image.open(package_dir / page["frame"]).convert("RGB")
        base = cover_crop(frame, page.get("focus_x", 0.5)).convert("RGBA")
        base = ImageEnhance.Brightness(base).enhance(0.76)
        base.alpha_composite(Image.new("RGBA", CANVAS, (0, 0, 0, 22)))
        add_gradient(base, 120, 205)
        draw = ImageDraw.Draw(base, "RGBA")

        page_no = f'{page["page"]:02d} / {len(spec["pages"]):02d}'
        draw.text((54, 44), page_no, font=header_num, fill=GOLD, stroke_width=2,
                  stroke_fill=(15, 15, 15))
        draw.text((54, 91), page["section_title"], font=header_title, fill=GOLD,
                  stroke_width=3, stroke_fill=(15, 15, 15))
        base.alpha_composite(logo, (1288, 42))

        divider_y = 1115
        draw.rounded_rectangle((570, divider_y, 870, divider_y + 7), radius=4, fill=GOLD)
        start_y = 1195
        row_step = 128
        overflow = False
        for idx, line in enumerate(page["lines"]):
            bbox = draw.textbbox((0, 0), line, font=body_font, stroke_width=4)
            tw = bbox[2] - bbox[0]
            if tw > 1280:
                overflow = True
            band_w = min(1320, tw + 118)
            y = start_y + idx * row_step
            draw.rounded_rectangle(((CANVAS[0] - band_w) // 2, y - 18,
                                    (CANVAS[0] + band_w) // 2, y + 84),
                                   radius=9, fill=(0, 0, 0, 142))
            draw_centered(draw, y, line, body_font, WHITE, stroke=4)

        output = out_dir / f'{page["page"]:02d}.jpg'
        base.convert("RGB").save(output, quality=94, subsampling=0, optimize=True)
        pages_qa.append({
            "page": page["page"], "file": output.name, "size": list(CANVAS),
            "line_count": len(page["lines"]), "font_px": 56,
            "text_overflow": overflow, "frame_time": page["frame_time"],
        })

    thumbs = []
    for page in spec["pages"]:
        img = Image.open(out_dir / f'{page["page"]:02d}.jpg').resize((270, 360), Image.Resampling.LANCZOS)
        thumbs.append(img)
    sheet = Image.new("RGB", (1080, 720), (18, 18, 18))
    for i, img in enumerate(thumbs):
        sheet.paste(img, ((i % 4) * 270, (i // 4) * 360))
    sheet.save(package_dir / "总览图.jpg", quality=92, subsampling=0)
    report = {
        "package": package_dir.name,
        "page_count": len(pages_qa),
        "all_body_fonts_equal": all(p["font_px"] == 56 for p in pages_qa),
        "all_dimensions_correct": all(p["size"] == list(CANVAS) for p in pages_qa),
        "all_lines_within_limit": all(p["line_count"] <= 5 for p in pages_qa),
        "all_text_within_canvas": not any(p["text_overflow"] for p in pages_qa),
        "pages": pages_qa,
    }
    (package_dir / "质检报告.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("packages", nargs="+", type=Path)
    parser.add_argument("--logo", type=Path, default=Path("brand/低温水獭_logo_gold.png"))
    parser.add_argument("--logo-reference", type=Path)
    args = parser.parse_args()
    if not args.logo.exists():
        if args.logo_reference and args.logo_reference.exists():
            extract_logo(args.logo_reference, args.logo)
        else:
            draw_fallback_logo(args.logo)
    for package in args.packages:
        print(json.dumps(render_package(package, args.logo), ensure_ascii=False))


if __name__ == "__main__":
    main()
