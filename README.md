---
title: Turntable Time Machine
emoji: 📻
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
  - facebook/mms-tts-eng
  - facebook/mms-tts-deu
  - facebook/mms-tts-fra
  - facebook/mms-tts-spa
  - CohereLabs/tiny-aya-global
tags:
  - build-small
  - thousand-token-wood
  - gradio
  - small-models
  - multilingual
  - audio
  - music-generation
  - text-to-audio
  - track:wood
  - sponsor:openai
  - achievement:offgrid
  - achievement:offbrand
  - achievement:fieldnotes
---

# 🤗 💿📻⏳ Turntable Time Machine

## **Pick two eras 🕰️. Summon a fictional DJ 🎙️. Hear a tiny radio broadcast from a timeline that never happened 📻✨.**

Turntable Time Machine is a whimsical Gradio app built for the Hugging Face x Gradio Build Small Hackathon. It lets users choose a source era 🕰️, remix era 🔁, fictional DJ host 🎙️, language 🌍, mood 🌈, texture 📼, and vocal mode 🎵, then generates a short original AI radio postcard 📻.

*The twist:* this is not a famous-song remix machine. The app uses broad musical-era vocabularies and safety constraints to make new little audio artifacts: 1960s soul through a 1990s house lens, 1980s synth-pop polished into 2000s filtered disco house, or a 2020s lo-fi signal drifting backward through old radio static.

This submission targets the **Thousand Token Wood** track: playful, compact, AI-native, and built around small/open model targets. ACE-Step, MMS TTS, and Tiny Aya are used as optional model hooks, while deterministic templates and fallback audio keep the app demonstrable when model access or GPU runtime is limited.

## 🔗 Submission Links

- 🤗 Live Space: https://huggingface.co/spaces/build-small-hackathon/turntable-time-machine
- GitHub repo: https://github.com/jd-coderepos/turntable-time-machine
- 🎬 Demo video: https://www.youtube.com/watch?v=EKCwTK88pUE
- Field notes & Social Post: [Bending Time with a Virtual DJ -- Field Notes from the Build Small AI Hackathon](https://medium.com/@jenlindadsouza/bending-musical-time-with-a-fictional-dj-field-notes-from-the-build-small-hackathon-71f10680ca0e?postPublishedType=repub)

## 🎬 Demo Script

A concise demo flow:

1. 🤗 Open the [Turntable Time Machine Space](https://huggingface.co/spaces/build-small-hackathon/turntable-time-machine).
2. Set **Source era** to **1960s** and **Source genre** to **Folk pop**.
3. Set **Remix era** to **2000s** and **Remix genre** to **2000s indie rock**.
4. Choose **The Warehouse Announcer** as the fictional DJ persona.
5. Choose **French** as the broadcast language.
6. Choose **Original micro-lyrics** and keep **Night drive** as the lyric theme.
7. Set **Music prompt language** to **English + broadcast language** to show the app's bilingual prompt path.
8. Keep **nostalgic and warm**, choose **Clean digital master**, and use the **10 second** duration.
9. Click **Bend the Timeline**.
10. Play the **Final broadcast**, then compare it with **Music only**.
11. Show the **Fictional DJ intro** text card and the **Spoken DJ intro** audio when MMS TTS is available.
12. Show the **Generated micro-lyrics** card and the **Mixtape Card** with the route, model status, BPM, seed, texture, and safety note.

🎬 Recommended one-video case: **1960s Folk pop -> 2000s indie rock** with **The Warehouse Announcer**, **French**, **Original micro-lyrics**, and **English + broadcast language**. It shows the app's full loop: era routing, fictional host text, multilingual prompt routing, generated micro-lyrics, safety-aware prompt, texture processing, and final audio.

⚠️ Note: The app does **not** generate covers, real-DJ imitation, voice clones, copyrighted lyrics, or famous melodies. Outputs are original compositions guided by broad genre descriptors.

## ℹ️ Main Features

* Custom illustrated [Gradio](https://www.gradio.app/) interface
* Era-to-era routing across the 1960s, 1970s, 1980s, 1990s, 2000s, 2010s, and 2020s
* Curated genre vocabulary for soul, disco, funk, synth-pop, house, trip-hop, UK garage, hyperpop, lo-fi, amapiano-inspired grooves, and AI-era electronic
* Six fictional DJ personas with original intro templates
* English, German, French, and Spanish broadcast text support
* Three vocal modes: Instrumental only, Wordless vocal texture, and Original micro-lyrics
* Nostalgia textures: vinyl crackle, cassette warmth, FM radio, mono radio, club PA, VHS glow, early MP3 compression, and clean digital master
* Surprise Me route generation
* Mixtape card with route, language, texture, BPM, seed, model status, and safety note
* Lazy model hooks and fallback generation for deployment reliability

### 🧠 Built-in Timeline Engine

Turntable Time Machine is not just a prompt wrapper around an audio model. Before generation, it runs a lightweight programmed Timeline Engine:

```text
User selections
→ source era / genre lookup
→ remix era / genre lookup
→ fictional DJ persona selection
→ language and prompt-mode routing
→ BPM selection from genre ranges
→ optional Tiny Aya micro-lyrics
→ safety-aware music prompt
→ optional MMS TTS DJ narration
→ ACE-Step music hook or fallback synth audio
→ nostalgia texture processing
→ final broadcast and mixtape card
```

🛠️ The design explores a simple idea: small models work better when the app gives them a playful structure. Curated taxonomies, deterministic routing, and clear guardrails turn a broad generation task into a tiny musical instrument.

## 🤖 Models Used

| Component | Model | Parameters | Used for |
| --- | --- | ---: | --- |
| Music generation target | [ACE-Step/Ace-Step1.5](https://huggingface.co/ACE-Step/Ace-Step1.5) | under 32B target stack | Original short music clips |
| Spoken DJ intro target | [facebook/mms-tts-eng](https://huggingface.co/facebook/mms-tts-eng), `deu`, `fra`, `spa` variants | 36.3M each for English model card | Optional fictional DJ narration in the selected broadcast language |
| Text / micro-lyrics target | [CohereLabs/tiny-aya-global](https://huggingface.co/CohereLabs/tiny-aya-global) | small multilingual model | Optional two-line original lyrics |
| Template and synth fallback | none | 0 | Keeps the app usable in restricted runtimes |

ACE-Step and MMS TTS are lazy optional hooks. If model packages, weights, or hardware are unavailable, the app falls back to playable synthetic demo audio and text-only DJ intros. Tiny Aya falls back to deterministic micro-lyrics when access is restricted.

## 🗂️ Data

The app's character layer lives in `data/`:

* `music_eras.json` defines eras, genres, safe prompt styles, BPM ranges, instruments, sonic traits, and avoid notes.
* `dj_personas.json` defines six fictional hosts, including The Midnight Radio Curator and The Neon Signal Host.
* `audio_textures.json` defines record, cassette, radio, club, VHS, MP3, and clean-master post-processing flavors.
* `languages.json` defines English, German, French, and Spanish.
* `lyric_themes.json` defines compact lyric themes such as Future city, Night drive, Radio signal, and Time travel.

## 🛠️ Local Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Run tests:

```bash
python -m unittest discover -s tests
```

For mocked model paths in tests only:

```bash
set TTM_TEST_MODEL_CALLS=1
python -m unittest discover -s tests
```

## Hugging Face Space / ZeroGPU Notes

Recommended Space settings:

```text
SDK: Gradio
Python: 3.10.13
App file: app.py
Hardware: ZeroGPU or compatible GPU runtime
```

Useful environment variables:

```text
TEXT_MODEL_ID=CohereLabs/tiny-aya-global
HF_TOKEN=hf_your_token_here
HUGGING_FACE_HUB_TOKEN=hf_your_token_here
```

If model access fails, add an `HF_TOKEN` secret with read access and make sure the Space owner has accepted any required model terms.

## 🛡️ Protective Guardrails

Turntable Time Machine is designed for original audio from broad musical-era descriptors. Its prompt builder avoids requests to imitate specific songs, artists, singers, producers, DJs, hooks, samples, lyrics, melodies, or arrangements.

The lyric generator asks for only two short original lines and sanitizes generated text before use. The DJ personas are fictional hosts, not imitations of real broadcasters or performers.

## 🙌 Acknowledgements

This project was built using [**OpenAI Codex**](https://openai.com/codex/) as a coding agent. Codex supported the Gradio app structure, timeline orchestration logic, fallback audio behavior, safety checks, tests, and submission-readiness polish.

Thank you to the **Gradio team** and the [Build Small Hackathon](https://huggingface.co/build-small-hackathon) partners for making room for tiny, playful, local/open-weight AI experiments. 🎛️📻✨
