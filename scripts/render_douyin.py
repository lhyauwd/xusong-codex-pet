from __future__ import annotations

import argparse
import math
import os
import subprocess
import sys
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
import imageio_ffmpeg


WIDTH = 1080
HEIGHT = 1920
FPS = 30
BG = (244, 244, 239)
INK = (24, 24, 22)
PURPLE = (128, 78, 184)
YELLOW = (244, 205, 76)
MUTED = (103, 103, 98)

STATES = [
    ("idle", "抱着格洛米", 1.30),
    ("waving", "挥手等你", 1.25),
    ("running", "埋头写歌", 1.45),
    ("review", "紫麦唱歌", 1.35),
    ("running-right", "唱着向右", 1.20),
    ("running-left", "唱着向左", 1.20),
    ("waiting", "等待回应", 1.20),
    ("jumping", "借你", 1.35),
    ("failed", "灵感掉线", 1.30),
]


def find_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    windows = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    candidates = [
        windows / ("msyhbd.ttc" if bold else "msyh.ttc"),
        windows / ("simhei.ttf" if bold else "simsun.ttc"),
        windows / "arialbd.ttf",
        windows / "arial.ttf",
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


FONT_HOOK = find_font(84, True)
FONT_TITLE = find_font(68, True)
FONT_LABEL = find_font(42, True)
FONT_SMALL = find_font(28)
FONT_TINY = find_font(22, True)


def ease_out_cubic(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return 1 - (1 - value) ** 3


def load_gifs(preview_dir: Path) -> dict[str, list[Image.Image]]:
    result: dict[str, list[Image.Image]] = {}
    for state, _, _ in STATES:
        path = preview_dir / f"{state}.gif"
        if not path.exists():
            raise FileNotFoundError(f"Missing preview: {path}")
        gif = Image.open(path)
        frames = []
        for index in range(getattr(gif, "n_frames", 1)):
            gif.seek(index)
            frames.append(gif.convert("RGBA"))
        result[state] = frames
    return result


def fit_sprite(sprite: Image.Image, max_width: int = 690, max_height: int = 820) -> Image.Image:
    box = sprite.getbbox()
    if box:
        sprite = sprite.crop(box)
    sprite = ImageOps.contain(sprite, (max_width, max_height), Image.Resampling.LANCZOS)
    return sprite


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill, radius=18, outline=None, width=0):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_progress(draw: ImageDraw.ImageDraw, active: int):
    start_x = 82
    y = 1730
    for index in range(len(STATES)):
        x = start_x + index * 79
        color = PURPLE if index == active else (205, 205, 198)
        radius = 12 if index == active else 8
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def render_frame(
    gifs: dict[str, list[Image.Image]],
    timeline_time: float,
    total_duration: float,
) -> Image.Image:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(canvas)

    draw.rectangle((0, 0, WIDTH, 22), fill=PURPLE)
    draw.text((72, 58), "XUSONG / CODEX PET", font=FONT_TINY, fill=MUTED)

    hook_duration = 1.55
    outro_duration = 2.15
    body_start = hook_duration
    body_end = total_duration - outro_duration

    if timeline_time < hook_duration:
        local = timeline_time / hook_duration
        draw.text((70, 170), "如果许嵩", font=FONT_HOOK, fill=INK)
        draw.text((70, 275), "住进 Codex", font=FONT_HOOK, fill=PURPLE)
        rounded(draw, (70, 405, 516, 470), YELLOW, radius=10)
        draw.text((94, 419), "9 个动作，一次看完", font=FONT_SMALL, fill=INK)

        frames = gifs["idle"]
        sprite = fit_sprite(frames[int(timeline_time * 7) % len(frames)], 720, 850)
        scale = 0.88 + 0.12 * ease_out_cubic(min(1.0, local * 2.2))
        sprite = sprite.resize((int(sprite.width * scale), int(sprite.height * scale)), Image.Resampling.LANCZOS)
        canvas.paste(sprite, ((WIDTH - sprite.width) // 2, 700), sprite)
        draw.text((72, 1630), "xusong", font=FONT_TITLE, fill=INK)
        return canvas

    if timeline_time >= body_end:
        local = (timeline_time - body_end) / outro_duration
        frames = gifs["jumping"]
        sprite = fit_sprite(frames[int(local * 10) % len(frames)], 750, 880)
        bob = int(18 * math.sin(local * math.pi * 2))
        canvas.paste(sprite, ((WIDTH - sprite.width) // 2 - 30, 590 + bob), sprite)
        draw.text((70, 215), "你最喜欢", font=FONT_TITLE, fill=INK)
        draw.text((70, 300), "哪个动作？", font=FONT_TITLE, fill=PURPLE)
        draw.text((72, 1660), "评论区告诉我", font=FONT_SMALL, fill=MUTED)
        return canvas

    body_time = timeline_time - body_start
    elapsed = 0.0
    active = 0
    state = STATES[0]
    local = 0.0
    for index, item in enumerate(STATES):
        if body_time < elapsed + item[2]:
            active = index
            state = item
            local = (body_time - elapsed) / item[2]
            break
        elapsed += item[2]

    state_id, state_label, _ = state
    frames = gifs[state_id]
    sprite = fit_sprite(frames[int(local * len(frames) * 1.65) % len(frames)])
    entrance = ease_out_cubic(min(1.0, local * 5.5))
    x = int(170 + (1 - entrance) * 90)
    y = 555 + int(12 * math.sin(local * math.pi * 2))

    draw.text((70, 175), f"{active + 1:02d}", font=FONT_TITLE, fill=PURPLE)
    draw.text((70, 270), state_label, font=FONT_HOOK, fill=INK)
    rounded(draw, (70, 405, 70 + max(250, 25 * len(state_id)), 458), INK, radius=9)
    draw.text((92, 415), state_id.upper(), font=FONT_TINY, fill=(255, 255, 255))
    canvas.paste(sprite, (x, y), sprite)

    draw_progress(draw, active)
    draw.text((72, 1790), "xusong 的全部动作", font=FONT_SMALL, fill=MUTED)
    return canvas


def write_original_audio(path: Path, duration: float):
    sample_rate = 44100
    total = int(duration * sample_rate)
    chords = [
        (261.63, 329.63, 392.00),
        (220.00, 261.63, 329.63),
        (174.61, 220.00, 261.63),
        (196.00, 246.94, 293.66),
    ]
    melody = [523.25, 659.25, 783.99, 659.25, 587.33, 659.25, 523.25, 493.88]
    bpm = 96
    beat = 60 / bpm
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        chunk = bytearray()
        for index in range(total):
            t = index / sample_rate
            chord = chords[int(t / (beat * 4)) % len(chords)]
            note = melody[int(t / beat) % len(melody)]
            env = min(1.0, t / 0.5, max(0.0, (duration - t) / 0.8))
            pulse = (t % beat) / beat
            pluck = math.exp(-4.2 * pulse)
            value = sum(math.sin(2 * math.pi * f * t) for f in chord) * 0.055
            value += math.sin(2 * math.pi * note * t) * 0.075 * pluck
            value += math.sin(2 * math.pi * 98.0 * t) * 0.025 * (1 if pulse < 0.12 else 0)
            sample = int(max(-1, min(1, value * env)) * 32767)
            chunk.extend(sample.to_bytes(2, "little", signed=True) * 2)
            if len(chunk) >= 65536:
                wav.writeframesraw(chunk)
                chunk.clear()
        if chunk:
            wav.writeframesraw(chunk)


def run(args: argparse.Namespace):
    preview_dir = Path(args.preview_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    gifs = load_gifs(preview_dir)

    duration = 1.55 + sum(item[2] for item in STATES) + 2.15
    silent_path = output_dir / "xusong-actions-douyin-silent.mp4"
    preview_path = output_dir / "xusong-actions-douyin-preview.mp4"
    audio_path = output_dir / "original-preview-track.wav"
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    command = [
        ffmpeg, "-y", "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-", "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(silent_path),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin is not None
    try:
        for frame_index in range(math.ceil(duration * FPS)):
            frame = render_frame(gifs, frame_index / FPS, duration)
            process.stdin.write(frame.tobytes())
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError("FFmpeg video render failed")

    write_original_audio(audio_path, duration)
    mux = [
        ffmpeg, "-y", "-i", str(silent_path), "-i", str(audio_path),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
        "-movflags", "+faststart", str(preview_path),
    ]
    subprocess.run(mux, check=True)
    audio_path.unlink(missing_ok=True)
    print(f"silent={silent_path}")
    print(f"preview={preview_path}")
    print(f"duration={duration:.2f}s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    run(parser.parse_args())


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit("FFmpeg closed the video pipe early")
