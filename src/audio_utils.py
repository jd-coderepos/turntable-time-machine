from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

try:
    from scipy.signal import resample_poly
except Exception:  # pragma: no cover - dependency fallback for tiny runtimes
    resample_poly = None


def load_audio(path: str) -> tuple[np.ndarray, int]:
    audio, sr = sf.read(path, always_2d=True)
    return audio.astype(np.float32), int(sr)


def save_audio(path: str, audio: np.ndarray, sr: int) -> str:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, normalize_audio(ensure_2d_audio(audio)), sr)
    return path


def normalize_audio(audio: np.ndarray, peak: float = 0.92) -> np.ndarray:
    audio = np.asarray(audio, dtype=np.float32)
    max_amp = float(np.max(np.abs(audio))) if audio.size else 0.0
    if max_amp > 0:
        audio = audio / max_amp * min(peak, max_amp if max_amp < peak else peak)
    return np.clip(audio, -1.0, 1.0)


def ensure_2d_audio(audio: np.ndarray) -> np.ndarray:
    audio = np.asarray(audio, dtype=np.float32)
    if audio.ndim == 1:
        return np.stack([audio, audio], axis=1)
    if audio.shape[1] == 1:
        return np.repeat(audio, 2, axis=1)
    return audio[:, :2]


def resample_if_needed(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    if orig_sr == target_sr:
        return ensure_2d_audio(audio)
    if resample_poly is None:
        audio = ensure_2d_audio(audio)
        old_x = np.linspace(0.0, 1.0, len(audio), endpoint=False)
        new_len = max(1, int(len(audio) * target_sr / orig_sr))
        new_x = np.linspace(0.0, 1.0, new_len, endpoint=False)
        left = np.interp(new_x, old_x, audio[:, 0])
        right = np.interp(new_x, old_x, audio[:, 1])
        return np.stack([left, right], axis=1).astype(np.float32)
    gcd = np.gcd(orig_sr, target_sr)
    return resample_poly(ensure_2d_audio(audio), target_sr // gcd, orig_sr // gcd, axis=0).astype(np.float32)


def add_silence(duration_seconds: float, sr: int) -> np.ndarray:
    return np.zeros((int(duration_seconds * sr), 2), dtype=np.float32)


def concatenate_audio(parts: list[np.ndarray], sr: int) -> np.ndarray:
    usable = [ensure_2d_audio(part) for part in parts if part is not None and len(part)]
    return np.concatenate(usable, axis=0) if usable else add_silence(0.5, sr)
