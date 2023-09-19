import discord
from discord.ext import commands
import gspread
from google.oauth2 import service_account
import asyncio

class vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def vote(self,ctx, pregunta, opciones: str, duracion: int):
        # Verificar si el autor del mensaje es un administrador
        if ctx.author.guild_permissions.administrator:
            opciones = opciones.split('|')
            if duracion <= 0:
                await ctx.send("La duración de la votación debe ser mayor que cero.")
                return

            if len(opciones) < 2 or len(opciones) > 9:
                await ctx.send("La votación debe tener entre 2 y 9 opciones.")
                return

            embed = discord.Embed(title="Votación", description=pregunta, color=discord.Color.blue())

            for i, opcion in enumerate(opciones):
                embed.add_field(name=opcion, value=" ", inline=True)

            message = await ctx.send(embed=embed)
            
            for i in range(1, len(opciones) + 1):
                await message.add_reaction(f"{i}\N{COMBINING ENCLOSING KEYCAP}")

            for i in range(duracion):
                await asyncio.sleep(1)
                tiempo_restante = duracion - i
                if tiempo_restante % 60 == 0:
                    minutos = tiempo_restante // 60
                    await message.edit(content=f'Tiempo restante: {minutos} minutos')
                else:
                    await message.edit(content=f'Tiempo restante: {tiempo_restante} segundos')

            for i in range(1, len(opciones) + 1):
                await message.add_reaction(f"{i}\N{COMBINING ENCLOSING KEYCAP}")

            message = await ctx.channel.fetch_message(message.id)
            results = {opcion: reaction.count for opcion, reaction in zip(opciones, message.reactions)}

            ganador = max(results, key=results.get)
            await ctx.send(f'El ganador es: {ganador}')
        else:
            await ctx.send("Solo los administradores pueden ejecutar este comando.")

def setup(bot):
    bot.add_cog(vote(bot))
