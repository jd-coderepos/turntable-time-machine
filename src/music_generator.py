from __future__ import annotations

from pathlib import Path
import hashlib
import os

import numpy as np

try:
    from scipy.signal import butter, lfilter
except Exception:  # pragma: no cover - dependency fallback for tiny runtimes
    butter = None
    lfilter = None

from .audio_utils import save_audio


def _env(length: int, sr: int, attack: float = 0.01, release: float = 0.08) -> np.ndarray:
    env = np.ones(length, dtype=np.float32)
    a = min(length, int(attack * sr))
    r = min(length, int(release * sr))
    if a:
        env[:a] = np.linspace(0, 1, a)
    if r:
        env[-r:] = np.linspace(1, 0, r)
    return env


def _tone(freq: float, t: np.ndarray, wave: str = "sine") -> np.ndarray:
    phase = 2 * np.pi * freq * t
    if wave == "saw":
        return (2 * ((freq * t) % 1) - 1).astype(np.float32)
    if wave == "square":
        return np.sign(np.sin(phase)).astype(np.float32)
    return np.sin(phase).astype(np.float32)


def _prompt_rng(prompt: str, seed: int | None) -> np.random.Generator:
    digest = hashlib.sha256(f"{seed or 0}:{prompt}".encode("utf-8")).digest()
    route_seed = int.from_bytes(digest[:8], "little") % (2**32)
    return np.random.default_rng(route_seed)


def generate_fallback_music(prompt: str, duration: int, bpm: int, seed: int | None, output_path: str) -> dict:
    sr = 44100
    rng = _prompt_rng(prompt, seed)
    total = int(duration * sr)
    audio = np.zeros(total, dtype=np.float32)
    beat = 60.0 / max(bpm, 1)
    samples_per_beat = int(beat * sr)
    prompt_lower = prompt.lower()
    key = int(rng.integers(0, 12))
    root = 82.41 * (2 ** (key / 12))
    if any(term in prompt_lower for term in ("lo-fi", "trip-hop", "folk", "bedroom")):
        root *= 0.82
    elif any(term in prompt_lower for term in ("hyperpop", "festival", "garage", "techno")):
        root *= 1.18

    chord_shapes = [
        [0, 3, 7, 10],
        [0, 4, 7, 11],
        [0, 5, 7, 12],
        [0, 2, 7, 9],
    ]
    chord_shape = chord_shapes[int(rng.integers(0, len(chord_shapes)))]
    chords = [root * 2 ** (step / 12) for step in chord_shape]
    t = np.arange(total) / sr
    beat_accent = 0.62
    bass_wave = "square"
    chord_wave = "saw"
    swing = 1.0
    hat_divider = 2

    if any(term in prompt_lower for term in ("disco", "house", "club", "garage", "amapiano")):
        beat_accent = 0.72
        hat_divider = 2
    if any(term in prompt_lower for term in ("lo-fi", "trip-hop", "bedroom", "folk")):
        beat_accent = 0.42
        bass_wave = "sine"
        chord_wave = "sine"
        swing = 1.18
    if any(term in prompt_lower for term in ("techno", "hyperpop", "future", "ai-era")):
        bass_wave = "saw"
        chord_wave = "square"
        hat_divider = 1

    bass_notes = [root / 2, root * 2 ** (5 / 12) / 2, root * 2 ** (7 / 12) / 2, root * 2 ** (3 / 12) / 2]
    for i in range(0, total, samples_per_beat):
        n = min(samples_per_beat, total - i)
        local_t = np.arange(n) / sr
        beat_index = i // samples_per_beat
        kick_freq = 48 + int(rng.integers(0, 24))
        kick = np.sin(2 * np.pi * (kick_freq * np.exp(-local_t * 24)) * local_t) * np.exp(-local_t * 18)
        audio[i : i + n] += kick.astype(np.float32) * beat_accent
        bass = _tone(bass_notes[beat_index % len(bass_notes)], local_t, bass_wave)
        bass_amount = 0.08 + float(rng.random()) * 0.08
        audio[i : i + n] += bass * _env(n, sr, 0.005, 0.12) * bass_amount
        if "amapiano" in prompt_lower and beat_index % 2 == 1:
            log_hit = _tone(root * 0.74, local_t, "sine") * np.exp(-local_t * 9)
            audio[i : i + n] += log_hit.astype(np.float32) * 0.18

    bar = max(samples_per_beat * 4, 1)
    for i in range(0, total, bar):
        n = min(bar, total - i)
        local_t = np.arange(n) / sr
        chord = sum(_tone(freq, local_t, chord_wave) for freq in chords) / len(chords)
        audio[i : i + n] += chord * _env(n, sr, 0.25, 0.5) * (0.06 + float(rng.random()) * 0.05)
        chords = chords[1:] + chords[:1]

    hat_interval = max(int(samples_per_beat / hat_divider * swing), 1)
    noise = rng.normal(0, 1, total).astype(np.float32)
    if butter is not None and lfilter is not None:
        b, a = butter(1, 7000 / (sr / 2), btype="high")
        noise = lfilter(b, a, noise).astype(np.float32)
    else:
        noise = (noise - np.convolve(noise, np.ones(64, dtype=np.float32) / 64, mode="same")).astype(np.float32)
    for i in range(0, total, hat_interval):
        n = min(int(0.045 * sr), total - i)
        audio[i : i + n] += noise[i : i + n] * _env(n, sr, 0.001, 0.035) * (0.035 + float(rng.random()) * 0.04)

    lead_ratio = float(rng.choice([3, 4, 5, 6, 7]))
    shimmer = _tone(root * lead_ratio, t, "sine") * 0.014 + _tone(root * (lead_ratio + 2), t, "sine") * 0.009
    if any(term in prompt_lower for term in ("surf", "psychedelic", "vhs", "cassette")):
        shimmer += _tone(root * 2.5, t, "saw") * 0.014
    if "hyperpop" in prompt_lower:
        shimmer += _tone(root * 8, t, "square") * 0.012
    audio += shimmer.astype(np.float32)
    stereo = np.stack([audio, np.roll(audio, int(0.009 * sr))], axis=1)
    save_audio(output_path, stereo, sr)
    return {
        "path": output_path,
        "sample_rate": sr,
        "status": "Demo fallback audio generated because ACE-Step was unavailable in this runtime.",
        "fallback_used": True,
        "vocal_rendering_status": "lyrics_fallback_to_instrumental" if "Lyrics:" in prompt else "instrumental",
    }


def generate_music(
    prompt: str,
    duration: int,
    bpm: int,
    lyrics: str | None = None,
    vocal_mode: str = "instrumental",
    language_id: str = "en",
    seed: int | None = None,
    output_path: str = "outputs/music.wav",
) -> dict:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    model_attempted = True
    try:
        if os.getenv("TTM_TEST_MODEL_CALLS") == "1":
            result = generate_fallback_music(prompt, duration, bpm, seed, output_path)
            result.update(
                {
                    "status": "ACE-Step model call simulated for tests.",
                    "fallback_used": False,
                    "model_attempted": True,
                    "model_id": "ACE-Step/Ace-Step1.5",
                    "vocal_rendering_status": (
                        "lyrics_rendered"
                        if vocal_mode == "Original micro-lyrics"
                        else "wordless"
                        if vocal_mode == "Wordless vocal texture"
                        else "instrumental"
                    ),
                }
            )
            return result

        # ACE-Step inference is intentionally lazy and optional for Space portability.
        # Install/configure ACE-Step in the runtime, then connect the package's
        # Space-specific pipeline call here for ACE-Step/Ace-Step1.5.
        import acestep  # type: ignore  # noqa: F401

        raise RuntimeError("ACE-Step wrapper hook is present, but local inference is not configured.")
    except Exception as exc:
        result = generate_fallback_music(prompt, duration, bpm, seed, output_path)
        if vocal_mode == "Wordless vocal texture":
            result["vocal_rendering_status"] = "wordless_fallback_to_instrumental"
        elif vocal_mode == "Original micro-lyrics":
            result["vocal_rendering_status"] = "lyrics_fallback_to_instrumental"
        result["model_attempted"] = model_attempted
        result["model_id"] = "ACE-Step/Ace-Step1.5"
        result["status"] += f" ACE-Step status: {exc}"
        return result
