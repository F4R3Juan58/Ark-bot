import discord
from discord.ext import commands
import gspread
from google.oauth2 import service_account
import config

creds = service_account.Credentials.from_service_account_file(config.KEY, scopes=config.SCOPES)
client = gspread.authorize(creds)
Admin = client.open('Vouch Info').worksheet('Admin')
SoftAdmin = client.open('Vouch Info').worksheet('SoftAdmin')
Member = client.open('Vouch Info').worksheet('Member')
NewMember = client.open('Vouch Info').worksheet('NewMember')

def admin_or_has_role(role_name):
    async def predicate(ctx):
        # Verificar si el usuario es un administrador o tiene el rol especificado
        if ctx.author.guild_permissions.administrator or any(role.name == role_name for role in ctx.author.roles):
            return True
        await ctx.send("No tienes permiso para usar este comando.")
        return False
    return commands.check(predicate)

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_in_progress = False  # Variable de estado
    
    @commands.command()
    @admin_or_has_role("Admin")
    async def ar(self, ctx, user: discord.Member, role_name):
        # Verificar si el comando ya se está ejecutando
        if self.command_in_progress:
            return
        
        # Establecer la variable de estado a True
        self.command_in_progress = True
        
        try:
            user_id = str(user.id)
            if role_name.lower() == "admin" and discord.utils.get(user.roles, name="Admin") is None:
                await user.add_roles(discord.utils.get(ctx.guild.roles, name="Admin"))
                Admin.append_row([user.name, user_id])
            elif role_name.lower() == "softadmin" and discord.utils.get(user.roles, name="SoftAdmin") is None:
                await user.add_roles(discord.utils.get(ctx.guild.roles, name="SoftAdmin"))
                SoftAdmin.append_row([user.name, user_id])
            elif role_name.lower() == "member" and discord.utils.get(user.roles, name="Member") is None:
                await user.add_roles(discord.utils.get(ctx.guild.roles, name="Member"))
                Member.append_row([user.name, user_id])
            elif role_name.lower() == "newmember" and discord.utils.get(user.roles, name="NewMember") is None:
                await user.add_roles(discord.utils.get(ctx.guild.roles, name="NewMember"))
                NewMember.append_row([user.name, user_id])
            else:
                await ctx.send(f"{user.mention} already has the {role_name} role or {role_name} is not a valid role")
            await ctx.message.delete()

        finally:
            # Restablecer la variable de estado a False cuando el comando ha terminado
            self.command_in_progress = False

    @commands.command()
    @admin_or_has_role("Admin")
    async def rr(self, ctx, user: discord.Member, role_name):
        # Verificar si el comando ya se está ejecutando
        if self.command_in_progress:
            return
        
        # Establecer la variable de estado a True
        self.command_in_progress = True
        
        try:
            user_id = str(user.id)
            if role_name.lower() == "admin" and discord.utils.get(user.roles, name="Admin") is not None:
                await user.remove_roles(discord.utils.get(ctx.guild.roles, name="Admin"))
                admin_cell = Admin.find(user_id)
                if admin_cell:
                    admin_row = admin_cell.row
                    Admin.delete_row(admin_row)
            elif role_name.lower() == "softadmin" and discord.utils.get(user.roles, name="SoftAdmin") is not None:
                await user.remove_roles(discord.utils.get(ctx.guild.roles, name="SoftAdmin"))
                softadmin_cell = SoftAdmin.find(user_id)
                if softadmin_cell:
                    softadmin_row = softadmin_cell.row
                    SoftAdmin.delete_row(softadmin_row)
            elif role_name.lower() == "member" and discord.utils.get(user.roles, name="Member") is not None:
                await user.remove_roles(discord.utils.get(ctx.guild.roles, name="Member"))
                member_cell = Member.find(user_id)
                if member_cell:
                    member_row = member_cell.row
                    Member.delete_row(member_row)
            elif role_name.lower() == "newmember" and discord.utils.get(user.roles, name="NewMember") is not None:
                await user.remove_roles(discord.utils.get(ctx.guild.roles, name="NewMember"))
                newmember_cell = NewMember.find(user_id)
                if newmember_cell:
                    newmember_row = newmember_cell.row
                    NewMember.delete_row(newmember_row)
            else:
                await ctx.send(f"{user.mention} does not have the {role_name} role or {role_name} is not a valid role")
            await ctx.message.delete()
        finally:
            # Restablecer la variable de estado a False cuando el comando ha terminado
            self.command_in_progress = False


async def setup(bot):
    await bot.add_cog(Roles(bot))
