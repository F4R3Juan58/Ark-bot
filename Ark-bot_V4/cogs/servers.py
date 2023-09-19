import discord
import config
from discord.ext import commands, tasks
import gspread
from google.oauth2 import service_account

creds = service_account.Credentials.from_service_account_file(config.KEY, scopes=config.SCOPES)
client = gspread.authorize(creds)
previous_messages = {"TheIsland": None, "Scorchead": None}


class servers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @tasks.loop(hours=24)
    async def update_embed(self):
        TheIsland = client.open('Servers').worksheet('TheIsland')
        Scorchead = client.open('Servers').worksheet('Scorchead')
        global previous_messages

        print("Actualizando embeds...")
        
        # Obtener datos de la hoja de cálculo TheIsland
        isla = TheIsland.get_all_values()
        
        if isla==None:
            return
        elif isla!=None:
            # Crear un nuevo embed para TheIsland
            embed_isla = discord.Embed(title="Actualización Diaria TheIsland", color=0x00ff00)

            # Obtener valores de la primera columna y sus correspondientes columnas de valores
            for row in isla:
                field = row[0]
                values = row[1:]
                value_str = " , ".join(values)  # Concatenar los valores en un solo mensaje

                embed_isla.add_field(name=field, value=value_str, inline=False)

            # Obtener el canal de actualización
            update_channel = discord.utils.get(self.get_all_channels(), name=config.servers_chanel_name)

            # Borrar el mensaje anterior de TheIsland si existe
            if previous_messages["TheIsland"]:
                await previous_messages["TheIsland"].delete()

            # Enviar el nuevo embed de TheIsland al canal y guardar una referencia al mensaje
            previous_messages["TheIsland"] = await update_channel.send(embed=embed_isla)
        
        # Obtener datos de la hoja de cálculo Scorchead
        se = Scorchead.get_all_values()

        if se==None:
            return
        elif se!=None:
            # Crear un nuevo embed para Scorchead
            embed_se = discord.Embed(title="Actualización Diaria Scorchead", color=0x0000ff)

            # Obtener valores de la primera columna y sus correspondientes columnas de valores
            for row in se:
                field = row[0]
                values = row[1:]
                value_str = " , ".join(values)  # Concatenar los valores en un solo mensaje

                embed_se.add_field(name=field, value=value_str, inline=False)

            # Borrar el mensaje anterior de Scorchead si existe
            if previous_messages["Scorchead"]:
                await previous_messages["Scorchead"].delete()

            # Enviar el nuevo embed de Scorchead al canal y guardar una referencia al mensaje
            previous_messages["Scorchead"] = await update_channel.send(embed=embed_se)


def setup(bot):
    bot.add_cog(servers(bot))
