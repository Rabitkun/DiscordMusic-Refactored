from . import music

from discord.ext import commands
from base.bot import MusicBot
from base.options import Options

async def setup(bot: MusicBot):
    await bot.add_cog(music.MusicCog(bot, bot.options.opt_yt_formats, bot.options.opt_ydl, bot.options.opt_ffmpeg))
