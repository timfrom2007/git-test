#!/usr/bin/env python3
"""
把 videos/NN-slug/scenes.json 轉成 IG 輪播圖（1080x1350，4:5），輸出到 videos/NN-slug/carousel/。

張數 = 封面 1 張 + 中間重點（scenes[1:-1]）+ 結尾 1 張，超過 8 張會合併最後幾個重點。
輪播沒有聲音，所以每張除了大字卡，還會放旁白全文當內文；結尾放資料來源。

用法：python3 tools/make_carousel.py videos/01-tax-free-refund
"""
import json, sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from make_video import font, wrap, hex2rgb, gradient  # noqa: E402

W, H = 1080, 1350
MAX_SLIDES = 8


def center(d, lines, f, y, fill, stroke=0, spacing=1.25):
    lh = int(f.size * spacing)
    for i, ln in enumerate(lines):
        w = d.textlength(ln, font=f)
        d.text(((W - w) / 2, y + i * lh), ln, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))
    return y + len(lines) * lh


def base(spec):
    bg = gradient(hex2rgb(spec.get("bg1", "#1d2b53")), hex2rgb(spec.get("bg2", "#7e2553")), W, H).convert("RGBA")
    tex = Image.new("RGBA", (W, H), (0, 0, 0, 0)); td = ImageDraw.Draw(tex)
    for x in range(-H, W, 60):
        td.line([(x, 0), (x + H, H)], fill=(255, 255, 255, 10), width=14)
    im = Image.alpha_composite(bg, tex)
    d = ImageDraw.Draw(im)
    brand = spec.get("brand", "")
    if brand:
        f = font(36); tw = d.textlength(brand, font=f)
        d.rounded_rectangle([(W - tw) / 2 - 26, 60, (W + tw) / 2 + 26, 124], 32, fill=(0, 0, 0, 110))
        d.text(((W - tw) / 2, 71), brand, font=f, fill=(255, 255, 255))
    return im


def page_no(d, k, n):
    f = font(34); s = f"{k}/{n}"
    d.text((W - 60 - d.textlength(s, font=f), H - 80), s, font=f, fill=(255, 255, 255, 200))


def slide(spec, sc, k, n, body=None, footer=None, swipe=False):
    im = base(spec); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    acc = hex2rgb(spec.get("accent", "#FFD54A"))
    y = 230 if body or footer else 380
    if sc.get("badge"):
        f = font(50); b = sc["badge"]; tw = d.textlength(b, font=f)
        d.rounded_rectangle([(W - tw) / 2 - 32, y, (W + tw) / 2 + 32, y + 86], 43, fill=acc + (255,))
        d.text(((W - tw) / 2, y + 15), b, font=f, fill=(20, 20, 20))
        y += 130
    head = sc.get("text", "")
    if head:
        size = 104 if len(head.replace("\n", "")) <= 12 else 88
        f = font(size)
        y = center(d, wrap(d, head, f, W - 140), f, y, (255, 255, 255), stroke=5) + 20
    if sc.get("sub"):
        f = font(48)
        y = center(d, wrap(d, sc["sub"], f, W - 160), f, y, acc, stroke=2, spacing=1.35) + 10
    if body:
        f = font(42)
        lines = wrap(d, body, f, W - 220)
        lh = int(42 * 1.5)
        top = max(y + 30, H - 140 - len(lines) * lh - 60)
        d.rounded_rectangle([70, top, W - 70, top + len(lines) * lh + 60], 28, fill=(0, 0, 0, 120))
        for i, ln in enumerate(lines):
            d.text((110, top + 30 + i * lh), ln, font=f, fill=(255, 255, 255, 235))
    if footer:
        f = font(32)
        lines = []
        for para in footer:
            lines += wrap(d, para, f, W - 200)
        lh = int(32 * 1.45)
        top = H - 140 - len(lines) * lh
        for i, ln in enumerate(lines):
            d.text((100, top + i * lh), ln, font=f, fill=(255, 255, 255, 210))
    if swipe:
        f = font(44); s = "左滑看重點 →"
        d.text(((W - d.textlength(s, font=f)) / 2, H - 200), s, font=f, fill=(255, 255, 255, 230))
    page_no(d, k, n)
    return Image.alpha_composite(im, ov).convert("RGB")


def main():
    vd = Path(sys.argv[1])
    spec = json.loads((vd / "scenes.json").read_text(encoding="utf-8"))
    scenes = spec["scenes"]
    mid = [dict(s) for s in scenes[1:-1]]
    while len(mid) + 2 > MAX_SLIDES:  # 合併最後兩個重點
        a, b = mid[-2], mid.pop()
        a["say"] = a["say"] + b["say"]
        a["sub"] = (a.get("sub", "") + "\n" + b.get("text", "").replace("\n", " ")).strip()
    n = len(mid) + 2
    out = vd / "carousel"; out.mkdir(exist_ok=True)
    for old in out.glob("*.jpg"):
        old.unlink()
    cover = spec.get("cover", scenes[0])
    slide(spec, cover, 1, n, swipe=True).save(out / "01.jpg", quality=92)
    for i, sc in enumerate(mid):
        slide(spec, sc, i + 2, n, body=sc["say"]).save(out / f"{i+2:02}.jpg", quality=92)
    end = scenes[-1]
    footer = ["資料來源：" + "、".join(spec.get("sources", [])), f"查核日期：{spec.get('checked', '')}"] if spec.get("sources") else None
    slide(spec, {"text": end.get("text", "").replace("→ 主頁連結", "→ 連結在主頁"), "sub": end.get("sub")}, n, n,
          footer=footer).save(out / f"{n:02}.jpg", quality=92)
    print(f"{out}: {n} 張", file=sys.stderr)


if __name__ == "__main__":
    main()
