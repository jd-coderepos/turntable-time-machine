from __future__ import annotations

from pathlib import Path
import os

import numpy as np

from .audio_utils import save_audio


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
        return {
            "path": None,
            "sample_rate": None,
            "status": f"Spoken DJ intro unavailable; showing text intro only. Kokoro TTS unavailable or unsupported here: {exc}",
            "tts_succeeded": False,
            "model_attempted": True,
            "model_id": "hexgrad/Kokoro-82M",
        }
