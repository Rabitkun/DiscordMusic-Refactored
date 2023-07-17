from typing import Any, Optional, Type
import discord
from base.options import Options
from discord.ext import commands


class MusicBot(commands.Bot):
    options: Options = None

    async def setup_hook(self):
        await self.load_extension('cogs')