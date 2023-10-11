import discord
from discord.ext import commands
import gspread
import config
from google.oauth2 import service_account

creds = service_account.Credentials.from_service_account_file(config.KEY, scopes=config.SCOPES)
client = gspread.authorize(creds)
sheet = client.open('Vouch Info').sheet1

def admin_or_has_role(role_name):
    async def predicate(ctx):
        await ctx.message.delete()
        # Verificar si el usuario es un administrador o tiene el rol especificado
        if ctx.author.guild_permissions.administrator or any(role.name == role_name for role in ctx.author.roles):
            return True
        await ctx.send("No tienes permiso para usar este comando.")
        return False
    return commands.check(predicate)

class Vouchby(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_in_progress = False

    @commands.command()
    @admin_or_has_role("Admin")
    async def vby(self, ctx, user: discord.Member):
        if self.command_in_progress:
            return
        # Establecer la variable de estado a True
        self.command_in_progress = True
        try:
            user_id = str(user.id)
            userid = sheet.find(str(user_id))
            namedc = sheet.cell(userid.row, 11).value
            vouchedby = sheet.cell(userid.row, 10).value
            print(vouchedby)
            canal = self.bot.get_channel(config.COMANDOSADMIN)
            await canal.send(f"El jugador {namedc} ha sido vouched by: {vouchedby}")
        finally:
           self.command_in_progress = False 

async def setup(bot):
    await bot.add_cog(Vouchby(bot))
