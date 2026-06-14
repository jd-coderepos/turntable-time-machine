from __future__ import annotations

import html
import random

from .safety import copyright_safety_note


LANG_TEMPLATES = {
    "de": "Erzeuge einen originalen Musikclip. Ausgangspunkt: {source_era} {source_genre}: {source_style}. Verwandle ihn in {remix_era} {remix_genre}: {remix_style}. Stimmung: {mood}. Textur: {texture_terms}. BPM: {bpm}. Dauer: {duration} Sekunden.",
    "fr": "Cree un clip musical original. Point de depart: {source_era} {source_genre}: {source_style}. Transforme-le en {remix_era} {remix_genre}: {remix_style}. Ambiance: {mood}. Texture: {texture_terms}. BPM: {bpm}. Duree: {duration} secondes.",
    "es": "Crea un clip musical original. Punto de partida: {source_era} {source_genre}: {source_style}. Transformalo en {remix_era} {remix_genre}: {remix_style}. Ambiente: {mood}. Textura: {texture_terms}. BPM: {bpm}. Duracion: {duration} segundos.",
}

INTRO_MOOD_LINES = {
    "en": "The mood is {mood}, and the route is entirely original.",
    "de": "Die Stimmung ist {mood}, und diese Route ist vollstaendig original.",
    "fr": "L'ambiance est {mood}, et cette route est entierement originale.",
    "es": "El ambiente es {mood}, y esta ruta es completamente original.",
}

INTRO_TEMPLATES = {
    "de": "Guten Abend, Zeitreisende. Wir schicken {source_era} {source_genre} durch {remix_era} {remix_genre}.",
    "fr": "Bonsoir, voyageurs du temps. Nous envoyons {source_era} {source_genre} vers {remix_era} {remix_genre}.",
    "es": "Buenas noches, viajeros del tiempo. Enviamos {source_era} {source_genre} hacia {remix_era} {remix_genre}.",
}


def choose_bpm(remix_genre, source_genre=None, mood=None, seed=None) -> int:
    rng = random.Random(seed)
    lo, hi = (remix_genre or {}).get("bpm_range") or (source_genre or {}).get("bpm_range") or [90, 125]
    if mood == "relaxed and intimate":
        hi = max(lo, int((lo + hi) / 2))
    elif mood == "energetic and club-ready":
        lo = min(hi, int((lo + hi) / 2))
    return rng.randint(int(lo), int(hi))


def _english_prompt(source_era, source_genre, remix_era, remix_genre, texture, mood, duration, bpm) -> str:
    texture_terms = ", ".join(texture.get("prompt_terms", [])) or texture.get("label", "clean digital master")
    return (
        f"Create an original music clip. Start from a {source_era.get('label')} {source_genre.get('label')} "
        f"musical vocabulary: {source_genre.get('safe_prompt_style')}. Transform it into a {remix_era.get('label')} "
        f"{remix_genre.get('label')} production: {remix_genre.get('safe_prompt_style')}. Mood: {mood}. "
        f"Texture: {texture_terms}. BPM: {bpm}. Duration: {duration} seconds."
    )


def _localized_prompt(language_id, source_era, source_genre, remix_era, remix_genre, texture, mood, duration, bpm) -> tuple[str, str]:
    if language_id == "en":
        return _english_prompt(source_era, source_genre, remix_era, remix_genre, texture, mood, duration, bpm), "English prompt."
    template = LANG_TEMPLATES.get(language_id)
    if not template:
        return _english_prompt(source_era, source_genre, remix_era, remix_genre, texture, mood, duration, bpm), "Selected language template missing; English prompt used."
    return template.format(
        source_era=source_era.get("label"),
        source_genre=source_genre.get("label"),
        source_style=source_genre.get("safe_prompt_style"),
        remix_era=remix_era.get("label"),
        remix_genre=remix_genre.get("label"),
        remix_style=remix_genre.get("safe_prompt_style"),
        texture_terms=", ".join(texture.get("prompt_terms", [])),
        mood=mood,
        bpm=bpm,
        duration=duration,
    ), "Selected-language prompt built from deterministic template."


def build_music_prompt(
    source_era,
    source_genre,
    remix_era,
    remix_genre,
    texture,
    mood,
    duration,
    bpm,
    language_id="en",
    prompt_language_mode="English prompt for best stability",
    vocal_mode="Instrumental only",
    lyrics=None,
) -> str:
    english = _english_prompt(source_era, source_genre, remix_era, remix_genre, texture, mood, duration, bpm)
    localized, _ = _localized_prompt(language_id, source_era, source_genre, remix_era, remix_genre, texture, mood, duration, bpm)
    if prompt_language_mode == "Selected language prompt":
        prompt = localized
    elif prompt_language_mode == "Bilingual prompt" and language_id != "en":
        prompt = f"{english}\n{localized}"
    else:
        prompt = english
    if vocal_mode == "Instrumental only":
        prompt += " No vocals. No lyrics."
    elif vocal_mode == "Wordless vocal texture":
        prompt += " Optional wordless, non-lexical vocal texture only. No recognizable words. No lyrics."
    elif vocal_mode == "Original micro-lyrics":
        prompt += f" Use only the following original micro-lyrics. Do not add extra lyrics.\nLyrics:\n{lyrics or ''}"
    prompt += " Original composition only. No copyrighted melody. Do not imitate any specific song, artist, singer, producer, DJ, hook, riff, sample, lyric, melody, or arrangement."
    return prompt


def build_dj_intro(persona, source_era, source_genre, remix_era, remix_genre, mood, language_id="en") -> dict:
    values = {
        "source_era": source_era.get("label"),
        "source_genre": source_genre.get("label"),
        "remix_era": remix_era.get("label"),
        "remix_genre": remix_genre.get("label"),
    }
    if language_id == "en":
        text = (persona.get("intro_template") or "").format(**values)
        status = "English persona intro template."
    else:
        text = INTRO_TEMPLATES.get(language_id, persona.get("intro_template", "")).format(**values)
        status = "Handcrafted multilingual intro template." if language_id in INTRO_TEMPLATES else "Intro template fallback to English."
    text = f"{text} {INTRO_MOOD_LINES.get(language_id, INTRO_MOOD_LINES['en']).format(mood=mood)}"
    return {"text": text[:420], "status": status}


def build_mixtape_card(
    source_era,
    source_genre,
    remix_era,
    remix_genre,
    persona,
    texture,
    mood,
    bpm,
    language,
    prompt_language_mode,
    vocal_mode,
    lyric_theme,
    lyrics,
    statuses,
    seed,
) -> str:
    route = f"{source_era.get('label')} {source_genre.get('label')} -> {remix_era.get('label')} {remix_genre.get('label')}"
    rows = [
        ("Route", route),
        ("Fictional DJ", persona.get("name")),
        ("Language", language.get("label")),
        ("Prompt mode", prompt_language_mode),
        ("Vocal mode", vocal_mode),
        ("Lyric theme", lyric_theme.get("label") if lyric_theme else "None"),
        ("Texture", texture.get("label")),
        ("Mood", mood),
        ("BPM / Seed", f"{bpm} / {seed}"),
        ("Model stack", "ACE-Step 1.5 music, Kokoro-82M spoken DJ, Tiny Aya text; graceful local fallbacks"),
        ("Status", " | ".join(statuses)),
        ("Safety", copyright_safety_note()),
    ]
    lyric_html = ""
    if lyrics:
        lyric_html = f"<div class='lyrics-chip'>{html.escape(lyrics).replace(chr(10), '<br>')}</div>"
    kv = "".join(f"<div class='ttm-kv'><span>{html.escape(k)}</span><b>{html.escape(str(v))}</b></div>" for k, v in rows)
    return f"""
    <div class="mixtape-card">
      <div class="mixtape-title">Mixtape Card</div>
      <h3>{html.escape(route)}</h3>
      {lyric_html}
      {kv}
    </div>
    """

