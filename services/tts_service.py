"""
High-Fidelity British English Text-to-Speech (TTS) Service for Umar Tutor Bot.
Generates authentic British English (en-GB) MP3 audio, caches files on disk,
and handles long dialogs, vocabulary words, and conversational responses.
"""
import os
import re
import hashlib
import urllib.parse
import urllib.request
import logging
from pathlib import Path

logger = logging.getLogger("umar_tutor.tts")

CACHE_DIR = Path(__file__).parent.parent / "data" / "tts_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_tts_cache_path(text: str, accent: str = "en-gb") -> Path:
    """Returns unique cached MP3 file path for given text and accent."""
    key = f"{accent}_{text.strip().lower()}".encode("utf-8")
    h = hashlib.sha256(key).hexdigest()[:24]
    return CACHE_DIR / f"{h}.mp3"


def generate_british_tts(text: str, accent: str = "en-gb") -> bytes:
    """
    Returns authentic British English MP3 audio bytes.
    Checks disk cache first; if missing, fetches and caches.
    """
    if not text or not text.strip():
        return b""

    clean_text = text.strip()
    # Strip speaker prefixes like 'Barista: ' or 'Anna: ' for smooth listening narration
    clean_text = re.sub(r"^[A-Za-z]+:\s*", "", clean_text, flags=re.MULTILINE)

    cache_file = get_tts_cache_path(clean_text, accent)
    if cache_file.exists():
        try:
            with open(cache_file, "rb") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Error reading TTS cache: {e}")

    # Break down into manageable sentences / chunks under 150 chars
    lines = [l.strip() for l in clean_text.split("\n") if l.strip()]
    chunks = []
    for line in lines:
        sents = re.split(r"(?<=[.!?])\s+", line)
        for s in sents:
            s = s.strip()
            if s:
                while len(s) > 150:
                    split_idx = s[:150].rfind(",")
                    if split_idx == -1:
                        split_idx = s[:150].rfind(" ")
                    if split_idx == -1:
                        split_idx = 150
                    chunks.append(s[:split_idx].strip())
                    s = s[split_idx:].strip()
                if s:
                    chunks.append(s)

    audio_bytes = bytearray()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for chunk in chunks:
        q = urllib.parse.quote(chunk)
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl={accent}&client=tw-ob&q={q}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                audio_bytes.extend(resp.read())
        except Exception as err:
            logger.error(f"Error downloading TTS chunk '{chunk[:30]}': {err}")

    result_bytes = bytes(audio_bytes)
    if result_bytes:
        try:
            with open(cache_file, "wb") as f:
                f.write(result_bytes)
        except Exception as write_err:
            logger.warning(f"Failed to write TTS cache file: {write_err}")

    return result_bytes
