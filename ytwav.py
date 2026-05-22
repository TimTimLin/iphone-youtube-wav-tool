#!/usr/bin/env python3
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from yt_dlp import YoutubeDL


OUT_DIR = Path.home() / "Documents" / "YouTube WAV"


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: ytwav "https://www.youtube.com/watch?v=..."', file=sys.stderr)
        return 64

    url = sys.argv[1].strip()
    if not is_youtube_url(url):
        print("Only single YouTube video URLs are supported.", file=sys.stderr)
        return 64

    require_tool("ffmpeg")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    work_dir = OUT_DIR / ".work"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    try:
        info = probe(url)
        title = info.get("title") or "youtube_audio"
        bpm, key = parse_metadata(info)
        suffix = build_suffix(bpm, key)
        output_name = unique_name(OUT_DIR, sanitize_filename(f"{title}{suffix}") + ".wav")

        print(f"Title: {title}")
        print(f"BPM: {bpm or 'unknown'}")
        print(f"Key: {key or 'unknown'}")
        print("Downloading audio...")

        input_path = download_audio(url, work_dir)
        temp_wav = work_dir / "output.wav"

        print("Converting to WAV...")
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(input_path),
                "-vn",
                "-acodec",
                "pcm_s16le",
                "-ar",
                "44100",
                "-ac",
                "2",
                str(temp_wav),
            ],
            check=True,
        )

        shutil.move(str(temp_wav), str(output_name))
        print("")
        print(f"Saved: {output_name}")
        return 0
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def is_youtube_url(url: str) -> bool:
    return re.match(r"^https?://(www\.|m\.|music\.)?(youtube\.com|youtu\.be)/", url) is not None


def require_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"Missing required tool: {name}")


def probe(url: str) -> dict:
    with YoutubeDL({"quiet": True, "no_playlist": True}) as ydl:
        return ydl.extract_info(url, download=False)


def download_audio(url: str, work_dir: Path) -> Path:
    outtmpl = str(work_dir / "input.%(ext)s")
    with YoutubeDL({"format": "bestaudio", "outtmpl": outtmpl, "quiet": False, "no_playlist": True}) as ydl:
        ydl.download([url])
    candidates = [p for p in work_dir.iterdir() if p.name.startswith("input.")]
    if not candidates:
        raise RuntimeError("Downloaded audio file not found.")
    return candidates[0]


def parse_metadata(info: dict) -> tuple[str | None, str | None]:
    text = "\n".join(str(info.get(k) or "") for k in ("title", "description", "track", "alt_title"))
    bpm = None
    bpm_match = re.search(r"\b([5-9]\d|1\d{2}|2[0-4]\d|250)\s*(?:bpm|beats?\s*per\s*minute)\b", text, re.I)
    if bpm_match:
        bpm = bpm_match.group(1)

    key = None
    key_match = re.search(
        r"\b([A-G])\s*(#|♯|sharp|-sharp|b|♭|flat|-flat)?\s*[-_/ ]?\s*(major|minor|maj|min)\b",
        text,
        re.I,
    )
    if key_match:
        root = key_match.group(1).upper()
        accidental_raw = (key_match.group(2) or "").lower()
        accidental = ""
        if accidental_raw in ("#", "♯", "sharp", "-sharp"):
            accidental = "#"
        elif accidental_raw in ("b", "♭", "flat", "-flat"):
            accidental = "b"
        mode_raw = key_match.group(3).lower()
        mode = "major" if mode_raw in ("major", "maj") else "minor"
        key = f"{root}{accidental} {mode}"

    return bpm, key


def build_suffix(bpm: str | None, key: str | None) -> str:
    parts = []
    if bpm:
        parts.append(f"{bpm} BPM")
    if key:
        parts.append(key)
    return "" if not parts else " - " + " - ".join(parts)


def sanitize_filename(value: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", value)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:120].strip() or "youtube_audio"


def unique_name(directory: Path, filename: str) -> Path:
    path = directory / filename
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    index = 1
    while True:
        candidate = directory / f"{stem} ({index}){suffix}"
        if not candidate.exists():
            return candidate
        index += 1


if __name__ == "__main__":
    raise SystemExit(main())
