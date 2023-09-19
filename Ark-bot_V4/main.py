import config
import discord
from discord.ext import commands, tasks

bot = commands.Bot(command_prefix="!!", intents=discord.Intents.all())
previous_messages = {"TheIsland": None, "Scorchead": None}

####    Modulos     ####

bot.load_extension("cogs.bps")
bot.load_extension("cogs.costbp")
bot.load_extension("cogs.vote")
bot.load_extension("cogs.vouch")
bot.load_extension("cogs.idioma")
bot.load_extension("cogs.quota")
bot.load_extension("cogs.servers")

####    Inicio del Bot      ####

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')

#### Token ####

bot.run(config.TOKEN)  # Asegúrate de definir TOKEN en tu archivo de configuración
