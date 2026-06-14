from __future__ import annotations

from pathlib import Path


def generate_dj_voice(
    text: str,
    language_id: str,
    persona_id: str,
    output_path: str = "outputs/dj_intro.wav",
) -> dict:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    try:
        # Kokoro is optional and lazily imported. This app never clones or imitates
        # voices; the text is only fictional DJ narration.
        import kokoro  # type: ignore  # noqa: F401

        raise RuntimeError("Kokoro wrapper hook is present, but local TTS inference is not configured.")
    except Exception as exc:
        return {
            "path": None,
            "sample_rate": None,
            "status": f"Text-only DJ intro fallback. Kokoro unavailable or unsupported here: {exc}",
            "tts_succeeded": False,
        }

