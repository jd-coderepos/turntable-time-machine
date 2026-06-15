---
title: Turntable Time Machine
emoji: 🎛️
colorFrom: yellow
colorTo: purple
sdk: gradio
sdk_version: 5.49.1
python_version: 3.10.13
app_file: app.py
pinned: false
license: mit
models:
  - ACE-Step/Ace-Step1.5
  - hexgrad/Kokoro-82M
  - CohereLabs/tiny-aya-global
tags:
  - build-small
  - track:wood
  - thousand-token-wood
  - best-use-of-codex
  - off-brand
  - best-demo
  - audio
  - music-generation
  - text-to-audio
  - multilingual
  - gradio
  - small-models
---

# Turntable Time Machine

## Original AI radio postcards from impossible musical timelines.

Turntable Time Machine is a whimsical Gradio app built for the Hugging Face x Gradio Build Small Hackathon. It gives users a tiny retro radio console where they can choose a source era, remix era, fictional DJ host, broadcast language, nostalgia texture, mood, and vocal mode, then generate a short original "broadcast" from that alternate timeline.

The idea is simple: what if a late-night AI DJ could take the vocabulary of one decade and route it through the production logic of another? Not a cover, not a famous-song remix, not an artist imitation, but a little audio artifact from a timeline that never quite existed.

This submission targets the **Thousand Token Wood** track: playful, compact, selection-driven, and oriented around small/open model components. The app currently includes optional hooks for ACE-Step music generation, Kokoro spoken narration, and Tiny Aya text generation, while keeping the experience usable through deterministic templates and local fallback audio when model loading is unavailable.

## Submission Links

- Live Space: add Hugging Face Space URL here
- GitHub repo: add repository URL here
- Demo video: add demo video URL here
- Social post: add social post URL here
- Agent traces: add trace dataset or notes URL here, if applicable

## Demo Script

Recommended single demo case:

**1980s Synth-pop -> 2000s Filtered disco house** with **The Neon Signal Host**, **English**, **Original micro-lyrics**, **Future city**, **VHS glow**, and a **dreamy and cinematic** mood.

This is the strongest one-video route because it shows the app's full personality in one pass: a clear before/after era transformation, a fictional DJ identity, optional generated lyrics, a visible prompt card, audio texture processing, and the final broadcast output.

Concise demo flow:

1. Open the Turntable Time Machine Space.
2. Show the custom radio-console interface and the timeline route panel.
3. Set the source to **1980s / Synth-pop**.
4. Set the remix destination to **2000s / Filtered disco house**.
5. Choose **The Neon Signal Host** as the fictional DJ.
6. Choose **English** so the spoken intro path has the best chance to work when Kokoro is available.
7. Set vocal mode to **Original micro-lyrics** and lyric theme to **Future city**.
8. Pick **VHS glow** or **Clean digital master** depending on whether you want a more nostalgic or cleaner audio result.
9. Click **Bend the Timeline**.
10. Play the final broadcast, then briefly show the DJ intro text, generated micro-lyrics, generated ACE-Step prompt, model status, and mixtape card.

Optional quick second shot if the first generation finishes fast: click **Surprise Me** to show that the app can build a complete route automatically.

## Main Features

* Custom illustrated Gradio interface styled as a fictional timeline radio console
* Era-to-era music routing across the 1960s, 1970s, 1980s, 1990s, 2000s, 2010s, and 2020s
* Curated genre vocabulary for soul, disco, funk, synth-pop, house, trip-hop, UK garage, hyperpop, lo-fi, amapiano-inspired grooves, AI-era electronic, and more
* Fictional DJ personas with distinct intro templates and voice direction
* English, German, French, and Spanish broadcast-language support for text prompts and DJ intro text
* Three vocal modes: instrumental only, wordless vocal texture, and original two-line micro-lyrics
* Audio nostalgia textures such as vinyl crackle, cassette warmth, FM radio, mono radio, club PA, VHS glow, early MP3 compression, and clean digital master
* Surprise Me route generation for complete randomized sessions
* Mixtape card output with route, language, prompt mode, vocal mode, texture, BPM, seed, model status, and safety note
* Graceful local fallbacks so the app can still produce playable audio and useful text when model downloads, GPU access, or optional packages are unavailable

## Timeline Engine

Turntable Time Machine is more than a blank prompt box. The app constrains generation through curated data and a small programmed routing layer:

```text
User selections
-> source era and genre lookup
-> remix era and genre lookup
-> fictional DJ persona lookup
-> language and prompt-mode routing
-> mood sanitization
-> BPM choice from genre ranges
-> optional Tiny Aya micro-lyrics
-> safe ACE-Step music prompt construction
-> optional Kokoro spoken-DJ intro
-> fallback music generation if needed
-> nostalgia texture processing
-> final broadcast mix
-> mixtape card and safety note
```

The important design choice is that the app uses broad musical descriptors instead of asking users to name songs, artists, singers, producers, DJs, or copyrighted material. The result is meant to feel culturally legible without being a copy machine.

## Models Used

| Component | Model | Parameters | Used for |
| --- | --- | ---: | --- |
| Music generation target | [ACE-Step/Ace-Step1.5](https://huggingface.co/ACE-Step/Ace-Step1.5) | under 32B target stack | Original short music clips from safe era-remix prompts |
| Spoken DJ intro target | [hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) | 82M | Optional fictional DJ narration, without voice cloning |
| Text / micro-lyrics target | [CohereLabs/tiny-aya-global](https://huggingface.co/CohereLabs/tiny-aya-global) | small multilingual model | Optional two-line original micro-lyrics |
| Template and synth fallback | none | 0 | Keeps the app usable in restricted or model-limited runtimes |

The repository is intentionally defensive about runtime availability. ACE-Step and Kokoro are represented as lazy optional hooks; if their packages, weights, or hardware path are unavailable, the app falls back to generated demo audio and text-only DJ intro behavior. Tiny Aya also falls back to deterministic two-line lyrics if access is restricted.

## Data

The app's personality lives in the JSON files under `data/`.

`data/music_eras.json` defines the eras, genres, safe prompt styles, BPM ranges, instruments, sonic traits, and "avoid" notes that keep transformations broad and original.

`data/dj_personas.json` defines six fictional hosts: The Midnight Radio Curator, The Velvet Disco Host, The Warehouse Announcer, The Block Party Selector, The Sunset Terrace DJ, and The Neon Signal Host.

`data/audio_textures.json` defines post-processing flavors that make the generated clip feel like a record, cassette, radio broadcast, club system, VHS-era recording, early MP3, or clean master.

`data/languages.json` defines the supported broadcast languages: English, German, French, and Spanish.

`data/lyric_themes.json` defines compact lyric themes such as Night drive, Lost summer, Future city, Dancefloor memory, Radio signal, Sunset goodbye, and Time travel.

## Build Small Fit

Turntable Time Machine fits Thousand Token Wood because it is small, playful, local/open-weight-oriented, and intentionally off-brand. Instead of building a general music-prompting interface, it creates a constrained toy-like instrument: users make structured choices, the app turns those choices into safe generation instructions, and the output is a tiny timeline broadcast.

It is also designed to remain demonstrable on limited hackathon infrastructure. If the intended model stack cannot run in the current environment, the app still launches, still produces audio, still shows its routing logic, and still makes the safety boundaries visible.

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

On macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Testing

Run the logic and model-routing tests:

```bash
python -m unittest discover -s tests
```

The tests cover taxonomy loading, era-dependent genre dropdowns, lyric-theme visibility, Surprise Me state generation, fallback audio, final mix creation, and simulated ACE-Step/Kokoro/Tiny Aya call paths.

For test-only mocked model paths:

```bash
set TTM_TEST_MODEL_CALLS=1
python -m unittest discover -s tests
```

`TTM_TEST_MODEL_CALLS=1` is only for tests. Normal app execution attempts the intended model hooks first and falls back gracefully when they are unavailable.

## Hugging Face Space Notes

Recommended Space settings:

```text
SDK: Gradio
Python: 3.10.13
App file: app.py
Hardware: ZeroGPU or a compatible GPU runtime for model-backed audio generation
```

Useful environment variables:

```text
TEXT_MODEL_ID=CohereLabs/tiny-aya-global
HF_TOKEN=hf_your_token_here
HUGGING_FACE_HUB_TOKEN=hf_your_token_here
```

If a restricted model is used, add the token under **Settings -> Repository secrets** as `HF_TOKEN` or `HUGGING_FACE_HUB_TOKEN`. Do not commit tokens to the repository.

## Safety and Originality

Turntable Time Machine is designed for original audio generation from broad era and genre descriptors. It does not create covers, reproduce famous songs, clone real voices, imitate real DJs, imitate specific artists, or generate copyrighted lyrics or melodies.

The prompt builder appends originality constraints to every music prompt. The lyric generator asks for only two short original lines and sanitizes generated text before use. The fictional DJ personas are invented hosts, not attempts to mimic real broadcasters or performers.

## Acknowledgements

This project was built with [OpenAI Codex](https://openai.com/codex/) assistance for the Build Small Hackathon. Codex supported the Gradio app structure, data-driven routing logic, fallback audio behavior, safety checks, tests, and README polishing.

Thanks to the Hugging Face, Gradio, and Build Small teams for creating a hackathon format that makes small-model experiments feel like musical toys, weird radios, and tiny instruments worth shipping.
