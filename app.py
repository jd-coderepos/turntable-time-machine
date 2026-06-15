from __future__ import annotations

import random
import uuid
import html
from pathlib import Path

import gradio as gr

try:
    import spaces
except Exception:  # pragma: no cover - local/CPU fallback when ZeroGPU is absent
    class _SpacesFallback:
        def GPU(self, *args, **kwargs):
            if args and callable(args[0]) and len(args) == 1 and not kwargs:
                return args[0]

            def decorator(fn):
                return fn

            return decorator

    spaces = _SpacesFallback()

from src.audio_effects import apply_texture
from src.audio_utils import add_silence, concatenate_audio, load_audio, resample_if_needed, save_audio
from src.data_loader import (
    get_era_by_id,
    get_genre_by_id,
    get_language_by_id,
    get_persona_by_id,
    get_texture_by_id,
    get_theme_by_id,
    load_audio_textures,
    load_dj_personas,
    load_languages,
    load_lyric_themes,
    load_music_eras,
    make_label_id_maps,
)
from src.lyrics_generator import generate_micro_lyrics
from src.music_generator import generate_music
from src.prompt_builder import build_dj_intro, build_mixtape_card, build_music_prompt, choose_bpm
from src.safety import copyright_safety_note, sanitize_mood
from src.tts import generate_dj_voice


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

MUSIC_DATA = load_music_eras()
PERSONA_DATA = load_dj_personas()
TEXTURE_DATA = load_audio_textures()
LANGUAGE_DATA = load_languages()
THEME_DATA = load_lyric_themes()

ERAS = MUSIC_DATA.get("eras", [])
PERSONAS = PERSONA_DATA.get("dj_personas", [])
TEXTURES = TEXTURE_DATA.get("audio_textures", [])
LANGUAGES = LANGUAGE_DATA.get("languages", [])
THEMES = THEME_DATA.get("themes", [])

ERA_LABEL_TO_ID, ERA_ID_TO_LABEL = make_label_id_maps(ERAS)
PERSONA_LABEL_TO_ID, _ = make_label_id_maps(PERSONAS, "name")
TEXTURE_LABEL_TO_ID, _ = make_label_id_maps(TEXTURES)
LANGUAGE_LABEL_TO_ID, _ = make_label_id_maps(LANGUAGES)
THEME_LABEL_TO_ID, _ = make_label_id_maps(THEMES)

MOODS = [
    "nostalgic and warm",
    "danceable and bright",
    "late-night and smoky",
    "dreamy and cinematic",
    "energetic and club-ready",
    "futuristic and strange",
    "relaxed and intimate",
]
PROMPT_MODES = ["Best stability (English)", "Broadcast language", "English + broadcast language"]
VOCAL_MODES = ["Instrumental only", "Wordless vocal texture", "Original micro-lyrics"]
DURATIONS = [10, 15, 20]


def genre_choices_for_era_label(era_label: str) -> list[str]:
    era = get_era_by_id(ERAS, ERA_LABEL_TO_ID.get(era_label, ERAS[0]["id"]))
    return [genre.get("label", genre.get("id")) for genre in era.get("genres", [])]


def genre_label_to_id(era: dict, label: str) -> str:
    for genre in era.get("genres", []):
        if genre.get("label") == label:
            return genre.get("id")
    return era.get("genres", [{}])[0].get("id", "")


def update_source_genres(source_era_label: str):
    choices = genre_choices_for_era_label(source_era_label)
    return gr.update(choices=choices, value=choices[0])


def update_remix_genres(remix_era_label: str):
    choices = genre_choices_for_era_label(remix_era_label)
    return gr.update(choices=choices, value=choices[0])


def update_lyric_theme_visibility(vocal_mode: str):
    return gr.update(visible=vocal_mode == "Original micro-lyrics")


def timeline_route_html(source_era_label: str, source_genre_label: str, remix_era_label: str, remix_genre_label: str) -> str:
    source_era = get_era_by_id(ERAS, ERA_LABEL_TO_ID.get(source_era_label, ERAS[0]["id"]))
    remix_era = get_era_by_id(ERAS, ERA_LABEL_TO_ID.get(remix_era_label, ERAS[0]["id"]))
    src_summary = source_era.get("summary", "")[:140]
    remix_summary = remix_era.get("summary", "")[:140]
    return f"""
    <div class="path">
      <div class="era-card"><small>source</small><h3>{source_era_label}</h3><p>{source_genre_label}<br>{src_summary}</p></div>
      <div class="swirl">-></div>
      <div class="era-card"><small>remix</small><h3>{remix_era_label}</h3><p>{remix_genre_label}<br>{remix_summary}</p></div>
    </div>
    <div class="wind-wave"></div>
    """


def surprise_me():
    rng = random.Random()
    source_era = rng.choice(ERAS)
    remix_era = rng.choice(ERAS)
    if len(ERAS) > 1 and rng.random() > 0.18:
        while remix_era["id"] == source_era["id"]:
            remix_era = rng.choice(ERAS)
    source_genre = rng.choice(source_era.get("genres", []))
    remix_genre = rng.choice(remix_era.get("genres", []))
    persona = rng.choice(PERSONAS)
    texture = rng.choice(TEXTURES)
    language = rng.choice(LANGUAGES)
    vocal_mode = rng.choice(VOCAL_MODES)
    theme = rng.choice(THEMES)
    duration = rng.choice(DURATIONS)
    route = timeline_route_html(source_era["label"], source_genre["label"], remix_era["label"], remix_genre["label"])
    return (
        source_era["label"],
        gr.update(choices=genre_choices_for_era_label(source_era["label"]), value=source_genre["label"]),
        remix_era["label"],
        gr.update(choices=genre_choices_for_era_label(remix_era["label"]), value=remix_genre["label"]),
        persona["name"],
        texture["label"],
        rng.choice(MOODS),
        language["label"],
        rng.choice(PROMPT_MODES),
        vocal_mode,
        gr.update(value=theme["label"], visible=vocal_mode == "Original micro-lyrics"),
        duration,
        int(rng.randint(1, 999999)),
        True,
        route,
    )


@spaces.GPU(duration=120)
def generate_time_machine_mix(
    source_era_label,
    source_genre_label,
    remix_era_label,
    remix_genre_label,
    dj_persona_label,
    audio_texture_label,
    mood,
    broadcast_language_label,
    prompt_language_mode,
    vocal_mode,
    lyric_theme_label,
    duration,
    seed,
    random_seed,
):
    run_id = uuid.uuid4().hex[:10]
    actual_seed = random.randint(1, 999999) if random_seed or seed in (None, "") else int(seed)
    mood = sanitize_mood(mood)

    source_era = get_era_by_id(ERAS, ERA_LABEL_TO_ID.get(source_era_label, ERAS[0]["id"]))
    remix_era = get_era_by_id(ERAS, ERA_LABEL_TO_ID.get(remix_era_label, ERAS[0]["id"]))
    source_genre = get_genre_by_id(source_era, genre_label_to_id(source_era, source_genre_label))
    remix_genre = get_genre_by_id(remix_era, genre_label_to_id(remix_era, remix_genre_label))
    persona = get_persona_by_id(PERSONAS, PERSONA_LABEL_TO_ID.get(dj_persona_label, PERSONAS[0]["id"]))
    texture = get_texture_by_id(TEXTURES, TEXTURE_LABEL_TO_ID.get(audio_texture_label, "clean_digital"))
    language = get_language_by_id(LANGUAGES, LANGUAGE_LABEL_TO_ID.get(broadcast_language_label, LANGUAGES[0]["id"]))
    lyric_theme = get_theme_by_id(THEMES, THEME_LABEL_TO_ID.get(lyric_theme_label, THEMES[0]["id"]))

    bpm = choose_bpm(remix_genre, source_genre, mood, actual_seed)
    intro = build_dj_intro(persona, source_era, source_genre, remix_era, remix_genre, mood, language["id"])

    lyric_status = "Lyrics disabled."
    lyrics = ""
    if vocal_mode == "Original micro-lyrics":
        lyric_result = generate_micro_lyrics(
            source_era, source_genre, remix_era, remix_genre, mood, lyric_theme, language["id"], actual_seed
        )
        lyrics = lyric_result["lyrics"]
        lyric_status = lyric_result["status"]

    music_prompt = build_music_prompt(
        source_era,
        source_genre,
        remix_era,
        remix_genre,
        texture,
        mood,
        int(duration),
        bpm,
        language["id"],
        prompt_language_mode,
        vocal_mode,
        lyrics,
    )

    intro_path = str(OUTPUT_DIR / f"dj_intro_{run_id}.wav")
    music_raw_path = str(OUTPUT_DIR / f"music_raw_{run_id}.wav")
    music_processed_path = str(OUTPUT_DIR / f"music_processed_{run_id}.wav")
    final_path = str(OUTPUT_DIR / f"final_mix_{run_id}.wav")

    tts_result = generate_dj_voice(intro["text"], language["id"], persona["id"], intro_path)
    music_result = generate_music(
        music_prompt,
        int(duration),
        bpm,
        lyrics=lyrics or None,
        vocal_mode=vocal_mode,
        language_id=language["id"],
        seed=actual_seed,
        output_path=music_raw_path,
    )

    music_audio, music_sr = load_audio(music_result["path"])
    processed_music = apply_texture(music_audio, music_sr, texture["id"])
    save_audio(music_processed_path, processed_music, music_sr)

    final_parts = []
    intro_audio_path = None
    if tts_result.get("path"):
        intro_audio, intro_sr = load_audio(tts_result["path"])
        intro_audio = resample_if_needed(intro_audio, intro_sr, music_sr)
        final_parts.extend([intro_audio, add_silence(0.4, music_sr)])
        intro_audio_path = tts_result["path"]
    final_parts.append(processed_music)
    save_audio(final_path, concatenate_audio(final_parts, music_sr), music_sr)

    statuses = [intro["status"], lyric_status, tts_result["status"], music_result["status"]]
    mixtape = build_mixtape_card(
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
        lyric_theme if vocal_mode == "Original micro-lyrics" else None,
        lyrics,
        statuses,
        actual_seed,
    )
    status_md = "\n".join([f"- {status}" for status in statuses])
    intro_audio_status = (
        "Spoken DJ intro generated."
        if tts_result.get("tts_succeeded")
        else "Spoken DJ intro is unavailable in this runtime; use the fictional DJ intro text shown in the timeline card."
    )
    route = timeline_route_html(source_era_label, source_genre_label, remix_era_label, remix_genre_label)
    intro_text = html.escape(intro["text"])
    lyrics_html = html.escape(lyrics or "Instrumental / no lyric text requested.").replace(chr(10), "<br>")
    journey = f"""
    {route}
    <div class="micro"><h3>Fictional DJ intro</h3><p>{intro_text}</p></div>
    <div class="micro lyric-box"><h3>Generated micro-lyrics</h3><p>{lyrics_html}</p></div>
    """
    return (
        final_path,
        music_processed_path,
        intro_audio_path,
        intro_audio_status,
        intro["text"],
        lyrics or "Instrumental / no lyric text requested.",
        music_prompt,
        mixtape,
        status_md,
        copyright_safety_note(),
        route,
        journey,
    )


CSS = """
:root{--sky:#dff9ff;--cream:#fff4d2;--sand:#f2c879;--ink:#26324a;--teal:#1db8c5;--orange:#f26a38;--deep:#172135;--purple:#6e54ff;--leaf:#78d69a;--line:rgba(38,50,74,.16)}
.gradio-container{font-family:ui-rounded,Inter,system-ui,sans-serif!important;color:var(--ink);background:radial-gradient(circle at 12% 8%,#fff 0 6rem,transparent 6.4rem),radial-gradient(circle at 95% 18%,rgba(29,184,197,.2),transparent 20rem),linear-gradient(180deg,#e7fbff 0%,#fff8df 48%,#f3d79a 100%)!important}
#app-shell{max-width:1340px;margin:0 auto}
.banner{background:rgba(255,255,255,.62);border:1px solid rgba(255,255,255,.9);border-radius:36px;padding:28px;box-shadow:0 30px 90px rgba(77,79,110,.17);overflow:hidden}
.tag{display:inline-flex;font-weight:900;color:var(--orange);text-transform:uppercase;letter-spacing:.12em;font-size:12px}
.hero-title{font-size:clamp(38px,6vw,76px);line-height:.94;margin:10px 0;letter-spacing:0;font-weight:1000}.hero-title em{font-style:normal;color:var(--teal)}
.sub{max-width:760px;font-size:19px;line-height:1.5;color:#44516b}.safety-pill{display:inline-flex;margin-top:12px;padding:9px 13px;border-radius:999px;background:#fff4d2;color:#26324a;font-weight:800}
.wind-mascot{min-height:292px;border-radius:36px;background:linear-gradient(135deg,rgba(23,33,53,.94),rgba(32,58,83,.9));padding:22px;position:relative;overflow:hidden;color:white;box-shadow:0 30px 90px rgba(23,33,53,.28)}
.wind-mascot:before{content:"";position:absolute;inset:-40%;background:conic-gradient(from 120deg,transparent,rgba(223,249,255,.55),transparent 35%,rgba(242,106,56,.3),transparent 65%);animation:spin 14s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}
.orb{position:absolute;inset:22px;border:2px solid rgba(255,255,255,.25);border-radius:28px;z-index:1}.avatar{position:absolute;left:50%;top:48%;transform:translate(-50%,-52%);width:145px;height:145px;border-radius:50%;background:radial-gradient(circle at 50% 52%,#ffe0a5 0 31%,#f26a38 32% 47%,#fff4d2 48% 52%,#1db8c5 53% 100%);z-index:2;box-shadow:0 0 0 12px rgba(255,255,255,.1),0 20px 50px rgba(0,0,0,.25)}
.avatar:before{content:"";position:absolute;width:70px;height:70px;border-radius:48%;background:#ffdcad;left:38px;top:42px}.avatar:after{content:"↻";position:absolute;left:55px;top:13px;font-size:30px;font-weight:900;color:#172135;opacity:.75}.eyes{position:absolute;left:57px;top:76px;width:36px;height:7px;background:linear-gradient(90deg,#172135 0 8px,transparent 8px 28px,#172135 28px);z-index:3}
.mascot-label{position:absolute;left:22px;right:22px;bottom:22px;z-index:2;display:flex;justify-content:space-between;gap:12px;align-items:end}.mascot-label b{font-size:20px}.mascot-label span{display:block;color:#bdeff5;font-size:13px;margin-top:4px}.seal{padding:9px 12px;border-radius:999px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.22);font-size:12px}
.panel{background:rgba(255,255,255,.66)!important;border:1px solid rgba(255,255,255,.86)!important;border-radius:32px!important;padding:20px!important;box-shadow:0 24px 70px rgba(77,79,110,.13)!important}
.panel h2{margin:0 0 12px!important;font-size:18px!important}.compact-control label span{color:#64708a!important;font-size:12px!important;text-transform:uppercase!important;letter-spacing:.08em!important;font-weight:900!important}
.compact-control input:not([type="radio"]):not([type="checkbox"]),.compact-control select,.compact-control textarea{background:#fffdf4!important;border:1px solid var(--line)!important;border-radius:16px!important;color:var(--ink)!important;font-weight:700!important}
.compact-control input[type="radio"],.compact-control input[type="checkbox"]{accent-color:var(--orange)!important;cursor:pointer!important}.compact-control label{cursor:pointer!important}
#generate-button{background:linear-gradient(135deg,var(--orange),#ffb84f)!important;color:#24121a!important;border:0!important;border-radius:18px!important;font-weight:1000!important;box-shadow:0 16px 32px rgba(242,106,56,.22)!important}
#surprise-button{background:linear-gradient(135deg,#c3f7ff,#a693ff)!important;color:#15213a!important;border:0!important;border-radius:18px!important;font-weight:1000!important}
.scroll{border-radius:34px;background:linear-gradient(180deg,#fffdf4,#fbebc5);border:1px solid rgba(255,255,255,.9);padding:24px;position:relative;overflow:hidden;min-height:470px}.path{display:grid;grid-template-columns:1fr auto 1fr;gap:14px;align-items:center;margin:12px 0 20px}.era-card{background:white;border:1px solid var(--line);border-radius:24px;padding:18px;box-shadow:0 14px 30px rgba(99,75,38,.08)}.era-card small{color:var(--teal);font-weight:900;text-transform:uppercase;letter-spacing:.1em}.era-card h3{font-size:26px;margin:9px 0 4px}.era-card p{margin:0;color:#657087;line-height:1.35}.swirl{width:76px;height:76px;border-radius:50%;display:grid;place-items:center;border:5px solid var(--teal);border-left-color:transparent;color:var(--orange);font-size:24px;font-weight:900}.wind-wave{height:112px;border-radius:28px;background:linear-gradient(135deg,rgba(29,184,197,.12),rgba(110,84,255,.14));border:1px dashed rgba(38,50,74,.18);position:relative;overflow:hidden}.wind-wave:before{content:"";position:absolute;inset:20px;background:repeating-radial-gradient(ellipse at center,transparent 0 12px,rgba(29,184,197,.65) 13px 16px,transparent 17px 28px);transform:skewX(-20deg)}
.micro{margin-top:18px;border-radius:24px;background:#172135;color:#fff;padding:18px}.micro h3{margin:0 0 8px;color:#f9d989!important}.micro p{font-size:18px;line-height:1.35;margin:0;color:#f7fbff!important}.lyric-box{background:#26324a}
.audio-card{background:#172135!important;color:white!important;border-radius:24px!important;padding:14px!important}.mixtape-card{background:white;border:1px solid var(--line);border-radius:24px;padding:18px}.mixtape-title{font-size:12px;color:var(--orange);font-weight:1000;text-transform:uppercase;letter-spacing:.12em}.mixtape-card h3{margin:8px 0 12px}.ttm-kv{display:flex;justify-content:space-between;gap:12px;border-bottom:1px dashed var(--line);padding:8px 0;font-size:14px}.ttm-kv span{color:#7d8697}.ttm-kv b{text-align:right}.lyrics-chip{background:#fff4d2;border-radius:16px;padding:12px;margin:10px 0;font-weight:800}
@media(max-width:900px){.path{grid-template-columns:1fr}.swirl{margin:auto}.ttm-kv{display:block}.ttm-kv b{text-align:left;display:block;margin-top:4px}}
"""


initial_source_era = ERAS[0]["label"]
initial_remix_era = ERAS[min(4, len(ERAS) - 1)]["label"]
initial_source_genre = genre_choices_for_era_label(initial_source_era)[0]
initial_remix_genre = genre_choices_for_era_label(initial_remix_era)[0]

with gr.Blocks(title="Turntable Time Machine", css=CSS) as demo:
    with gr.Column(elem_id="app-shell"):
        with gr.Row():
            with gr.Column(scale=11):
                gr.HTML(
                    """
                    <div class="banner">
                      <div class="tag">Whimsical timeline radio</div>
                      <div class="hero-title">Turntable <em>Time Machine</em></div>
                      <p class="sub">Original AI radio remixes from impossible musical timelines. Pick a source era, send it through another decade, and let a fictional AI DJ introduce your original time-travel track.</p>
                      <span class="safety-pill">No covers. No artist imitation. No voice cloning. Just original tiny timeline radio.</span>
                    </div>
                    """
                )
            with gr.Column(scale=8):
                gr.HTML(
                    """
                    <div class="wind-mascot">
                      <div class="orb"></div><div class="avatar"><div class="eyes"></div></div>
                      <div class="mascot-label"><div><b>The Wind-Time DJ</b><span>fictional guide through impossible remix eras</span></div><div class="seal">original mascot</div></div>
                    </div>
                    """
                )

        with gr.Row():
            with gr.Column(scale=4, elem_classes=["panel"]):
                gr.Markdown("## Choose your timeline path")
                with gr.Row():
                    source_era = gr.Dropdown(list(ERA_LABEL_TO_ID.keys()), value=initial_source_era, label="Source era", elem_classes=["compact-control"])
                    source_genre = gr.Dropdown(genre_choices_for_era_label(initial_source_era), value=initial_source_genre, label="Source genre", elem_classes=["compact-control"])
                with gr.Row():
                    remix_era = gr.Dropdown(list(ERA_LABEL_TO_ID.keys()), value=initial_remix_era, label="Remix era", elem_classes=["compact-control"])
                    remix_genre = gr.Dropdown(genre_choices_for_era_label(initial_remix_era), value=initial_remix_genre, label="Remix genre", elem_classes=["compact-control"])
                dj_persona = gr.Dropdown(list(PERSONA_LABEL_TO_ID.keys()), value=list(PERSONA_LABEL_TO_ID.keys())[0], label="Fictional DJ persona", elem_classes=["compact-control"])
                with gr.Row():
                    broadcast_language = gr.Dropdown(list(LANGUAGE_LABEL_TO_ID.keys()), value="English", label="Broadcast language", elem_classes=["compact-control"])
                    vocal_mode = gr.Dropdown(VOCAL_MODES, value="Instrumental only", label="Vocal mode", elem_classes=["compact-control"])
                lyric_theme = gr.Dropdown(list(THEME_LABEL_TO_ID.keys()), value=list(THEME_LABEL_TO_ID.keys())[0], label="Lyric theme", visible=False, elem_classes=["compact-control"])
                prompt_language_mode = gr.Dropdown(PROMPT_MODES, value=PROMPT_MODES[0], label="Music prompt language", elem_classes=["compact-control"])
                mood = gr.Dropdown(MOODS, value=MOODS[0], label="Mood", elem_classes=["compact-control"])
                audio_texture = gr.Dropdown(list(TEXTURE_LABEL_TO_ID.keys()), value=list(TEXTURE_LABEL_TO_ID.keys())[-1], label="Audio texture", elem_classes=["compact-control"])
                with gr.Row():
                    duration = gr.Radio(DURATIONS, value=15, label="Duration", elem_classes=["compact-control"])
                    seed = gr.Number(value=12345, precision=0, label="Seed", elem_classes=["compact-control"])
                    random_seed = gr.Checkbox(value=True, label="Random seed")
                with gr.Row():
                    surprise_button = gr.Button("Surprise Me", elem_id="surprise-button")
                    generate_button = gr.Button("Bend the Timeline", elem_id="generate-button")

            with gr.Column(scale=8):
                route_html = gr.HTML(timeline_route_html(initial_source_era, initial_source_genre, initial_remix_era, initial_remix_genre))
                with gr.Row():
                    with gr.Column(scale=6):
                        journey_html = gr.HTML(
                            f"<div class='scroll'>{timeline_route_html(initial_source_era, initial_source_genre, initial_remix_era, initial_remix_genre)}<div class='micro'><h3>Fictional DJ intro</h3><p>Generate a broadcast to hear the route open.</p></div></div>"
                        )
                    with gr.Column(scale=5, elem_classes=["panel"]):
                        final_audio = gr.Audio(label="Final broadcast", elem_classes=["audio-card"])
                        music_audio = gr.Audio(label="Music only", elem_classes=["audio-card"])
                        intro_audio = gr.Audio(label="Spoken DJ intro", elem_classes=["audio-card"])
                        intro_audio_status = gr.Markdown("Spoken DJ intro appears here when Kokoro TTS is available.")
                        mixtape_card = gr.HTML("<div class='mixtape-card'><div class='mixtape-title'>Mixtape Card</div><h3>Waiting for a timeline bend.</h3></div>")
                with gr.Accordion("Generated text and status", open=False):
                    dj_intro_text = gr.Textbox(label="Fictional DJ intro text", lines=3)
                    micro_lyrics_text = gr.Textbox(label="Generated micro-lyrics", lines=3)
                    generated_prompt_text = gr.Textbox(label="Generated ACE-Step prompt", lines=7)
                    model_status = gr.Markdown()
                    safety_note = gr.Markdown(copyright_safety_note())

    source_era.change(update_source_genres, source_era, source_genre, api_name=False).then(
        timeline_route_html, [source_era, source_genre, remix_era, remix_genre], route_html, api_name=False
    )
    source_genre.change(timeline_route_html, [source_era, source_genre, remix_era, remix_genre], route_html, api_name=False)
    remix_era.change(update_remix_genres, remix_era, remix_genre, api_name=False).then(
        timeline_route_html, [source_era, source_genre, remix_era, remix_genre], route_html, api_name=False
    )
    remix_genre.change(timeline_route_html, [source_era, source_genre, remix_era, remix_genre], route_html, api_name=False)
    vocal_mode.change(update_lyric_theme_visibility, vocal_mode, lyric_theme, api_name=False)

    surprise_button.click(
        surprise_me,
        outputs=[
            source_era,
            source_genre,
            remix_era,
            remix_genre,
            dj_persona,
            audio_texture,
            mood,
            broadcast_language,
            prompt_language_mode,
            vocal_mode,
            lyric_theme,
            duration,
            seed,
            random_seed,
            route_html,
        ],
        api_name=False,
    )

    generate_button.click(
        generate_time_machine_mix,
        inputs=[
            source_era,
            source_genre,
            remix_era,
            remix_genre,
            dj_persona,
            audio_texture,
            mood,
            broadcast_language,
            prompt_language_mode,
            vocal_mode,
            lyric_theme,
            duration,
            seed,
            random_seed,
        ],
        outputs=[
            final_audio,
            music_audio,
            intro_audio,
            intro_audio_status,
            dj_intro_text,
            micro_lyrics_text,
            generated_prompt_text,
            mixtape_card,
            model_status,
            safety_note,
            route_html,
            journey_html,
        ],
        api_name=False,
    )


if __name__ == "__main__":
    demo.launch()
