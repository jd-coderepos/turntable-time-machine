---
title: Turntable Time Machine
emoji: 🎛️
colorFrom: yellow
colorTo: purple
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
license: mit
tags:
  - build-small
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

Original AI radio remixes from impossible musical timelines.

Turntable Time Machine is a Gradio Space for the Build Small Hackathon Thousand Token Wood track. It is an audio-first radio console: choose a source era, remix era, fictional DJ host, broadcast language, nostalgia texture, and vocal mode, then generate a short original time-travel broadcast.

## What it does

- Builds safe music prompts from curated taxonomy JSON files.
- Generates a fictional DJ intro text in English, German, French, or Spanish.
- Uses optional original two-line micro-lyrics from `CohereLabs/tiny-aya-global`.
- Routes music generation through an ACE-Step wrapper.
- Routes spoken DJ narration through a Kokoro wrapper.
- Falls back gracefully to synthetic demo audio and text-only DJ intros when models are unavailable.
- Applies subtle nostalgia textures such as vinyl crackle, cassette warmth, FM radio, VHS glow, and club PA.

## Why it fits Thousand Token Wood

The app is whimsical, selection-driven, small-model-oriented, and deliberately off-brand: it turns structured taxonomy choices into tiny AI radio postcards instead of open-ended prompt boxes.

## Model stack

- Music generation: `ACE-Step/Ace-Step1.5`
- Spoken fictional DJ intro: `hexgrad/Kokoro-82M`
- Multilingual text and micro-lyrics: `CohereLabs/tiny-aya-global`

All intended models are under 32B parameters. No paid external API is required. The repository includes fallback paths so the app still launches and generates playable audio in limited runtimes.

## Build Small compliance

- Gradio app with `app.py`
- Uses small/open model targets under 32B parameters
- Includes fallback behavior for unavailable model downloads or restricted checkpoints
- Avoids famous-song remixing, artist imitation, real-DJ imitation, voice cloning, copyrighted lyrics, and copyrighted melody reproduction
- Includes custom Wind Nomad Radio-style UI rather than default Gradio styling

This project does not claim Tiny Titan by default because the full intended stack includes models that should be checked in the final Space runtime before adding the `tiny-titan` tag.

## Multilingual support

The app includes English, German, French, and Spanish in `data/languages.json`. Handcrafted deterministic templates are used for DJ intro text and prompt localization. Tiny Aya is used only for short optional text generation.

## Original Micro-Lyrics mode

Micro-lyrics are maximum two short lines, generated from structured dropdown selections. If Tiny Aya cannot load, deterministic fallback lyrics from the app are used. Tiny Aya generates text only; ACE-Step is the intended model for any sung/vocal rendering.

## Safety and originality policy

Turntable Time Machine generates original audio from broad musical-era descriptors. It does not create covers, reproduce famous songs, clone real voices, imitate real DJs, or generate copyrighted lyrics or melodies.

## How to run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

If you use a restricted Hugging Face model such as `CohereLabs/tiny-aya-global`, set a token locally without committing it:

```bash
set HF_TOKEN=hf_your_token_here
set HUGGING_FACE_HUB_TOKEN=hf_your_token_here
```

On Hugging Face Spaces, add the token under **Settings -> Repository secrets** as `HF_TOKEN` or `HUGGING_FACE_HUB_TOKEN`.

Optional override:

```bash
set TEXT_MODEL_ID=CohereLabs/tiny-aya-global
```

## How to use

1. Choose source era and genre.
2. Choose remix era and genre.
3. Pick fictional DJ persona, language, mood, texture, and vocal mode.
4. Click **Surprise Me** for a complete randomized route.
5. Click **Bend the Timeline**.
6. Play the final broadcast and inspect the mixtape card.

## Demo examples

- 1960s Motown-inspired soul -> 1990s deep house, German DJ intro
- 1970s funk -> 2020s amapiano-inspired groove, English DJ intro
- 1980s synth-pop -> 2000s filtered disco house, French DJ intro
- 1990s trip-hop -> 2020s lo-fi chill, Spanish micro-lyrics
- 2000s UK garage -> 1970s disco, bilingual prompt

## Demo video link

Placeholder: add demo video URL here.

## Social post link

Placeholder: add social post URL here.

## Codex attribution note

This project was developed with Codex assistance. Codex-attributed commits are included in the connected GitHub repository / Space history for Build Small judging.

## Demo video script

1. Show the custom retro Wind Nomad Radio-inspired UI.
2. Click **Surprise Me**.
3. Generate a short instrumental mix.
4. Show the mixtape card and safety note.
5. Generate a second example with **Original micro-lyrics**.
6. Show the multilingual DJ intro text.
7. Play the final audio.

## Social post draft

I built Turntable Time Machine for #BuildSmall: a tiny AI radio console that creates original cross-era music postcards. Pick a source decade, remix it through another era, choose a fictional DJ host and broadcast language, and generate a short original audio segment with optional micro-lyrics. Built with Gradio + small models under 32B.
