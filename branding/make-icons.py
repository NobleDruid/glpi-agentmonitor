#!/usr/bin/env python3
"""Generate Abundant Logic tray icons + logo for the Agent Monitor.

Usage (from repo root): python3 branding/make-icons.py   (needs Pillow: apt install python3-pil)
Writes Resources/glpiok.ico (normal), Resources/glpierr.ico (agent error) and Resources/glpilogo.png
(filenames kept so the .rc file needs no change). Source: branding/abundantlogic-logo.png, same
artwork as the agent installer (NobleDruid/glpi-agent contrib/windows/packaging/branding/).
"""
import os
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "Resources")
SRC = Image.open(os.path.join(HERE, "abundantlogic-logo.png")).convert("RGB")
CUBE_BOX, BG = (372, 55, 653, 383), (244, 244, 244)   # cube in the 1024x559 source; off-white bg


def cut_cube():
    crop = SRC.crop(CUBE_BOX)
    out = Image.new("RGBA", crop.size)
    cp, op = crop.load(), out.load()
    for y in range(crop.height):
        for x in range(crop.width):
            r, g, b = cp[x, y]
            dist = ((r - BG[0]) ** 2 + (g - BG[1]) ** 2 + (b - BG[2]) ** 2) ** 0.5
            a = max(0.0, min(1.0, (dist - 14) / 70))
            if a <= 0:
                op[x, y] = (0, 0, 0, 0)
                continue
            col = tuple(max(0, min(255, round((c - (1 - a) * bc) / a))) for c, bc in zip((r, g, b), BG))
            op[x, y] = col + (round(a * 255),)
    return out.crop(out.getbbox())


CUBE = cut_cube()


def cube_icon(size, error=False):
    s = min(size / CUBE.width, size / CUBE.height)
    c = CUBE.resize((max(1, round(CUBE.width * s)), max(1, round(CUBE.height * s))), Image.LANCZOS)
    if error:   # greyed cube + red "!" badge bottom-right
        alpha = c.getchannel("A")
        c = ImageEnhance.Brightness(c.convert("L").convert("RGB")).enhance(0.85).convert("RGBA")
        c.putalpha(alpha)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    img.alpha_composite(c, ((size - c.width) // 2, (size - c.height) // 2))
    if error:
        d = ImageDraw.Draw(img)
        r = max(4, round(size * 0.30))
        x1, y1 = size - 1, size - 1
        d.ellipse([x1 - 2 * r, y1 - 2 * r, x1, y1], fill=(220, 38, 38, 255), outline=(255, 255, 255, 255), width=max(1, size // 24))
        if size >= 24:
            f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", round(r * 1.5))
            d.text((x1 - r, y1 - r), "!", font=f, fill=(255, 255, 255, 255), anchor="mm")
        else:   # 16px: draw the "!" as pixels
            cx = x1 - r
            d.line([(cx, y1 - 2 * r + 2), (cx, y1 - 4)], fill=(255, 255, 255, 255))
            d.point((cx, y1 - 2), fill=(255, 255, 255, 255))
    return img


def write_ico(path, sizes, error=False):
    sizes = sorted(sizes, reverse=True)
    imgs = [cube_icon(s, error) for s in sizes]
    imgs[0].save(path, format="ICO", sizes=[(s, s) for s in sizes], append_images=imgs[1:], bitmap_format="bmp")


SIZES = [16, 20, 24, 32, 40, 48, 64, 138, 256]   # 20/40 = tray at 125%/250% scaling
write_ico(os.path.join(RES, "glpiok.ico"), SIZES)
write_ico(os.path.join(RES, "glpierr.ico"), SIZES, error=True)
cube_icon(90).save(os.path.join(RES, "glpilogo.png"))
prev = Image.new("RGBA", (2 * (16 + 24 + 32 + 48 + 90) + 120, 2 * 100), (255, 255, 255, 255))
ImageDraw.Draw(prev).rectangle([0, 100, prev.width, 200], fill=(32, 32, 32, 255))
x = 10
for err in (False, True):
    for s in (16, 24, 32, 48, 90):
        for row in (0, 100):
            prev.alpha_composite(cube_icon(s, err), (x, row + 95 - s))
        x += s + 10
    x += 20
prev.save(os.path.join(HERE, "preview-icons.png"))
print("generated Resources/glpiok.ico, Resources/glpierr.ico, Resources/glpilogo.png")
