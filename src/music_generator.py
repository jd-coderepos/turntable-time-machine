from __future__ import annotations

from pathlib import Path

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


def generate_fallback_music(prompt: str, duration: int, bpm: int, seed: int | None, output_path: str) -> dict:
    sr = 44100
    rng = np.random.default_rng(seed)
    total = int(duration * sr)
    audio = np.zeros(total, dtype=np.float32)
    beat = 60.0 / max(bpm, 1)
    samples_per_beat = int(beat * sr)
    key = int(rng.integers(0, 7))
    root = 110.0 * (2 ** (key / 12))
    chords = [root, root * 2 ** (3 / 12), root * 2 ** (7 / 12), root * 2 ** (10 / 12)]
    t = np.arange(total) / sr

    bass_notes = [root / 2, root * 2 ** (5 / 12) / 2, root * 2 ** (7 / 12) / 2, root * 2 ** (3 / 12) / 2]
    for i in range(0, total, samples_per_beat):
        n = min(samples_per_beat, total - i)
        local_t = np.arange(n) / sr
        kick = np.sin(2 * np.pi * (62 * np.exp(-local_t * 24)) * local_t) * np.exp(-local_t * 18)
        audio[i : i + n] += kick.astype(np.float32) * 0.55
        bass = _tone(bass_notes[(i // samples_per_beat) % len(bass_notes)], local_t, "square")
        audio[i : i + n] += bass * _env(n, sr, 0.005, 0.12) * 0.12

    bar = max(samples_per_beat * 4, 1)
    for i in range(0, total, bar):
        n = min(bar, total - i)
        local_t = np.arange(n) / sr
        chord = sum(_tone(freq, local_t, "saw") for freq in chords) / len(chords)
        audio[i : i + n] += chord * _env(n, sr, 0.4, 0.4) * 0.09
        chords = chords[1:] + chords[:1]

    hat_interval = max(samples_per_beat // 2, 1)
    noise = rng.normal(0, 1, total).astype(np.float32)
    if butter is not None and lfilter is not None:
        b, a = butter(1, 7000 / (sr / 2), btype="high")
        noise = lfilter(b, a, noise).astype(np.float32)
    else:
        noise = (noise - np.convolve(noise, np.ones(64, dtype=np.float32) / 64, mode="same")).astype(np.float32)
    for i in range(0, total, hat_interval):
        n = min(int(0.045 * sr), total - i)
        audio[i : i + n] += noise[i : i + n] * _env(n, sr, 0.001, 0.035) * 0.055

    shimmer = _tone(root * 4, t, "sine") * 0.018 + _tone(root * 6, t, "sine") * 0.011
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
    try:
        # ACE-Step inference is intentionally lazy and optional for Space portability.
        # Install/configure ACE-Step in the runtime, then replace this block with the
        # project-specific pipeline call for ACE-Step/Ace-Step1.5.
        import acestep  # type: ignore  # noqa: F401

        raise RuntimeError("ACE-Step wrapper hook is present, but local inference is not configured.")
    except Exception as exc:
        result = generate_fallback_music(prompt, duration, bpm, seed, output_path)
        if vocal_mode == "Wordless vocal texture":
            result["vocal_rendering_status"] = "wordless_fallback_to_instrumental"
        elif vocal_mode == "Original micro-lyrics":
            result["vocal_rendering_status"] = "lyrics_fallback_to_instrumental"
        result["status"] += f" ACE-Step status: {exc}"
        return result
