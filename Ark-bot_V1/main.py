import config
import discord
import asyncio
from discord.ext import commands, tasks
import gspread
from google.oauth2 import service_account

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
KEY = "credentials.json"
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
mensajes_en_canal = []

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')
    check_vote.start()
    await check_for_new_rows()
    

@bot.event
async def on_member_join(member):
    print("Poniendo roles")
    user_id = member.id
    await idiomarol(member, user_id)

async def check_for_new_rows():
    print("Revisando nuevas filas")
    creds = service_account.Credentials.from_service_account_file(KEY, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open('Vouch Info').sheet1

    last_processed_row = 1

    while True:
        all_rows = sheet.get_all_values()
        if len(all_rows) > last_processed_row:
            new_row = all_rows[-1]
            print(new_row)
            await process_new_row(new_row)
            last_processed_row = len(all_rows)
        await asyncio.sleep(1)

async def process_new_row(new_row):
    channel = bot.get_channel(config.VOUCH)  # Debes definir VOUCH en tu archivo de configuración

    if len(new_row) >= 10:  # Asegurarse de que la fila tenga suficientes columnas
        discordid = new_row[1]
        plataforma = new_row[2]
        id = new_row[3]
        edad = new_row[4]
        idioma = new_row[5]
        pretribe1 = new_row[6]
        pretribe2 = new_row[7]
        autenticacion = new_row[8]
        vouched = new_row[9]

        embed = discord.Embed(title="New Vouch")
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
        x_emoji = "❌"

        message = await channel.send(embed=embed)
        await message.add_reaction(tick_emoji)
        await message.add_reaction(x_emoji)

async def idiomarol(member, user_id):
    guild = member.guild if isinstance(member, discord.Member) else None
    role_name = None

    if user_id is not None:
        creds = service_account.Credentials.from_service_account_file(KEY, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open('Vouch Info').sheet1
        server_row = None
        all_rows = sheet.get_all_values()
        x = 1
        while x < len(all_rows):
            if len(all_rows[x]) > 1:
                ids = all_rows[x][1]
                if ids == str(user_id):
                    server_row = all_rows[x]
                    break
            x += 1

        idioma = server_row[5]
        # Mapeo de idiomas a roles
        idioma_roles = {
            "Spanish": "Spanish",
            "English": "English",
            "Chinese/Korean": "Chinese/Korean"
        }

        # Obtener el nombre del rol correspondiente al idioma
        role_name = idioma_roles.get(idioma)
    if role_name:
        # Obtener el rol correspondiente al nombre
        role = discord.utils.get(guild.roles, name=role_name)
        rolpete = discord.utils.get(guild.roles, name="petillos")
        if role:
            # Verificar si el usuario ya tiene un rol de idioma
            for existing_role in member.roles:
                if existing_role.name in idioma_roles.values():
                    await member.remove_roles(existing_role)  # Eliminar el rol existente
            # Agregar el nuevo rol
            await member.add_roles(role)
            await member.add_roles(rolpete)

@bot.event
async def on_message(message):
    if message.channel.id != config.VOUCH:  # Debes definir VOUCH en tu archivo de configuración
        return

    mensajes_en_canal.append(message.id)
    print(f'ID del mensaje almacenado: {message.id}')

@tasks.loop(seconds=10)
async def check_vote():
    print("Comprobando votos")
    for mensaje_id in mensajes_en_canal[:]:  # Usamos una copia [:] para evitar problemas al eliminar elementos
        try:
            mensaje = await bot.get_channel(config.VOUCH).fetch_message(mensaje_id)
            embed = mensaje.embeds[0]
            id = None
            for field in embed.fields:
                if field.name == "Discord Id:":
                    id = field.value  # Tomar solo el valor del campo
                    break
            print(id)
            reacciones = mensaje.reactions
            for reaccion in reacciones:
                if reaccion.count >= 1:  # Verificar si una reacción tiene al menos 1 voto
                    user = await bot.fetch_user(int(id))  # Convertir el valor a un entero antes de usarlo como ID de usuario
                    mensaje = "https://discord.gg/hxv3vcmu"
                    if mensaje_id in mensajes_en_canal:  # Verificar si el mensaje ID todavía está en la lista
                        mensajes_en_canal.remove(mensaje_id)  # Eliminar el mensaje ID de la lista
                        await user.send(mensaje)
        except discord.NotFound:
            continue



bot.run(config.TOKEN)  # Asegúrate de definir TOKEN en tu archivo de configuración
