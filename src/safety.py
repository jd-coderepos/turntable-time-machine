from __future__ import annotations

import re


SAFETY_NOTE = (
    "Turntable Time Machine generates original audio from broad musical-era "
    "descriptors. It does not create covers, reproduce famous songs, clone real "
    "voices, imitate real DJs, or generate copyrighted lyrics or melodies."
)

BLOCKED_PATTERNS = [
    r"\bin the style of\b",
    r"\bsound(?:s)? like\b",
    r"\bclone voice\b",
    r"\bvoice clone\b",
    r"\bimitate\b",
    r"\bremix\s+.+",
    r"\bcover of\b",
    r"\bcopy\b",
    r"\bfamous song\b",
    r"\bcelebrity\b",
    r"\breal dj\b",
]

FORBIDDEN_UI_TERMS = ["Aang", "Avatar", "Airbender", "Air Nomad", "four nations", "bending"]


def copyright_safety_note() -> str:
    return SAFETY_NOTE


def contains_blocked_request(text: str) -> bool:
    lowered = (text or "").lower()
    return any(re.search(pattern, lowered) for pattern in BLOCKED_PATTERNS)


def validate_safe_text(text: str) -> tuple[bool, list[str]]:
    warnings: list[str] = []
    if contains_blocked_request(text):
        warnings.append("Removed unsafe imitation or copyrighted-work request.")
    for term in FORBIDDEN_UI_TERMS:
        if term.lower() in (text or "").lower():
            warnings.append("Removed a forbidden franchise-related term.")
    return not warnings, warnings


def sanitize_mood(mood: str) -> str:
    mood = (mood or "nostalgic and warm").strip()
    if contains_blocked_request(mood):
        return "nostalgic and warm"
    return re.sub(r"[^A-Za-z0-9 ,.'-]", "", mood)[:80] or "nostalgic and warm"


def sanitize_generated_lyrics(lyrics: str) -> tuple[str, list[str]]:
    warnings: list[str] = []
    text = lyrics or ""
    for term in FORBIDDEN_UI_TERMS:
        text = re.sub(re.escape(term), "", text, flags=re.IGNORECASE)
    if contains_blocked_request(text):
        warnings.append("Generated lyrics contained unsafe wording and were replaced.")
        return "", warnings
    lines = [re.sub(r"^[\-\*\d\.\)\s]+", "", line).strip(" \"'") for line in text.splitlines()]
    clean_lines: list[str] = []
    for line in lines:
        line = re.sub(r"[^A-Za-zÀ-ÿ0-9 ,.'!?-]", "", line).strip()
        if not line:
            continue
        words = line.split()
        if len(words) > 12:
            warnings.append("Trimmed a lyric line to 12 words.")
            line = " ".join(words[:12])
        clean_lines.append(line)
        if len(clean_lines) == 2:
            break
    if not clean_lines:
        warnings.append("Generated lyrics were empty after sanitization.")
    return "\n".join(clean_lines), warnings

