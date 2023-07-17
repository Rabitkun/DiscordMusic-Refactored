from base.options import Options
from base.bot import MusicBot
from discord import Intents
import discord
import os

options = Options("options.json")
options.load()

intents = Intents.all()
bot = MusicBot(command_prefix=options.opt_command_prefix, intents=intents)
bot.options = options

@bot.event
async def on_message(message: discord.Message):
    print(message.content)
    if message.content.startswith(options.opt_command_prefix) != True:
       return
    await bot.process_commands(message)

token = os.getenv("TOKEN")
bot.run(token=token, reconnect=True)