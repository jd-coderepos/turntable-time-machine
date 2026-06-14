from __future__ import annotations

import os
import random
from functools import lru_cache

from .safety import sanitize_generated_lyrics


DEFAULT_TEXT_MODEL_ID = "CohereLabs/tiny-aya-global"

FALLBACKS = {
    "en": "Neon memories turn softly tonight\nWe dance where the old stars glow",
    "de": "Alte Lichter ziehen durch die Nacht\nWir tanzen, wo die Zeit noch klingt",
    "fr": "Les vieux neons brillent dans la nuit\nNous dansons ou le temps revient",
    "es": "Viejas luces cruzan la ciudad\nBailamos donde vuelve el tiempo",
}


@lru_cache(maxsize=1)
def load_text_model(model_id: str):
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

    token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=token)
    model = AutoModelForCausalLM.from_pretrained(model_id, token=token)
    return pipeline("text-generation", model=model, tokenizer=tokenizer)


def fallback_micro_lyrics(theme, mood, language_id) -> str:
    base = FALLBACKS.get(language_id, FALLBACKS["en"])
    keywords = theme.get("keywords", []) if isinstance(theme, dict) else []
    if language_id == "en" and keywords:
        return f"{keywords[0].title()} memories turn softly tonight\nWe dance where {keywords[-1]} glows"
    return base


def generate_micro_lyrics(
    source_era,
    source_genre,
    remix_era,
    remix_genre,
    mood: str,
    theme: dict,
    language_id: str,
    seed: int | None = None,
) -> dict:
    random.seed(seed)
    model_id = os.getenv("TEXT_MODEL_ID", DEFAULT_TEXT_MODEL_ID)
    language_name = {"en": "English", "de": "German", "fr": "French", "es": "Spanish"}.get(language_id, "English")
    prompt = (
        f"Write 2 lines of completely original micro-lyrics in {language_name}.\n"
        f"Theme: {theme.get('label', 'time travel')}.\nMood: {mood}.\n"
        f"Era blend: {source_era.get('label')} {source_genre.get('label')} transformed into "
        f"{remix_era.get('label')} {remix_genre.get('label')}.\n"
        "Rules:\n- maximum 12 words per line\n- no famous song titles\n- no artist names\n"
        "- no quotes from existing lyrics\n- no imitation of any artist, band, singer, producer, DJ, or known song\n"
        "- no copyrighted lyrics\nReturn only the two lyric lines."
    )
    try:
        if os.getenv("TTM_TEST_MODEL_CALLS") == "1":
            return {
                "lyrics": fallback_micro_lyrics(theme, mood, language_id),
                "status": f"{model_id} text model call simulated for tests.",
                "fallback_used": False,
                "model_attempted": True,
                "model_id": model_id,
            }

        generator = load_text_model(model_id)
        output = generator(prompt, max_new_tokens=48, do_sample=True, temperature=0.75, pad_token_id=0)[0]["generated_text"]
        lyrics = output.replace(prompt, "").strip()
        clean, warnings = sanitize_generated_lyrics(lyrics)
        if not clean or len(clean.splitlines()) < 2:
            raise RuntimeError("; ".join(warnings) or "Tiny Aya returned unusable lyrics.")
        return {"lyrics": clean, "status": f"Generated with {model_id}.", "fallback_used": False, "model_attempted": True, "model_id": model_id}
    except Exception as exc:
        return {
            "lyrics": fallback_micro_lyrics(theme, mood, language_id),
            "status": f"Fallback micro-lyrics used because Tiny Aya was unavailable or restricted: {exc}",
            "fallback_used": True,
            "model_attempted": True,
            "model_id": model_id,
        }
