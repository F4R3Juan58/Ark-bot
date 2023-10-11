import discord
import config
from discord.ext import commands
import gspread
from google.oauth2 import service_account

creds = service_account.Credentials.from_service_account_file(config.KEY, scopes=config.SCOPES)
client = gspread.authorize(creds)

class quota(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_in_progress = False

    @commands.command()
    async def quota(self, ctx):
        if self.command_in_progress:
            return
        
        # Establecer la variable de estado a True
        self.command_in_progress = True
        try:
            try:
                sheet = client.open('Quota').sheet1
                # Guardar el ID del usuario
                user_name = ctx.author.name
                user_id = ctx.author.id
                user = self.bot.get_user(user_id) 
                # Buscar el ID en la hoja de cálculo y marcar como entregado
                cell = sheet.find(str(user_id))

                if cell:
                    sheet.update_cell(cell.row, 3, "✓")
                    await user.send("Tu quota ha sido marcada como entregada.")
                else:
                    await user.send("No se encontró tu ID en la lista.")

                # Enviar el mensaje a "quota-done"
                verification_channel = discord.utils.get(ctx.guild.text_channels, id=config.QUOTADONE)
                if verification_channel:
                    if ctx.message.attachments:
                        for attachment in ctx.message.attachments:
                            embed = discord.Embed(title="Verificación de Quota", color=0x00ff00)
                            embed.add_field(name="Discord Name:", value=user_name)
                            embed.add_field(name="Discord Id:", value=user_id)
                            embed.set_image(url=attachment.url)
                            message = await verification_channel.send(embed=embed)
                            await message.add_reaction('✅')
            except Exception as e:
                print(f"Error en el comando 'quota': {e}")
        finally:
            # Restablecer la variable de estado a False cuando el comando ha terminado
            self.command_in_progress = False

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            sheet = client.open('Quota').sheet1
            user_id = payload.user_id
            cell = sheet.find(str(user_id))
            
            # Manejar las reacciones en "quota-done"
            if payload.channel_id == config.QUOTADONE:  # Reemplaza con el ID de tu canal "quota-done"
                if payload.emoji.name == '✅':
                    message_id = payload.message_id
                    channel = self.bot.get_channel(payload.channel_id)  # Corregir aquí
                    message = await channel.fetch_message(message_id)
                    
                    # Contar las reacciones con el emoji '✅'
                    reaction = discord.utils.get(message.reactions, emoji='✅')
                    if reaction and reaction.count >= 2:
                        sheet.update_cell(cell.row, 4, "✓")  # Suponiendo que la columna de estado está en la tercera columna (C)
                        user = self.bot.get_user(user_id)  # Corregir aquí
                        await user.send("¡Tu quota ha sido verificada!")
        except Exception as e:
            print(f"Error en el evento 'on_raw_reaction_add': {e}")

async def setup(bot):
    await bot.add_cog(quota(bot))
