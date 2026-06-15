from __future__ import annotations

from pathlib import Path
import hashlib
import os

import numpy as np

from .audio_utils import save_audio


def generate_fallback_dj_signal(text: str, output_path: str) -> dict:
    sr = 24000
    words = max(4, min(28, len((text or "").split())))
    duration = min(4.0, max(1.0, words * 0.16))
    total = int(sr * duration)
    t = np.arange(total) / sr
    digest = hashlib.sha256((text or "timeline radio").encode("utf-8")).digest()
    base = 150 + digest[0]
    carrier = np.sin(2 * np.pi * base * t) * 0.045
    radio = np.sin(2 * np.pi * (base * 1.5) * t) * 0.025
    envelope = 0.6 + 0.4 * np.sin(2 * np.pi * (2.2 + digest[1] / 128) * t)
    audio = (carrier + radio) * envelope
    for index in range(words):
        start = int((index / words) * total)
        stop = min(total, start + int(sr * 0.055))
        if stop > start:
            audio[start:stop] += np.sin(2 * np.pi * (base + 120 + (index % 5) * 38) * t[: stop - start]) * 0.055
    save_audio(output_path, audio.astype(np.float32), sr)
    return {
        "path": output_path,
        "sample_rate": sr,
        "tts_succeeded": False,
        "fallback_audio": True,
    }


def generate_dj_voice(
    text: str,
    language_id: str,
    persona_id: str,
    output_path: str = "outputs/dj_intro.wav",
) -> dict:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    try:
        if os.getenv("TTM_TEST_MODEL_CALLS") == "1":
            sr = 24000
            duration = min(2.0, max(0.4, len(text.split()) * 0.08))
            t = np.arange(int(sr * duration)) / sr
            tone = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 0.7) * 0.12
            save_audio(output_path, tone.astype(np.float32), sr)
            return {
                "path": output_path,
                "sample_rate": sr,
                "status": "Kokoro spoken-DJ model call simulated for tests.",
                "tts_succeeded": True,
                "model_attempted": True,
                "model_id": "hexgrad/Kokoro-82M",
            }

        # Kokoro is optional and lazily imported. This app never clones or imitates
        # voices; the text is only fictional DJ narration.
        import kokoro  # type: ignore  # noqa: F401

        raise RuntimeError("Kokoro wrapper hook is present, but local TTS inference is not configured.")
    except Exception as exc:
        fallback = generate_fallback_dj_signal(text, output_path)
        return {
            "path": fallback["path"],
            "sample_rate": fallback["sample_rate"],
            "status": f"Fallback DJ radio-signal intro audio generated. Kokoro spoken TTS unavailable or unsupported here: {exc}",
            "tts_succeeded": False,
            "fallback_audio": True,
            "model_attempted": True,
            "model_id": "hexgrad/Kokoro-82M",
        }
