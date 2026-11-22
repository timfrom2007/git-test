#!/usr/bin/env python3
"""
把 videos/NN-slug/scenes.json 轉成：
  - narration.txt   旁白稿（純文字，可直接給真人錄音）
  - subtitles.srt   依 TTS 實際長度切的字幕
  - storyboard.md   分鏡表（時間碼、畫面、字卡、旁白）
  - out/video.mp4   1080x1920 直式影片（字卡動畫 + TTS 旁白 + 燒入字幕），--no-video 可略過

用法：
  python3 tools/make_video.py videos/01-tax-free-refund            # 全部產出
  python3 tools/make_video.py videos/01-tax-free-refund --no-video # 只產文字檔與 srt
  python3 tools/make_video.py videos/01-... --bgm music.mp3        # 混入背景音樂（-20 dB）

依賴：ffmpeg、Pillow、sherpa-onnx、soundfile、numpy。
TTS 模型：MeloTTS zh_en（MIT 授權），第一次執行會自動下載到 ~/.cache/short-video-tts/。
"""
import argparse, json, os, re, subprocess, sys, tarfile, urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
GAP = 0.30  # 每個場景之間的停頓（秒）
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
MODEL_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-melo-tts-zh_en.tar.bz2"
CACHE = Path(os.environ.get("TTS_CACHE", Path.home() / ".cache/short-video-tts"))


# ---------------- TTS ----------------
def load_tts():
    import sherpa_onnx
    d = CACHE / "vits-melo-tts-zh_en"
    if not (d / "model.onnx").exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        tgz = CACHE / "melo.tar.bz2"
        print("下載 TTS 模型（約 160MB）…", file=sys.stderr)
        urllib.request.urlretrieve(MODEL_URL, tgz)
        with tarfile.open(tgz) as t:
            t.extractall(CACHE)
        tgz.unlink()
    p = lambda n: str(d / n)
    cfg = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                model=p("model.onnx"), lexicon=p("lexicon.txt"), tokens=p("tokens.txt"), dict_dir=p("dict")),
            num_threads=4),
        rule_fsts=",".join(p(f) for f in ["date.fst", "number.fst", "phone.fst", "new_heteronym.fst"]),
    )
    return sherpa_onnx.OfflineTts(cfg)


# ---------------- 文字處理 ----------------
PUNCT = "。！？；，、：,.!?;:"


def chunk_subs(text, maxlen=15):
    """把旁白切成字幕片段：先依標點切，再把過長的硬切。"""
    parts = [p.strip() for p in re.split(r"[。！？；!?;\n]", text) if p.strip()]
    out = []
    for p in parts:
        cur = ""
        for seg in re.split(r"(?<=[，、：,:])", p):
            seg = seg.strip()
            if not seg:
                continue
            if len(cur) + len(seg) <= maxlen:
                cur += seg
            else:
                if cur:
                    out.append(cur)
                while len(seg) > maxlen:
                    out.append(seg[:maxlen]); seg = seg[maxlen:]
                cur = seg
        if cur:
            out.append(cur)
    return [c.rstrip(PUNCT) for c in out if c.rstrip(PUNCT)]


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def font(size):
    return ImageFont.truetype(FONT, size)


def wrap(draw, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for ch in para:
            if draw.textlength(cur + ch, font=f) <= maxw:
                cur += ch
            else:
                lines.append(cur); cur = ch
        lines.append(cur)
    return lines


# ---------------- 畫面 ----------------
def hex2rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def gradient(c1, c2):
    a = np.linspace(0, 1, H)[:, None, None]
    g = (np.array(c1)[None, None, :] * (1 - a) + np.array(c2)[None, None, :] * a)
    return Image.fromarray(np.repeat(g, W, axis=1).astype(np.uint8), "RGB")


def draw_center(draw, lines, f, y, fill, stroke=0, stroke_fill=(0, 0, 0), spacing=1.25):
    lh = int(f.size * spacing)
    for i, ln in enumerate(lines):
        w = draw.textlength(ln, font=f)
        draw.text(((W - w) / 2, y + i * lh), ln, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return y + len(lines) * lh


def scene_layer(spec, sc, idx, total):
    """透明圖層：品牌標、編號、大字卡、小字。"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    acc = hex2rgb(spec.get("accent", "#FFD54A"))
    brand = spec.get("brand", "")
    if brand:
        f = font(40); tw = d.textlength(brand, font=f)
        d.rounded_rectangle([(W - tw) / 2 - 28, 150, (W + tw) / 2 + 28, 222], 36, fill=(0, 0, 0, 110))
        d.text(((W - tw) / 2, 162), brand, font=f, fill=(255, 255, 255))
    y = 470
    if sc.get("badge"):
        f = font(54); b = sc["badge"]; tw = d.textlength(b, font=f)
        d.rounded_rectangle([(W - tw) / 2 - 34, y, (W + tw) / 2 + 34, y + 92], 46, fill=acc + (255,))
        d.text(((W - tw) / 2, y + 16), b, font=f, fill=(20, 20, 20))
        y += 140
    head = sc.get("text", "")
    if head:
        size = sc.get("size", 108 if len(head.replace("\n", "")) <= 12 else 92)
        f = font(size)
        lines = wrap(d, head, f, W - 140)
        y = draw_center(d, lines, f, y, fill=(255, 255, 255), stroke=6, stroke_fill=(0, 0, 0, 200))
        y += 30
    if sc.get("sub"):
        f = font(52)
        lines = wrap(d, sc["sub"], f, W - 180)
        draw_center(d, lines, f, y, fill=acc, stroke=3, stroke_fill=(0, 0, 0, 200), spacing=1.35)
    return im


def sub_layer(text):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = font(64)
    lines = wrap(d, text, f, W - 160)
    y0 = 1330
    lh = int(64 * 1.3)
    box_h = len(lines) * lh + 40
    d.rounded_rectangle([60, y0 - 20, W - 60, y0 - 20 + box_h], 24, fill=(0, 0, 0, 150))
    draw_center(d, lines, f, y0, fill=(255, 255, 255), stroke=2, stroke_fill=(0, 0, 0))
    return im


# ---------------- 主流程 ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video_dir")
    ap.add_argument("--no-video", action="store_true")
    ap.add_argument("--bgm")
    ap.add_argument("--speed", type=float, default=1.12)
    a = ap.parse_args()

    vd = Path(a.video_dir)
    spec = json.loads((vd / "scenes.json").read_text(encoding="utf-8"))
    scenes = spec["scenes"]

    tts = load_tts()
    import soundfile as sf
    sr = None
    audio, timeline, t = [], [], 0.0
    for i, sc in enumerate(scenes):
        g = tts.generate(sc.get("tts", sc["say"]), sid=0, speed=sc.get("speed", a.speed))
        sr = g.sample_rate
        s = np.array(g.samples, dtype=np.float32)
        # 修剪首尾靜音
        nz = np.where(np.abs(s) > 0.01)[0]
        if len(nz):
            s = s[max(0, nz[0] - int(0.03 * sr)): nz[-1] + int(0.08 * sr)]
        dur = len(s) / sr
        hold = sc.get("hold", 0.0)
        audio += [s, np.zeros(int((GAP + hold) * sr), dtype=np.float32)]
        timeline.append((t, t + dur, t + dur + GAP + hold))
        t += dur + GAP + hold
    total = t

    # 字幕：每個場景的片段按字數比例分配語音長度
    subs = []
    for sc, (st, en, nxt) in zip(scenes, timeline):
        ch = chunk_subs(sc["say"])
        n = sum(len(c) for c in ch)
        cur = st
        for c in ch:
            d = (en - st) * len(c) / n
            subs.append((cur, cur + d, c)); cur += d

    (vd / "narration.txt").write_text(
        f"# {spec['title']}\n# 旁白稿（真人錄音時照念即可；括號內為語氣提示）\n\n" +
        "\n\n".join(f"[{i+1}] {sc['say']}" + (f"（{sc['tone']}）" if sc.get("tone") else "") for i, sc in enumerate(scenes)) + "\n",
        encoding="utf-8")
    (vd / "subtitles.srt").write_text(
        "\n".join(f"{i+1}\n{srt_time(s)} --> {srt_time(e)}\n{txt}\n" for i, (s, e, txt) in enumerate(subs)),
        encoding="utf-8")
    rows = ["| # | 時間 | 畫面（B-roll／素材） | 字卡 | 旁白 |", "|---|---|---|---|---|"]
    for i, (sc, (st, en, nxt)) in enumerate(zip(scenes, timeline)):
        txt = (sc.get("badge", "") + " " + sc.get("text", "").replace("\n", " ") + (" ／ " + sc["sub"].replace("\n", " ") if sc.get("sub") else "")).strip()
        rows.append(f"| {i+1} | {st:0.1f}–{nxt:0.1f}s | {sc.get('visual','')} | {txt} | {sc['say']} |")
    (vd / "storyboard.md").write_text(
        f"# 分鏡：{spec['title']}\n\n總長約 {total:0.1f} 秒（以 TTS 語速計；真人錄音通常 ±15%）。\n"
        "畫面安全區：重要文字放在上方 1/4 到 2/3 之間，避開右側按鈕與底部標題列。\n\n" + "\n".join(rows) + "\n",
        encoding="utf-8")
    print(f"總長 {total:0.1f}s，字幕 {len(subs)} 條", file=sys.stderr)
    if a.no_video:
        return

    out = vd / "out"; out.mkdir(exist_ok=True)
    wav = out / "voice.wav"
    sf.write(wav, np.concatenate(audio), sr)

    c1, c2 = hex2rgb(spec.get("bg1", "#1d2b53")), hex2rgb(spec.get("bg2", "#7e2553"))
    bg = gradient(c1, c2).convert("RGBA")
    # 淡淡的斜線紋理
    tex = Image.new("RGBA", (W, H), (0, 0, 0, 0)); td = ImageDraw.Draw(tex)
    for x in range(-H, W, 60):
        td.line([(x, 0), (x + H, H)], fill=(255, 255, 255, 10), width=14)
    bg = Image.alpha_composite(bg, tex)
    acc = hex2rgb(spec.get("accent", "#FFD54A"))
    layers = [scene_layer(spec, sc, i, len(scenes)) for i, sc in enumerate(scenes)]
    sub_imgs = {}

    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-i", str(wav)] + (["-i", a.bgm] if a.bgm else []) +
        (["-filter_complex", "[2:a]volume=0.1,aloop=loop=-1:size=2e9[b];[1:a][b]amix=inputs=2:duration=first[a]", "-map", "0:v", "-map", "[a]"] if a.bgm else ["-map", "0:v", "-map", "1:a"]) +
        ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
         "-movflags", "+faststart", "-shortest", str(out / "video.mp4")],
        stdin=subprocess.PIPE)

    nframes = int(np.ceil(total * FPS))
    cache_key, cache_bytes = None, None
    for fi in range(nframes):
        tt = fi / FPS
        si = next((i for i, (st, en, nxt) in enumerate(timeline) if tt < nxt), len(scenes) - 1)
        st = timeline[si][0]
        anim = min(1.0, (tt - st) / 0.25)  # 0.25 秒進場動畫
        sub = next((s for s in subs if s[0] <= tt < s[1]), None)
        sub_txt = sub[2] if sub else None
        prog = int(W * tt / total) // 6 * 6
        key = (si, round(anim, 2) if anim < 1 else 1, sub_txt, prog)
        if key != cache_key:
            fr = bg.copy()
            L = layers[si]
            if anim < 1:
                e = 1 - (1 - anim) ** 3
                L2 = L.copy(); L2.putalpha(L.getchannel("A").point(lambda v: int(v * e)))
                frame_l = Image.new("RGBA", (W, H), (0, 0, 0, 0)); frame_l.paste(L2, (0, int((1 - e) * 60)), L2)
                fr = Image.alpha_composite(fr, frame_l)
            else:
                fr = Image.alpha_composite(fr, L)
            if sub_txt:
                if sub_txt not in sub_imgs:
                    sub_imgs[sub_txt] = sub_layer(sub_txt)
                fr = Image.alpha_composite(fr, sub_imgs[sub_txt])
            d = ImageDraw.Draw(fr)
            d.rectangle([0, 0, prog, 12], fill=acc + (255,))
            cache_key, cache_bytes = key, fr.convert("RGB").tobytes()
        ff.stdin.write(cache_bytes)
    ff.stdin.close(); ff.wait()
    # 封面圖（第一個場景的完整畫面）
    cov_l = scene_layer(spec, spec["cover"], 0, 1) if spec.get("cover") else layers[0]
    cov = Image.alpha_composite(bg, cov_l).convert("RGB")
    cov.save(out / "cover.jpg", quality=92)
    print(f"完成：{out/'video.mp4'}", file=sys.stderr)


if __name__ == "__main__":
    main()
