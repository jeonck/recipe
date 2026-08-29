#!/usr/bin/env python3
"""레시피 커버 이미지 생성기.

음식 사진 대신, 위에서 내려다본 접시를 단순한 도형으로 그린 플랫 일러스트를 만든다.
팔레트는 각 레시피의 첫 번째 카테고리에서 고르고, 폴더 이름을 시드로 써서
같은 레시피는 몇 번을 돌려도 같은 그림이 나온다.

    python3 scripts/gen_covers.py            # cover.png 없는 레시피만 생성
    python3 scripts/gen_covers.py --force    # 전부 다시 생성

content/recipes/ 아래 페이지 번들을 직접 훑기 때문에 따로 목록을 관리할 필요가 없다.
"""
import math
import os
import pathlib
import random
import sys

from PIL import Image, ImageDraw

W, H = 1200, 630
SS = 3  # 슈퍼샘플링 배율 (부드러운 곡선용)
OUT = os.path.join(os.path.dirname(__file__), "..", "content", "recipes")

# 카테고리별 팔레트: (배경, 접시, 음식 바탕, 고명1, 고명2)
PALETTES = {
    "한식": ("#8E2B22", "#FBEFE0", "#D9482F", "#F4A93C", "#3F6B43"),
    "분식": ("#A32133", "#FCEFDD", "#E5452F", "#F7B23F", "#4F7B4A"),
    "양식": ("#8A5A25", "#FBF2E2", "#E08B37", "#C9433A", "#5E7F4B"),
    "중식": ("#7A1F2B", "#FAEBD9", "#C9432F", "#EDA93A", "#4C7350"),
    "일식": ("#28505C", "#F7F1E3", "#5E9C93", "#E8A552", "#C4523F"),
    "반찬": ("#41562A", "#F8F3E1", "#8FA945", "#E4B441", "#B4552F"),
    "국·찌개": ("#7C3A1E", "#FBEFDD", "#CE6A32", "#EFB852", "#54763F"),
    "디저트": ("#6B3350", "#FDF3EA", "#D98BA6", "#F0C27B", "#8E5A7D"),
}


def hexcol(s):
    s = s.lstrip("#")
    return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def circle(d, cx, cy, r, fill):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)


def background(d, base):
    """배경 + 오른쪽 위로 흐르는 옅은 대각선 띠."""
    d.rectangle((0, 0, W * SS, H * SS), fill=base)
    light = mix(base, (255, 255, 255), 0.10)
    band = W * SS * 0.30
    for i in range(-2, 5):
        x0 = i * band * 1.9
        d.polygon(
            [
                (x0, H * SS),
                (x0 + band, H * SS),
                (x0 + band + H * SS * 0.6, 0),
                (x0 + H * SS * 0.6, 0),
            ],
            fill=light,
        )


def confetti(d, rng, base, accents):
    """접시 주변에 흩뿌린 재료 조각들."""
    for _ in range(26):
        x = rng.uniform(0, W * SS)
        y = rng.uniform(0, H * SS)
        # 접시 영역은 비워둔다
        if math.hypot(x - W * SS * 0.5, y - H * SS * 0.5) < H * SS * 0.42:
            continue
        r = rng.uniform(H * SS * 0.006, H * SS * 0.018)
        col = mix(hexcol(accents[rng.randrange(len(accents))]), base, 0.42)
        if rng.random() < 0.35:
            d.rounded_rectangle(
                (x - r * 1.7, y - r * 0.7, x + r * 1.7, y + r * 0.7),
                radius=r * 0.7,
                fill=col,
            )
        else:
            circle(d, x, y, r, col)


def plate(d, rng, pal):
    """위에서 본 접시: 테두리 → 접시 → 음식 → 고명."""
    base, dish, food, g1, g2 = (hexcol(c) for c in pal)
    cx, cy = W * SS * 0.5, H * SS * 0.5
    r_plate = H * SS * 0.36

    # 접시 그림자
    circle(d, cx, cy + r_plate * 0.045, r_plate * 1.02, mix(base, (0, 0, 0), 0.22))
    # 접시
    circle(d, cx, cy, r_plate, dish)
    # 안쪽 굽 선
    circle(d, cx, cy, r_plate * 0.86, mix(dish, base, 0.10))
    circle(d, cx, cy, r_plate * 0.82, dish)
    # 음식 바탕
    r_food = r_plate * 0.66
    circle(d, cx, cy, r_food, food)

    # 고명: 링 위에 고르게 배치하고 시드로 조금씩 흔든다
    n = rng.choice((5, 6, 7))
    start = rng.uniform(0, math.tau)
    for i in range(n):
        a = start + i * math.tau / n + rng.uniform(-0.12, 0.12)
        rr = r_food * rng.uniform(0.44, 0.62)
        px, py = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        col = g1 if i % 2 == 0 else g2
        size = r_food * rng.uniform(0.15, 0.21)
        shape = rng.random()
        if shape < 0.45:
            circle(d, px, py, size, col)
        elif shape < 0.8:
            d.rounded_rectangle(
                (px - size * 1.5, py - size * 0.6, px + size * 1.5, py + size * 0.6),
                radius=size * 0.6,
                fill=col,
            )
        else:
            d.pieslice(
                (px - size, py - size, px + size, py + size),
                start=rng.uniform(0, 360),
                end=rng.uniform(0, 360) + 210,
                fill=col,
            )

    # 가운데 하이라이트
    circle(d, cx, cy, r_food * 0.22, mix(hexcol(pal[2]), (255, 255, 255), 0.28))


def cutlery(d, pal):
    """접시 양옆 여백에 젓가락 한 쌍씩."""
    col = mix(hexcol(pal[1]), hexcol(pal[0]), 0.34)
    ln = H * SS * 0.34
    gap = H * SS * 0.030
    width = int(H * SS * 0.014)
    for cx, cy, deg in (
        (W * SS * 0.135, H * SS * 0.50, -14),
        (W * SS * 0.865, H * SS * 0.50, 14),
    ):
        a = math.radians(deg)
        dx, dy = math.sin(a), math.cos(a)      # 막대 방향
        px, py = math.cos(a), -math.sin(a)     # 수직 방향
        for off in (-gap, gap):
            ox, oy = px * off, py * off
            d.line(
                [
                    (cx + ox - dx * ln / 2, cy + oy - dy * ln / 2),
                    (cx + ox + dx * ln / 2, cy + oy + dy * ln / 2),
                ],
                fill=col,
                width=width,
            )


def make_at(path, seed, category):
    pal = PALETTES[category]
    rng = random.Random(seed)
    img = Image.new("RGB", (W * SS, H * SS))
    d = ImageDraw.Draw(img)

    background(d, hexcol(pal[0]))
    confetti(d, rng, hexcol(pal[0]), pal[2:])
    cutlery(d, pal)
    plate(d, rng, pal)

    img = img.resize((W, H), Image.LANCZOS)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, "PNG", optimize=True)
    return path


def front_matter_value(md, key):
    """프런트매터에서 key의 첫 번째 값을 꺼낸다(리스트면 첫 항목)."""
    lines = md.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    prefix = key + ":"
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith(prefix):
            raw = line.split(":", 1)[1].strip().strip("[]")
            first = raw.split(",")[0].strip().strip('"').strip("'")
            return first or None
    return None


def targets():
    """(폴더, 카테고리 이름) 목록. 레시피 번들과 카테고리 페이지를 모두 훑는다."""
    content = pathlib.Path(OUT).resolve().parent
    for md in sorted((content / "recipes").glob("*/index.md")):
        yield md.parent, front_matter_value(md, "categories")
    for md in sorted((content / "categories").glob("*/_index.md")):
        yield md.parent, front_matter_value(md, "title")


def main(force=False):
    repo = pathlib.Path(OUT).resolve().parent.parent
    made = 0
    for folder, category in targets():
        cover = folder / "cover.png"
        if cover.exists() and not force:
            continue
        if category not in PALETTES:
            print(f"  건너뜀: {folder.name} (카테고리 {category!r}에 팔레트 없음)")
            continue
        make_at(cover, folder.name, category)
        made += 1
        print(f"  생성: {cover.relative_to(repo)}")
    print(f"커버 {made}개 생성")


if __name__ == "__main__":
    main(force="--force" in sys.argv[1:])
