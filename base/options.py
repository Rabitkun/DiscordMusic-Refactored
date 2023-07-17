import json

class Options():
    
    def __init__(self, filepath: str) -> None:
        self.filepath: str = filepath
        #options
        self.opt_command_prefix: str = None
        self.opt_yt_formats: list[str] = None
        self.opt_ydl: dict[str, any] = None
        self.opt_ffmpeg: dict[str, str] = None

    def load(self) -> None:
        with open(self.filepath, "r") as file:
            options = json.load(file)
            self.opt_command_prefix: str = options["command_prefix"]
            self.opt_yt_formats: list[str] = options["yt_formats"]
            self.opt_ydl: dict[str, any] = options["ydl"]
            self.opt_ffmpeg: dict[str, str] = options["ffmpeg"]