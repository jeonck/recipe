#!/usr/bin/env python3
"""사이트 아바타/파비콘 생성기 — 김이 오르는 그릇 마크."""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "img")
S = 1024  # 작업 해상도 (다운샘플링으로 안티에일리어싱)


def make():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 둥근 사각 배경에 위에서 아래로 따뜻한 그러데이션
    bg = Image.new("RGB", (S, S))
    bp = bg.load()
    top, bottom = (0xE0, 0x6C, 0x3E), (0xB0, 0x2E, 0x2E)
    for y in range(S):
        t = y / float(S)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        for x in range(S):
            bp[x, y] = c
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, S - 1, S - 1), radius=int(S * 0.24), fill=255)
    img.paste(bg, (0, 0), mask)

    cream = (255, 244, 232, 255)

    # 김 세 줄기 — 둥근 점을 촘촘히 찍어 매끄러운 물결을 만든다
    r = S * 0.016
    for i, cx in enumerate((S * 0.36, S * 0.5, S * 0.64)):
        for step in range(161):
            t = step / 160.0
            y = S * 0.17 + t * S * 0.24
            x = cx + math.sin(t * math.pi * 2 + i * 1.1) * S * 0.035
            d.ellipse((x - r, y - r, x + r, y + r), fill=cream[:3] + (210,))

    # 그릇 — 반원 몸통
    bowl = (S * 0.14, S * 0.46, S * 0.86, S * 0.86)
    d.pieslice(bowl, start=0, end=180, fill=cream)

    # 그릇 테두리(림)
    d.rounded_rectangle(
        (S * 0.10, S * 0.435, S * 0.90, S * 0.505),
        radius=int(S * 0.035),
        fill=cream,
    )

    # 받침
    d.rounded_rectangle(
        (S * 0.34, S * 0.855, S * 0.66, S * 0.905),
        radius=int(S * 0.025),
        fill=cream[:3] + (235,),
    )

    return img


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    art = make()
    art.resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, "avatar.png"), optimize=True)
    art.filter(ImageFilter.GaussianBlur(2)).resize((180, 180), Image.LANCZOS).save(
        os.path.join(OUT, "favicon.png"), optimize=True
    )
    print("wrote avatar.png, favicon.png")
