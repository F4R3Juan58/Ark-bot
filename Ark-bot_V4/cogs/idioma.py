import discord
from discord.ext import commands
import gspread
from google.oauth2 import service_account
import asyncio

KEY = "credentials.json"
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

creds = service_account.Credentials.from_service_account_file(KEY, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open('Vouch Info').sheet1

class idioma(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.event
    async def on_member_join(self, member):
        print("Poniendo roles")
        user_id = member.id
        await self.idiomarol(member, user_id)
    
    ####    Asiganar Rol De Idioma Segun Id     ####

    @commands.event
    async def idiomarol(self, member, user_id):
        guild = member.guild if isinstance(member, discord.Member) else None
        role_name = None

        if user_id is not None:
            find_id = sheet.find(str(user_id))

            idioma = sheet.cell(find_id.row, 6).value

            idioma_roles = {
                "Spanish": "Spanish",
                "English": "English",
                "Chinese/Korean": "Chinese/Korean"
            }

            role_name = idioma_roles.get(idioma)

        if role_name:
            role = discord.utils.get(guild.roles, name=role_name)
            rolpete = discord.utils.get(guild.roles, name="petillos")
            if role:
                for existing_role in member.roles:
                    if existing_role.name in idioma_roles.values():
                        await member.remove_roles(existing_role) 
                await member.add_roles(role)
                await member.add_roles(rolpete)


def setup(bot):
    bot.add_cog(idioma(bot))
