from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DATA_DIR = Path("data")

FALLBACK_ERAS = {
    "eras": [
        {
            "id": "1980s",
            "label": "1980s",
            "display_name": "1980s: Synth-pop",
            "summary": "Bright synths, drum machines, and glossy nostalgia.",
            "genres": [
                {
                    "id": "synth_pop",
                    "label": "Synth-pop",
                    "safe_prompt_style": "bright analog synth chords, electronic drums, pulsing bassline",
                    "bpm_range": [95, 130],
                    "instruments": ["analog synth", "drum machine"],
                    "sonic_traits": ["glossy", "bright"],
                    "avoid": "Do not imitate specific songs or artists.",
                }
            ],
        }
    ]
}

FALLBACK_PERSONAS = {
    "dj_personas": [
        {
            "id": "neon_signal_host",
            "name": "The Neon Signal Host",
            "description": "A fictional cyber-radio host.",
            "voice_direction": "cool, futuristic, precise",
            "intro_template": "Signal detected. We are translating {source_era} {source_genre} through {remix_era} {remix_genre}.",
            "best_for": ["electronic"],
            "avoid": "Do not imitate real people.",
        }
    ]
}

FALLBACK_TEXTURES = {
    "audio_textures": [
        {
            "id": "clean_digital",
            "label": "Clean digital master",
            "description": "Clean, bright audio.",
            "prompt_terms": ["clean digital master", "wide stereo"],
            "post_processing_hint": "Normalize only.",
        }
    ]
}


def load_json(path: str | Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return fallback or {}


def load_music_eras(path: str = "data/music_eras.json") -> dict[str, Any]:
    return load_json(path, FALLBACK_ERAS)


def load_dj_personas(path: str = "data/dj_personas.json") -> dict[str, Any]:
    return load_json(path, FALLBACK_PERSONAS)


def load_audio_textures(path: str = "data/audio_textures.json") -> dict[str, Any]:
    return load_json(path, FALLBACK_TEXTURES)


def load_languages(path: str = "data/languages.json") -> dict[str, Any]:
    return load_json(path, {"languages": []})


def load_lyric_themes(path: str = "data/lyric_themes.json") -> dict[str, Any]:
    return load_json(path, {"themes": []})


def get_era_by_id(eras: list[dict[str, Any]], era_id: str) -> dict[str, Any]:
    return next((era for era in eras if era.get("id") == era_id), eras[0])


def get_genres_for_era(era: dict[str, Any]) -> list[dict[str, Any]]:
    return era.get("genres") or []


def get_genre_by_id(era: dict[str, Any], genre_id: str) -> dict[str, Any]:
    genres = get_genres_for_era(era)
    return next((genre for genre in genres if genre.get("id") == genre_id), genres[0])


def get_persona_by_id(personas: list[dict[str, Any]], persona_id: str) -> dict[str, Any]:
    return next((persona for persona in personas if persona.get("id") == persona_id), personas[0])


def get_texture_by_id(textures: list[dict[str, Any]], texture_id: str) -> dict[str, Any]:
    return next((texture for texture in textures if texture.get("id") == texture_id), textures[-1])


def get_language_by_id(languages: list[dict[str, Any]], language_id: str) -> dict[str, Any]:
    return next((language for language in languages if language.get("id") == language_id), languages[0])


def get_theme_by_id(themes: list[dict[str, Any]], theme_id: str) -> dict[str, Any]:
    return next((theme for theme in themes if theme.get("id") == theme_id), themes[0])


def make_label_id_maps(items: list[dict[str, Any]], label_key: str = "label") -> tuple[dict[str, str], dict[str, str]]:
    label_to_id = {}
    id_to_label = {}
    for item in items:
        item_id = item.get("id", "")
        label = item.get(label_key) or item.get("name") or item_id
        label_to_id[label] = item_id
        id_to_label[item_id] = label
    return label_to_id, id_to_label

