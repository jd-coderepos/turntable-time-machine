from __future__ import annotations

import numpy as np

try:
    from scipy.signal import butter, lfilter
except Exception:  # pragma: no cover - dependency fallback for tiny runtimes
    butter = None
    lfilter = None

from .audio_utils import ensure_2d_audio, normalize_audio


def _lowpass(audio: np.ndarray, sr: int, cutoff: float) -> np.ndarray:
    if butter is None or lfilter is None:
        kernel = np.ones(7, dtype=np.float32) / 7
        return np.apply_along_axis(lambda x: np.convolve(x, kernel, mode="same"), 0, audio).astype(np.float32)
    b, a = butter(2, min(cutoff / (sr / 2), 0.98), btype="low")
    return lfilter(b, a, audio, axis=0).astype(np.float32)


def _bandpass(audio: np.ndarray, sr: int, low: float, high: float) -> np.ndarray:
    if butter is None or lfilter is None:
        blurred = _lowpass(audio, sr, high)
        very_low = _lowpass(audio, sr, low)
        return (blurred - very_low * 0.35).astype(np.float32)
    b, a = butter(2, [low / (sr / 2), min(high / (sr / 2), 0.98)], btype="band")
    return lfilter(b, a, audio, axis=0).astype(np.float32)


def _compress(audio: np.ndarray, drive: float = 1.4) -> np.ndarray:
    return np.tanh(audio * drive) / np.tanh(drive)


def _echo(audio: np.ndarray, sr: int, delay: float = 0.055, amount: float = 0.16) -> np.ndarray:
    out = audio.copy()
    offset = int(delay * sr)
    if offset < len(out):
        out[offset:] += audio[:-offset] * amount
    return out


def apply_texture(audio: np.ndarray, sr: int, texture_id: str) -> np.ndarray:
    audio = ensure_2d_audio(audio)
    rng = np.random.default_rng(777)
    texture_id = texture_id or "clean_digital"
    if texture_id == "vinyl_crackle":
        crackles = (rng.random(audio.shape[0]) > 0.996).astype(np.float32) * rng.uniform(-0.18, 0.18, audio.shape[0])
        audio = _lowpass(audio, sr, 12500) + crackles[:, None] * 0.25
    elif texture_id == "cassette_warmth":
        audio = _compress(audio, 1.25) + rng.normal(0, 0.004, audio.shape).astype(np.float32)
        audio = _lowpass(audio, sr, 11000)
    elif texture_id == "fm_radio":
        audio = _compress(_lowpass(audio, sr, 14000), 1.6)
    elif texture_id == "mono_radio":
        mono = audio.mean(axis=1, keepdims=True)
        audio = np.repeat(mono, 2, axis=1) * 0.85 + audio * 0.15
        audio = _bandpass(audio, sr, 180, 5200)
    elif texture_id == "club_pa":
        audio = _compress(_echo(audio, sr), 1.55)
    elif texture_id == "vhs_glow":
        audio = _lowpass(_compress(audio, 1.2), sr, 9000)
    elif texture_id == "mp3_compression":
        audio = np.round(_lowpass(audio, sr, 8500) * 96) / 96
    return normalize_audio(audio)
