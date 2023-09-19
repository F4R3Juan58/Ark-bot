import discord
from discord.ext import commands, tasks
import gspread
from google.oauth2 import service_account
import config


mensajes_en_canal = []

creds = service_account.Credentials.from_service_account_file(config.KEY, scopes=config.SCOPES)
client = gspread.authorize(creds)
sheet = client.open('Vouch Info').sheet1

class Vouch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_for_new_rows.start()
        self.check_vote.start()

    @tasks.loop(minutes=5)
    async def check_for_new_rows(self):
        print("Revisando nuevas filas")

        with open(config.archivo_nombre, 'r') as archivo:
            uid = archivo.read().strip()

        cell = sheet.find(uid)

        if cell:
            siguiente_cell = sheet.cell(cell.row + 1, 2)
            if siguiente_cell.value is not None:
                siguiente = siguiente_cell.value
            else:
                return

            if siguiente != uid and siguiente is not None:
                with open(config.archivo_nombre, 'w') as archivo:
                    archivo.write(siguiente)
                print(siguiente)
                await self.process_new_row(siguiente)

    @check_for_new_rows.before_loop
    async def before_check_for_new_rows(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=60)
    async def check_vote(self):
        print("Comprobando votos")
        for mensaje_id in mensajes_en_canal[:]:
            try:
                mensaje = await self.bot.get_channel(config.VOUCH).fetch_message(mensaje_id)
                embed = mensaje.embeds[0]
                id = None
                for field in embed.fields:
                    if field.name == "Discord Id:":
                        id = field.value
                        break
                print(id)
                reacciones = mensaje.reactions
                print(reacciones)
                for reaccion in reacciones:
                    if reaccion.count >= 2:
                        user = await self.bot.fetch_user(int(id))
                        mensaje = "https://discord.gg/hxv3vcmu"
                        if mensaje_id in mensajes_en_canal:
                            mensajes_en_canal.remove(mensaje_id)
                            await user.send(mensaje)
            except discord.NotFound:
                continue

    @check_vote.before_loop
    async def before_check_vote(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == config.VOUCH:
            print(f'ID del mensaje almacenado: {message.id}')
            mensajes_en_canal.append(message.id)
            await self.check_vote()
        else:
            await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.id in mensajes_en_canal:
            mensajes_en_canal.remove(message.id)

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

def setup(bot):
    bot.add_cog(Vouch(bot))
