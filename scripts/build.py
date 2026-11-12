#!/usr/bin/env python3
"""Render video vertikal 1080x1920 dari voiceover.mp3 + naskah.json.

Teks ditampilkan per segmen. Durasi tiap segmen dihitung otomatis
berdasarkan jumlah kata, lalu disesuaikan dengan panjang voiceover.
"""
import json
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO = os.path.join(ROOT, "voiceover.mp3")
SCRIPT = os.path.join(ROOT, "naskah.json")
OUT_DIR = os.path.join(ROOT, "output")
OUT = os.path.join(OUT_DIR, "video.mp4")

FONT_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]
FONT_REG = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "C:/Windows/Fonts/arial.ttf",
]

GOLD = (255, 205, 90)
CYAN = (120, 220, 255)
WHITE = (255, 255, 255)


def load_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(out.strip())


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def build_timeline(segments, total):
    start, end = 0.6, total - 0.8
    gap = 0.25
    weights = [max(1, len(s["text"].split())) for s in segments]
    usable = (end - start) - gap * (len(segments) - 1)
    total_w = sum(weights)
    t, timeline = start, []
    for s, w in zip(segments, weights):
        d = usable * w / total_w
        timeline.append((t, t + d, s))
        t += d + gap
    return timeline


def make_background():
    mask = Image.linear_gradient("L").resize((W, H))
    top = Image.new("RGB", (W, H), (12, 14, 38))
    bottom = Image.new("RGB", (W, H), (46, 12, 62))
    return Image.composite(bottom, top, mask)


def make_glow(size=900):
    radial = Image.radial_gradient("L").resize((size, size))
    alpha = radial.point(lambda v: int(120 * max(0.0, 1 - v / 190) ** 2))
    glow = Image.new("RGBA", (size, size), (255, 120, 60, 0))
    glow.putalpha(alpha)
    return glow


def render_frame(t, total, base, glow, timeline, fonts, cfg):
    f_title, f_label, f_body, f_small = fonts
    frame = base.copy()

    # Cahaya bergerak perlahan di latar
    gx = int(W / 2 + 260 * math.sin(t * 0.6) - glow.width / 2)
    gy = int(H * 0.35 + 180 * math.cos(t * 0.4) - glow.height / 2)
    frame.paste(glow, (gx, gy), glow)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    d.text((W / 2, 170), cfg.get("title", ""), font=f_title,
           fill=GOLD + (255,), anchor="ma")

    active = None
    for idx, (a, b, s) in enumerate(timeline):
        if a <= t <= b:
            active = (idx, a, b, s)
            break

    if active:
        idx, a, b, s = active
        alpha = int(255 * min(1.0, (t - a) / 0.3, (b - t) / 0.2))
        lines = wrap(d, s["text"], f_body, W - 160)
        line_h = int(f_body.size * 1.3)
        block_h = len(lines) * line_h
        y = H * 0.46 - block_h / 2
        d.text((W / 2, y - 90), f"{idx + 1:02d}  {s['label'].upper()}",
               font=f_label, fill=CYAN + (alpha,), anchor="ma")
        for line in lines:
            d.text((W / 2, y), line, font=f_body,
                   fill=WHITE + (alpha,), anchor="ma")
            y += line_h

    # Progress bar
    bar_y = H - 170
    d.rectangle([80, bar_y, W - 80, bar_y + 14], fill=(255, 255, 255, 50))
    progress = min(1.0, t / total)
    d.rectangle([80, bar_y, 80 + (W - 160) * progress, bar_y + 14],
                fill=GOLD + (255,))
    d.text((W / 2, H - 110), cfg.get("brand", ""), font=f_small,
           fill=(255, 255, 255, 170), anchor="ma")

    return Image.alpha_composite(frame.convert("RGBA"), overlay).convert("RGB")


def main():
    if not os.path.exists(AUDIO):
        sys.exit("voiceover.mp3 tidak ditemukan di root project.")

    with open(SCRIPT, encoding="utf-8") as f:
        cfg = json.load(f)

    total = probe_duration(AUDIO)
    timeline = build_timeline(cfg["segments"], total)
    os.makedirs(OUT_DIR, exist_ok=True)

    fonts = (
        load_font(FONT_BOLD, 60),   # judul
        load_font(FONT_BOLD, 36),   # label segmen
        load_font(FONT_BOLD, 58),   # isi teks
        load_font(FONT_REG, 34),    # brand
    )
    base = make_background()
    glow = make_glow()

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-",
        "-i", AUDIO,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        OUT,
    ]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    n = math.ceil(total * FPS)
    for i in range(n):
        frame = render_frame(i / FPS, total, base, glow, timeline, fonts, cfg)
        ff.stdin.write(frame.tobytes())
        if i % 300 == 0:
            print(f"frame {i}/{n}", flush=True)

    ff.stdin.close()
    if ff.wait() != 0:
        sys.exit("ffmpeg gagal merender video.")
    print(f"Selesai: {OUT} ({n} frame, durasi {total:.2f} detik, {W}x{H})")


if __name__ == "__main__":
    main()
