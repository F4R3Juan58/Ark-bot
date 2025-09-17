import config
import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix="!!", intents=discord.Intents.all())


####    Inicio del Bot      ####

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')
    await load_extensions()

async def load_extensions():
    print("Cargando extensiones")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await bot.load_extension(f"cogs.{filename[:-3]}")
    print("Extensiones cargadas.")
    
#### Token ####

bot.run(config.TOKEN) 