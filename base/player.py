import discord
from discord import VoiceChannel, VoiceClient, TextChannel
from enum import Enum

class PlayerState(Enum):
    WAITING = 0
    PLAYING = 1
    PAUSED = 2

class Player():
    def __init__(self, voice_channel: VoiceChannel, ffmpeg_options: dict[str, any]) -> None:
        self.vchannel = voice_channel
        self.text_channel: TextChannel = None
        self.vclient: VoiceClient = None
        self.ffmpeg_options: dict[str, any] = ffmpeg_options
        #list with audio titles and urls
        self.queue: list[tuple[str, str]] = []

    async def print_info_to_channel(self, text: str) -> None:
        if self.text_channel == None:
            return
        await self.text_channel.send(text)

    def state(self) -> PlayerState:
        if self.vclient == None:
            return  PlayerState.WAITING
        if self.vclient.is_connected() == False:
            return  PlayerState.WAITING
        if self.vclient.is_paused():
            return PlayerState.PAUSED
        if self.vclient.is_playing():
            return PlayerState.PLAYING
        return PlayerState.WAITING

    def add_to_queue(self, title: str, sound_url: str) -> tuple[bool, str]:
        self.queue.append((title, sound_url))
        return (True, f"Song {title} added to queue.")

    def pause(self) -> tuple[bool, str]:
        if self.state() == PlayerState.WAITING:
            return (False, "Bot is not playing.")
        self.vclient.pause()
        return (True, "Bot paused.")

    def resume(self) -> tuple[bool, str]:
        if self.state() != PlayerState.PAUSED:
            return (False, "Bot is not paused.")
        self.vclient.resume()
        return (True, "Bot continues to play.")

    async def connect_to_channel(self) -> tuple[bool, str]:
        if self.vclient == None or not self.vclient.is_connected():
            self.vclient = await self.vchannel.connect()
        else:
            await self.vclient.move_to(self.vchannel)
        return (True, "Bot connected to channel.")

    def play_next_sound(self) -> tuple[bool, str] | None:
        if self.vclient.is_playing(): 
            self.vclient.stop()
        if len(self.queue) == 0:
            return (False, "Sound queue is empty.")
        sound_obj = self.queue.pop(0)
        sound_title = sound_obj[0]
        sound_url = sound_obj[1]
        #self.print_info_to_channel(f'Now playing {sound_title}.')
        self.vclient.play(discord.FFmpegPCMAudio(sound_url, **self.ffmpeg_options), after=lambda e: self.play_next_sound())

    async def play(self) -> None:
        if len(self.queue) == 0:
            return (False, "Sound queue is empty.")
        if self.state() == PlayerState.PLAYING:
            return (False, "Player is already active.")
        if self.state() == PlayerState.PAUSED:
            return self.resume()
        await self.connect_to_channel()
        self.play_next_sound()
    
    async def skip(self) -> None:
        if len(self.queue) == 0:
            self.vclient.stop()
            return
        self.play_next_sound()
    
    async def clear(self):
        if self.vclient != None and self.vclient.is_playing():
            self.vclient.stop()
        self.queue = []
        await self.print_info_to_channel("Music queue cleared.")
    
    async def leave(self):
        await self.clear()
        await self.vclient.disconnect()
        await self.print_info_to_channel("Bot leaved the channel.")