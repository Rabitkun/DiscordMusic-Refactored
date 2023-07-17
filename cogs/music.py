from ast import alias
import discord
from discord.ext import commands
import os
from base.player import Player, PlayerState
from yt_dlp import YoutubeDL
from discord.ext.commands.context import Context

class MusicCog(commands.Cog):
    def __init__(self, bot: commands.Bot, yt_formats: list[str], ydl_opts: dict[str, any], ffmpeg_opts: dict[str, str]):
        self.bot: commands.Bot = bot
        self.yt_format_ids = yt_formats
        self.YDL_OPTIONS = ydl_opts
        self.FFMPEG_OPTIONS = ffmpeg_opts
        #dictiony with guild.id as key and tuple[Guild, Player] as value
        self.players: dict[int, (discord.Guild, Player)] = {}

    def configure_info_from_response(self, ydl_info: dict[str, any]) -> dict[str, str]:
        result = {}
        info = ydl_info['entries'][0]
        result["id"] = info["id"]
        result["title"] = info["title"]
        formats = info["formats"]
        for format in formats:
            format_id = format["format_id"]
            if format_id in self.yt_format_ids or format_id == "audio only":
                result["source"] = format["url"]
                break
        return result

     #searching the item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                full_info = ydl.extract_info("ytsearch:%s" % item, download=False)
                info = self.configure_info_from_response(full_info)
            except Exception as ex:
                print("ERROR:", ex.__traceback__)
                return False

        return info
    def get_player(self, guild_id: int) -> Player:
        if (guild_id in self.players) == False:
            return None
        player: Player = self.players[guild_id][1]
        return player
    @commands.command(name="play", aliases=["p","playing"], help="Plays a selected song from youtube")
    async def play(self, ctx: Context, *args):
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("Connect to a voice channel!")
            return

        if (ctx.guild.id in self.players) == False:
            self.players[ctx.guild.id] = (ctx.guild, Player(voice_channel, self.FFMPEG_OPTIONS))
        query = " ".join(args)
        song = self.search_yt(query)
        if type(song) == type(True):
            await ctx.send("Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.")
            return
        player: Player = self.get_player(ctx.guild.id)
        player.text_channel = ctx.channel
        message = player.add_to_queue(song["title"], song["source"])
        await ctx.send(message[1])
        if player.state() == PlayerState.PLAYING:
            return
        await player.play()
    
    @commands.command(name="skip", aliases=["s"], help="Skips the current song being played")
    async def skip(self, ctx: Context):
        player: Player = self.get_player(ctx.guild.id)
        await player.skip()

    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        player: Player = self.get_player(ctx.guild.id)
        if player.state == PlayerState.PLAYING:
            player.pause()
        elif player.state == PlayerState.PAUSED:
            player.resume()

    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx: Context):
        player: Player = self.get_player(ctx.guild.id)
        titles: list = []
        for i in range(len(player.queue)):
            titles.append(f'{i+1}. {player.queue[0][0]}')
        await ctx.send("\n".join(titles))

    @commands.command(name="clear", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        player: Player = self.get_player(ctx.guild.id)
        await player.clear()

    @commands.command(name="leave", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
    async def leave(self, ctx):
        player: Player = self.get_player(ctx.guild.id)
        await player.leave()
    
