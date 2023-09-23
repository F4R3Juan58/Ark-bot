import discord
from discord.ext import commands, tasks
import gspread
from google.oauth2 import service_account
import config
import asyncio

creds = service_account.Credentials.from_service_account_file(config.KEY, scopes=config.SCOPES)
client = gspread.authorize(creds)
sheet = client.open('Vouch Info').sheet1

def admin_or_has_role(role_name):
    async def predicate(ctx):
        # Verificar si el usuario es un administrador o tiene el rol especificado
        if ctx.author.guild_permissions.administrator or any(role.name == role_name for role in ctx.author.roles):
            return True
        await ctx.send("No tienes permiso para usar este comando.")
        return False
    return commands.check(predicate)


class Vouch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.check_vote.start()

    @commands.command()
    @admin_or_has_role("Admin")
    async def vouch(self , ctx):
        while True:
            asyncio.sleep(60)
            with open(config.archivo_nombre, 'r') as archivo:
                uid = archivo.read().strip()

            cell = sheet.find(uid)

            if cell:
                siguiente_cell = sheet.cell(cell.row + 1, 2)
                if siguiente_cell.value is not None:
                    siguiente = siguiente_cell.value
                else:
                    print("saliendo del comando vouch")
                    break

                if siguiente != uid and siguiente is not None:
                    with open(config.archivo_nombre, 'w') as archivo:
                        archivo.write(siguiente)
                    print(siguiente)
                    await self.process_new_row(siguiente)


    @tasks.loop(seconds=60)
    async def check_vote(self):
        print("Comprobando votos")
        
        with open(config.archivo_vote_vouch, 'r') as file:
            lineas = file.readlines()
        
        for linea in lineas:
            mensaje_id = int(linea.strip())
            
            try:
                mensaje = await self.bot.get_channel(config.VOUCH).fetch_message(mensaje_id)
                embed = mensaje.embeds[0]
                Name = None
                id = None
                for field in embed.fields:
                    if field.name == "Discord Id:":
                        id = field.value
                        break
                for field in embed.fields:
                    if field.name == "Discord Name:":
                        Name = field.value
                        break
                print(id)
                print(Name)
                reacciones = mensaje.reactions
                print(reacciones)
                for reaccion in reacciones:
                    if reaccion.count >= 2:
                        try:
                            user = await self.bot.fetch_user(int(id))
                            mensaje = config.invite
                            await user.send(mensaje)
                            # Eliminar el ID de la lista después de enviar el mensaje
                            lineas.remove(linea)
                            with open(config.archivo_vote_vouch, 'w') as file:
                                file.writelines(lineas)
                        except:
                            chanel_id = config.sininv  # Reemplaza esto con el ID del canal que deseas notificar
                            error_message = f"Se produjo un error al enviar mensaje al usuario con Nombre de dc: {Name} ."
                            print(error_message)
                            lineas.remove(linea)
                            with open(config.archivo_vote_vouch, 'w') as file:
                                file.writelines(lineas)
                            canal = self.bot.get_channel(chanel_id)
                            if canal:
                                await canal.send(error_message)
                            return

            except:
                print("Error al ejecutar la comprobación de votos")
                return


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == config.VOUCH:
            print(f'ID del mensaje almacenado: {message.id}')
            with open(config.archivo_vote_vouch, 'w') as archivo:
                        archivo.write(f'{message.id}\n')
            await self.check_vote()
        else:
            await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def process_new_row(self, uid):
        channel = self.bot.get_channel(config.VOUCH)
        siguiente = sheet.find(uid)

        if siguiente:
            discordid = sheet.cell(siguiente.row, 2).value
            plataforma = sheet.cell(siguiente.row, 3).value
            id = sheet.cell(siguiente.row, 4).value
            edad = sheet.cell(siguiente.row, 5).value
            idioma = sheet.cell(siguiente.row, 6).value
            pretribe1 = sheet.cell(siguiente.row, 7).value
            pretribe2 = sheet.cell(siguiente.row, 8).value
            autenticacion = sheet.cell(siguiente.row, 9).value
            vouched = sheet.cell(siguiente.row, 10).value
            dcname = sheet.cell(siguiente.row, 11).value

            embed = discord.Embed(title="New Vouch")
            embed.add_field(name="Discord Name: ", value=str(dcname), inline=False)
            embed.add_field(name="Discord Id: ", value=str(discordid), inline=False)
            embed.add_field(name="Platform: ", value=str(plataforma), inline=False)
            embed.add_field(name="Steam ID / Epic Name / Xbox ID / Psn Name: ", value=str(id), inline=False)
            embed.add_field(name="Age: ", value=str(edad), inline=False)
            embed.add_field(name="Languages: ", value=str(idioma), inline=False)
            embed.add_field(name="Previous Tribes Ark 1: ", value=str(pretribe1), inline=False)
            embed.add_field(name="Previous Tribes ASA: ", value=str(pretribe2), inline=False)
            embed.add_field(name="2FA: ", value=str(autenticacion), inline=False)
            embed.add_field(name="Vouched by: ", value=str(vouched), inline=False)

            tick_emoji = "✅"

            message = await channel.send(embed=embed)
            await message.add_reaction(tick_emoji)

async def setup(bot):
    await bot.add_cog(Vouch(bot))