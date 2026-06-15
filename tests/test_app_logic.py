from __future__ import annotations

import glob
import os
import unittest
from pathlib import Path

import soundfile as sf

import app
from src.lyrics_generator import generate_micro_lyrics
from src.music_generator import generate_music
from src.safety import sanitize_generated_lyrics
from src.tts import generate_dj_voice


class TurntableTimeMachineLogicTests(unittest.TestCase):
    def tearDown(self):
        os.environ.pop("TTM_TEST_MODEL_CALLS", None)
        patterns = [
            "outputs/test_*.wav",
            "outputs/final_mix_*.wav",
            "outputs/music_raw_*.wav",
            "outputs/music_processed_*.wav",
            "outputs/dj_intro_*.wav",
        ]
        for path in [item for pattern in patterns for item in glob.glob(pattern)]:
            try:
                Path(path).unlink()
            except OSError:
                pass

    def test_taxonomy_files_loaded(self):
        self.assertGreaterEqual(len(app.ERAS), 4)
        self.assertGreaterEqual(len(app.PERSONAS), 3)
        self.assertGreaterEqual(len(app.TEXTURES), 4)
        self.assertGreaterEqual(len(app.LANGUAGES), 4)
        self.assertGreaterEqual(len(app.THEMES), 4)

    def test_genre_dropdowns_update_from_selected_era(self):
        source_update = app.update_source_genres("1980s")
        remix_update = app.update_remix_genres("2020s")
        self.assertIn("Synth-pop", source_update["choices"])
        self.assertIn("Amapiano-inspired groove", remix_update["choices"])
        self.assertEqual(source_update["value"], source_update["choices"][0])
        self.assertEqual(remix_update["value"], remix_update["choices"][0])

    def test_lyric_theme_visibility_tracks_vocal_mode(self):
        self.assertTrue(app.update_lyric_theme_visibility("Original micro-lyrics")["visible"])
        self.assertFalse(app.update_lyric_theme_visibility("Instrumental only")["visible"])
        self.assertFalse(app.update_lyric_theme_visibility("Wordless vocal texture")["visible"])

    def test_micro_lyrics_sanitizer_removes_instruction_text(self):
        clean, warnings = sanitize_generated_lyrics(
            "No explanation, no punctuation\n"
            "Vapor dreams drift on neon haze\n"
            "We chase tomorrow through glass streets"
        )
        self.assertEqual(clean, "Vapor dreams drift on neon haze\nWe chase tomorrow through glass streets")
        self.assertTrue(any("instruction" in warning for warning in warnings))

    def test_compact_control_css_does_not_restyle_radio_inputs(self):
        self.assertIn('input:not([type="radio"]):not([type="checkbox"])', app.CSS)
        self.assertIn('input[type="radio"]', app.CSS)

    def test_surprise_me_returns_complete_valid_state(self):
        result = app.surprise_me()
        self.assertEqual(len(result), 15)
        self.assertIn(result[0], app.ERA_LABEL_TO_ID)
        self.assertIn(result[2], app.ERA_LABEL_TO_ID)
        self.assertIn(result[4], app.PERSONA_LABEL_TO_ID)
        self.assertIn(result[5], app.TEXTURE_LABEL_TO_ID)
        self.assertIn(result[7], app.LANGUAGE_LABEL_TO_ID)
        self.assertIn(result[8], app.PROMPT_MODES)
        self.assertIn(result[9], app.VOCAL_MODES)
        self.assertIn(result[11], app.DURATIONS)
        self.assertIn("era-card", result[14])

    def test_prompt_mode_labels_are_plain_language(self):
        self.assertEqual(
            app.PROMPT_MODES,
            ["Best stability (English)", "Broadcast language", "English + broadcast language"],
        )

    def test_music_wrapper_attempts_model_by_default_then_falls_back(self):
        result = generate_music(
            "Create an original music clip. No vocals. No lyrics.",
            duration=1,
            bpm=110,
            seed=101,
            output_path="outputs/test_default_model_attempt.wav",
        )
        self.assertTrue(result["model_attempted"])
        self.assertEqual(result["model_id"], "ACE-Step/Ace-Step1.5")
        self.assertTrue(result["fallback_used"])
        audio, sr = sf.read(result["path"])
        self.assertEqual(sr, 44100)
        self.assertGreater(audio.shape[0], 0)

    def test_fallback_music_varies_by_prompt_route(self):
        first = generate_music(
            "Create an original music clip. Start from 1960s Motown-inspired soul. Transform it into 2000s filtered disco house.",
            duration=1,
            bpm=118,
            seed=123,
            output_path="outputs/test_route_one.wav",
        )
        second = generate_music(
            "Create an original music clip. Start from 2020s lo-fi chill. Transform it into 1970s funk.",
            duration=1,
            bpm=118,
            seed=123,
            output_path="outputs/test_route_two.wav",
        )
        audio_one, _ = sf.read(first["path"])
        audio_two, _ = sf.read(second["path"])
        self.assertGreater(float(abs(audio_one - audio_two).mean()), 0.001)

    def test_audio_model_calls_can_be_exercised_with_test_switch(self):
        os.environ["TTM_TEST_MODEL_CALLS"] = "1"
        music = generate_music(
            "Create an original music clip. Optional wordless, non-lexical vocal texture only.",
            duration=1,
            bpm=122,
            vocal_mode="Wordless vocal texture",
            seed=202,
            output_path="outputs/test_model_music.wav",
        )
        tts = generate_dj_voice(
            "Signal detected. This is a fictional DJ intro.",
            "en",
            "neon_signal_host",
            "outputs/test_model_tts.wav",
        )
        lyrics = generate_micro_lyrics(
            app.ERAS[2],
            app.ERAS[2]["genres"][0],
            app.ERAS[4],
            app.ERAS[4]["genres"][0],
            "nostalgic and warm",
            app.THEMES[0],
            "en",
            seed=303,
        )
        self.assertFalse(music["fallback_used"])
        self.assertEqual(music["vocal_rendering_status"], "wordless")
        self.assertTrue(tts["tts_succeeded"])
        self.assertFalse(lyrics["fallback_used"])
        self.assertIn("simulated for tests", music["status"])
        self.assertIn("simulated for tests", tts["status"])
        self.assertIn("simulated for tests", lyrics["status"])

    def test_generate_pipeline_all_vocal_modes_create_final_audio(self):
        for index, vocal_mode in enumerate(app.VOCAL_MODES):
            with self.subTest(vocal_mode=vocal_mode):
                result = app.generate_time_machine_mix(
                    "1980s",
                    "Synth-pop",
                    "2000s",
                    "Filtered disco house",
                    "The Neon Signal Host",
                    "Clean digital master",
                    "nostalgic and warm",
                    "English",
                    "Best stability (English)",
                    vocal_mode,
                    "Night drive",
                    1,
                    400 + index,
                    False,
                )
                (
                    final_path,
                    music_path,
                    intro_path,
                    intro_status,
                    _intro_text,
                    lyrics_text,
                    prompt,
                    _card,
                    status,
                ) = result[:9]
                self.assertTrue(Path(final_path).exists())
                self.assertTrue(Path(music_path).exists())
                self.assertIsNone(intro_path)
                self.assertIn("Spoken DJ intro is unavailable", intro_status)
                self.assertIn("ACE-Step", status)
                self.assertIn("Spoken DJ intro unavailable", status)
                audio, sr = sf.read(final_path)
                self.assertEqual(sr, 44100)
                self.assertGreater(audio.shape[0], 0)
                if vocal_mode == "Original micro-lyrics":
                    self.assertGreaterEqual(len(lyrics_text.splitlines()), 2)
                    self.assertIn("Lyrics:", prompt)
                elif vocal_mode == "Wordless vocal texture":
                    self.assertIn("non-lexical vocal texture", prompt)
                else:
                    self.assertIn("No vocals. No lyrics.", prompt)

    def test_generate_pipeline_uses_mocked_model_outputs_when_available(self):
        os.environ["TTM_TEST_MODEL_CALLS"] = "1"
        result = app.generate_time_machine_mix(
            "1980s",
            "Synth-pop",
            "2000s",
            "Filtered disco house",
            "The Neon Signal Host",
            "Clean digital master",
            "nostalgic and warm",
            "English",
            "Best stability (English)",
            "Original micro-lyrics",
            "Night drive",
            1,
            777,
            False,
        )
        (
            final_path,
            music_path,
            intro_path,
            intro_status,
            _intro_text,
            lyrics_text,
            prompt,
            _card,
            status,
        ) = result[:9]
        self.assertTrue(Path(final_path).exists())
        self.assertTrue(Path(music_path).exists())
        self.assertTrue(Path(intro_path).exists())
        self.assertEqual(intro_status, "Spoken DJ intro generated.")
        self.assertIn("ACE-Step model call simulated", status)
        self.assertIn("Kokoro spoken-DJ model call simulated", status)
        self.assertIn("tiny-aya-global text model call simulated", status)
        self.assertIn("Lyrics:", prompt)
        self.assertGreaterEqual(len(lyrics_text.splitlines()), 2)


if __name__ == "__main__":
    unittest.main()
