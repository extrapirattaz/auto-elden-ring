"""Lazy streaming playback; no display initialization or whole-file decoding."""
import os
from pathlib import Path


class Music:
    def __init__(self):
        self.opened=False
        self.path=None
        self.paused=False
        self.backend=None

    def play(self,path):
        path=Path(path)
        if not path.is_file() or path.suffix.lower() not in (".mp3",".wav",".flac",".ogg"):
            raise ValueError("Choose an existing MP3, WAV, FLAC or OGG file.")
        os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT","1")
        import pygame.mixer as mixer
        import pygame
        try:
            if not mixer.get_init():
                mixer.init(buffer=1024)
            self.backend=mixer
            if self.opened and self.path==path.resolve() and self.paused:
                mixer.music.unpause()
            elif not self.opened or self.path!=path.resolve():
                mixer.music.load(str(path.resolve()))
                mixer.music.play(loops=-1)
                self.path=path.resolve()
            self.opened=True
            self.paused=False
        except (pygame.error,OSError) as exc:
            self.close()
            raise ValueError(f"Cannot decode or play this audio file: {exc}") from exc

    def pause(self):
        if self.opened:
            self.backend.music.pause()
            self.paused=True

    def close(self):
        if self.backend is not None and self.backend.get_init():
            try:
                self.backend.music.stop()
                self.backend.music.unload()
                self.backend.quit()
            finally:
                self.opened=False
                self.paused=False
                self.path=None
