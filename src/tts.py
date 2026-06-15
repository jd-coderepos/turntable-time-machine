from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import os

import numpy as np

from .audio_utils import save_audio


MMS_TTS_MODEL_IDS = {
    "en": "facebook/mms-tts-eng",
    "de": "facebook/mms-tts-deu",
    "fr": "facebook/mms-tts-fra",
    "es": "facebook/mms-tts-spa",
}
DEFAULT_TTS_MODEL_ID = MMS_TTS_MODEL_IDS["en"]


@lru_cache(maxsize=4)
def load_tts_pipeline(model_id: str):
    from transformers import pipeline

    token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    return pipeline("text-to-speech", model=model_id, token=token)


def generate_dj_voice(
    text: str,
    language_id: str,
    persona_id: str,
    output_path: str = "outputs/dj_intro.wav",
) -> dict:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    model_id = os.getenv("TTS_MODEL_ID") or MMS_TTS_MODEL_IDS.get(language_id, DEFAULT_TTS_MODEL_ID)
    try:
        if os.getenv("TTM_DISABLE_TTS_MODEL") == "1":
            raise RuntimeError("TTS model disabled by TTM_DISABLE_TTS_MODEL.")

        if os.getenv("TTM_TEST_MODEL_CALLS") == "1":
            sr = 24000
            duration = min(2.0, max(0.4, len(text.split()) * 0.08))
            t = np.arange(int(sr * duration)) / sr
            tone = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 0.7) * 0.12
            save_audio(output_path, tone.astype(np.float32), sr)
            return {
                "path": output_path,
                "sample_rate": sr,
                "status": f"MMS TTS spoken-DJ model call simulated for tests with {model_id}.",
                "tts_succeeded": True,
                "model_attempted": True,
                "model_id": model_id,
            }

        generator = load_tts_pipeline(model_id)
        speech = generator(text[:420])
        audio = np.asarray(speech["audio"], dtype=np.float32).squeeze()
        sample_rate = int(speech["sampling_rate"])
        save_audio(output_path, audio, sample_rate)
        return {
            "path": output_path,
            "sample_rate": sample_rate,
            "status": f"Spoken DJ intro generated with {model_id}.",
            "tts_succeeded": True,
            "model_attempted": True,
            "model_id": model_id,
        }
    except Exception as exc:
        return {
            "path": None,
            "sample_rate": None,
            "status": f"Spoken DJ intro unavailable; showing text intro only. MMS TTS unavailable or unsupported here: {exc}",
            "tts_succeeded": False,
            "model_attempted": True,
            "model_id": model_id,
        }
