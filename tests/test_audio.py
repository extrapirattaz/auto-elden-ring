"""Decode generated silence across formats without touching user music."""

import os
from pathlib import Path
import shutil
import tempfile
import time
import unittest
from unittest.mock import patch
from auto_elden_ring.audio import Music
from auto_elden_ring.core import resource_path


class StreamingAudio(unittest.TestCase):
    def test_formats_unicode_pause_resume_and_release(self):
        with patch.dict(os.environ, {"SDL_AUDIODRIVER": "dummy"}):
            music = Music()
            try:
                for fixture in resource_path("assets/audio-check").iterdir():
                    if fixture.suffix not in (".mp3", ".wav", ".flac", ".ogg", ".opus"):
                        continue
                    with self.subTest(format=fixture.name):
                        music.play(fixture)
                        self.assertTrue(music.backend.music.get_busy())
                        time.sleep(0.025)
                        music.pause()
                        position = music.backend.music.get_pos()
                        self.assertTrue(music.paused)
                        music.play(fixture)
                        self.assertFalse(music.paused)
                        self.assertGreaterEqual(music.backend.music.get_pos(), position)
                        music.close()
                        self.assertIsNone(music.backend.get_init())
                with tempfile.TemporaryDirectory() as folder:
                    path = Path(folder) / "Musique été 月.mp3"
                    shutil.copyfile(resource_path("assets/audio-check/variable.mp3"), path)
                    music.play(path)
                    self.assertTrue(music.opened)
                    music.close()
            finally:
                music.close()

    def test_decode_failure_releases_device_and_allows_next_file(self):
        with patch.dict(os.environ, {"SDL_AUDIODRIVER": "dummy"}):
            music = Music()
            try:
                with tempfile.TemporaryDirectory() as folder:
                    path = Path(folder) / "invalid.mp3"
                    path.write_bytes(b"Not an audio stream.")
                    with self.assertRaises(ValueError):
                        music.play(path)
                    self.assertFalse(music.opened)
                    self.assertIsNone(music.backend.get_init())
                music.play(resource_path("assets/audio-check/pcm16.wav"))
                self.assertTrue(music.opened)
            finally:
                music.close()
