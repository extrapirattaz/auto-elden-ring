"""Optional local MP3/WAV playback through Windows MCI; no decoder dependency."""
import ctypes
import os
from pathlib import Path
from uuid import uuid4


class Music:
    def __init__(self):
        self.alias="auto_elden_"+uuid4().hex
        self.opened=False

    def command(self,text):
        if os.name!="nt":
            raise ValueError("Music playback requires Windows.")
        code=ctypes.windll.winmm.mciSendStringW(text,None,0,None)
        if code:
            message=ctypes.create_unicode_buffer(512)
            ctypes.windll.winmm.mciGetErrorStringW(code,message,512)
            raise ValueError(message.value)

    def play(self,path):
        path=Path(path)
        if not path.is_file() or path.suffix.lower() not in (".mp3",".wav"):
            raise ValueError("Choose an existing local MP3 or WAV file.")
        self.close()
        self.command(f'open "{path.resolve()}" type mpegvideo alias {self.alias}')
        self.opened=True
        self.command(f"play {self.alias} from 0 repeat")

    def pause(self):
        if self.opened:
            self.command(f"pause {self.alias}")

    def close(self):
        if self.opened:
            try:
                self.command(f"close {self.alias}")
            finally:
                self.opened=False
