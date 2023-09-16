import config
import discord
import asyncio
from discord.ext import commands, tasks
import gspread
from google.oauth2 import service_account

####    Variables       ####

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
KEY = "credentials.json"
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
mensajes_en_canal = []
creds = service_account.Credentials.from_service_account_file(KEY, scopes=SCOPES)
client = gspread.authorize(creds)
previous_messages = {"TheIsland": None, "Scorchead": None}

####    Inicio del Bot      ####

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')
    check_vote.start()
    update_embed.start()
    await check_for_new_rows()
    
####    Cuando los Usuarios Entran      ####

@bot.event
async def on_member_join(member):
    print("Poniendo roles")
    user_id = member.id
    await idiomarol(member, user_id)

####    Verificar Los Nuevos Vouchs      ####

@bot.event
async def check_for_new_rows():
    print("Revisando nuevas filas")
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

####    Procesar Los Nuevos Vouchs      ####

@bot.event
async def process_new_row(new_row):
    channel = bot.get_channel(config.VOUCH) 

    if len(new_row) >= 10:
        discordid = new_row[1]
        plataforma = new_row[2]
        id = new_row[3]
        edad = new_row[4]
        idioma = new_row[5]
        pretribe1 = new_row[6]
        pretribe2 = new_row[7]
        autenticacion = new_row[8]
        vouched = new_row[9]
        dcname = new_row[10]

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

####    Asiganar Rol De Idioma Segun Id     ####

@bot.event
async def idiomarol(member, user_id):
    guild = member.guild if isinstance(member, discord.Member) else None
    role_name = None

    if user_id is not None:
        sheet = client.open('Vouch Info').sheet1
        find_id = sheet.find(str(user_id))

        idioma = sheet.cell(find_id.row, 2).value

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

####    Revisar Los Mensajes En Canal De Vouch      ####

@bot.event
async def on_message(message):
    if message.channel.id != config.VOUCH:  # Debes definir VOUCH en tu archivo de configuración
        return

    mensajes_en_canal.append(message.id)
    print(f'ID del mensaje almacenado: {message.id}')

####    Revisar Los Votos Del Canal De Vouch        ####

@tasks.loop(seconds=60)
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
            print(reacciones)
            for reaccion in reacciones:
                if reaccion.count >= 2:  # Verificar si una reacción tiene al menos 1 voto
                    user = await bot.fetch_user(int(id))  # Convertir el valor a un entero antes de usarlo como ID de usuario
                    mensaje = "https://discord.gg/hxv3vcmu"
                    if mensaje_id in mensajes_en_canal:  # Verificar si el mensaje ID todavía está en la lista
                        mensajes_en_canal.remove(mensaje_id)  # Eliminar el mensaje ID de la lista
                        await user.send(mensaje)
        except discord.NotFound:
            continue

####    Enviar Quota Con Imagen     ####

@bot.command()
async def quota(ctx):
    sheet = client.open('Quota').sheet1
    # Guardar el ID del usuario
    user_name = ctx.author.name
    user_id = ctx.author.id
    user = bot.get_user(user_id)
    # Buscar el ID en la hoja de cálculo y marcar como entregado
    cell = sheet.find(str(user_id))

    if cell:
        sheet.update_cell(cell.row, 2, "Entregado")
        await user.send("Tu quota ha sido marcada como entregada.")
    else:
        await user.send("No se encontró tu ID en la lista.")

    # Enviar el mensaje a "quota-done"
    verification_channel = discord.utils.get(ctx.guild.text_channels, name='quota-done')
    if verification_channel:
        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                embed = discord.Embed(title="Verificación de Quota", color=0x00ff00)
                embed.add_field(name="Discord Name:", value=user_name)
                embed.add_field(name="Discord Id:", value=user_id)
                embed.set_image(url=attachment.url)
                message = await verification_channel.send(embed=embed)
                await message.add_reaction('✅')

####    Confirmar Quota     ####

@bot.event
async def on_raw_reaction_add(payload):
    sheet = client.open('Quota').sheet1
    user_id = payload.user_id
    cell = sheet.find(str(user_id))
    
    # Manejar las reacciones en "quota-done"
    if payload.channel_id == config.QUOTADONE:  # Reemplaza con el ID de tu canal "quota-done"
        if payload.emoji.name == '✅':
            message_id = payload.message_id
            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(message_id)
            
            # Contar las reacciones con el emoji '✅'
            reaction = discord.utils.get(message.reactions, emoji='✅')
            if reaction and reaction.count >= 2:
                sheet.update_cell(cell.row, 3, "Verificado")  # Suponiendo que la columna de estado está en la tercera columna (C)
                user = bot.get_user(user_id)
                await user.send("¡Tu quota ha sido verificada!")

####    Actualizacion De Servers        ####

@tasks.loop(hours=24)
async def update_embed():
    TheIsland = client.open('Servers').worksheet('TheIsland')
    Scorchead = client.open('Servers').worksheet('Scorchead')
    global previous_messages

    print("Actualizando embeds...")
    
    # Obtener datos de la hoja de cálculo TheIsland
    isla = TheIsland.get_all_values()

    # Crear un nuevo embed para TheIsland
    embed_isla = discord.Embed(title="Actualización Diaria TheIsland", color=0x00ff00)

    # Obtener valores de la primera columna y sus correspondientes columnas de valores
    for row in isla:
        field = row[0]
        values = row[1:]
        value_str = " , ".join(values)  # Concatenar los valores en un solo mensaje

        embed_isla.add_field(name=field, value=value_str, inline=False)

    # Obtener el canal de actualización
    update_channel = discord.utils.get(bot.get_all_channels(), name=config.servers_chanel_name)

    # Borrar el mensaje anterior de TheIsland si existe
    if previous_messages["TheIsland"]:
        await previous_messages["TheIsland"].delete()

    # Enviar el nuevo embed de TheIsland al canal y guardar una referencia al mensaje
    previous_messages["TheIsland"] = await update_channel.send(embed=embed_isla)
    
    # Obtener datos de la hoja de cálculo Scorchead
    se = Scorchead.get_all_values()

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

####    Listado De Bps Por Categoria        ####

@bot.command()
async def bp(ctx):

    async def my_callback(interaction):
        selected_option = interaction.data["values"][0]
        if selected_option == "arma":
            await arma(ctx)
        elif selected_option == "armadura":
            await armadura(ctx)
        elif selected_option == "montura":
            await montura(ctx)
        # Agrega más opciones aquí si es necesario

    options = [
        discord.SelectOption(label="Armaduras", value="armadura"),
        discord.SelectOption(label="Monturas", value="montura"),
        discord.SelectOption(label="Armas", value="arma"),
    ]

    select = discord.ui.Select(
        placeholder="Qué BP buscas",
        options=options,
        custom_id="menu_desplegable"
    )

    select.callback = my_callback
    view = discord.ui.View()
    view.add_item(select)

    await ctx.send("Selecciona una opción:", view=view)

@bot.command()
async def arma(ctx):
    armas_worksheet = client.open('Bp').worksheet('Arma')

    armas = [
        discord.SelectOption(label="Hacha", value="hacha"),
        discord.SelectOption(label="Pico", value="pico"),
        discord.SelectOption(label="Espada", value="espada"),
        discord.SelectOption(label="Ballesta", value="ballesta"),
        discord.SelectOption(label="Garrote", value="garrote"),
        discord.SelectOption(label="Sniper", value="sniper"),
        discord.SelectOption(label="Escopeta", value="escopeta"),
        discord.SelectOption(label="Arco Compuesto", value="bow"),
        discord.SelectOption(label="Latigo", value="latigo"),
    ]

    select = discord.ui.Select(
        placeholder="Qué arma buscas",
        options=armas,
        custom_id="menu_arma"
    )

    async def my_callback(interaction):
        selected_option = interaction.data["values"][0]
        embed_armas = discord.Embed(title=f"Coste bp de {selected_option} ", color=0x00ff00)
        celda = armas_worksheet.find(str(selected_option))

        img = armas_worksheet.cell(celda.row,2).value
        metal = armas_worksheet.cell(celda.row,3).value
        madera = armas_worksheet.cell(celda.row,4).value
        piel = armas_worksheet.cell(celda.row,5).value
        fibra = armas_worksheet.cell(celda.row,6).value
        polimero = armas_worksheet.cell(celda.row,7).value
        cemento = armas_worksheet.cell(celda.row,8).value
        seda = armas_worksheet.cell(celda.row,9).value

        if img!=None:
            embed_armas.set_image(url=img)
        if metal!=None:
            embed_armas.add_field(name="metal", value=metal)
        if madera!=None:
            embed_armas.add_field(name="madera", value=madera)
        if piel!=None:
            embed_armas.add_field(name="piel", value=piel)
        if fibra!=None:
            embed_armas.add_field(name="fibra", value=fibra)
        if cemento!=None:
            embed_armas.add_field(name="cemento", value=cemento)
        if polimero!=None:
            embed_armas.add_field(name="polimero", value=polimero)
        if seda!=None:
            embed_armas.add_field(name="seda", value=seda)

        await interaction.response.send_message(embed=embed_armas)

    select.callback = my_callback
    view_arma = discord.ui.View()
    view_arma.add_item(select)

    await ctx.send("Selecciona un bp de arma:", view=view_arma)

@bot.command()
async def armadura(ctx):
    armaduras_worksheet = client.open('Bp').worksheet('Armadura')

    armaduras = [
        discord.SelectOption(label="Casco", value="casco"),
        discord.SelectOption(label="Pechera", value="pechera"),
        discord.SelectOption(label="Guantes", value="guantes"),
        discord.SelectOption(label="Pantalones", value="pantalones"),
        discord.SelectOption(label="Botas", value="botas"),
        discord.SelectOption(label="Escudo Riot", value="escudo_riot"),
        discord.SelectOption(label="Mascara de Gas", value="mascara_gas"),
    ]

    select = discord.ui.Select(
        placeholder="Qué armadura buscas",
        options=armaduras,
        custom_id="menu_armadura"
    )

    async def my_callback(interaction):
        selected_option = interaction.data["values"][0]
        embed_armadura = discord.Embed(title=f"Coste bp de {selected_option} ", color=0x00ff00)
        celda = armaduras_worksheet.find(str(selected_option))

        img = armaduras_worksheet.cell(celda.row,2).value
        fibra = armaduras_worksheet.cell(celda.row,3).value
        piel = armaduras_worksheet.cell(celda.row,4).value
        metal = armaduras_worksheet.cell(celda.row,5).value
        perlas = armaduras_worksheet.cell(celda.row,6).value
        cristal = armaduras_worksheet.cell(celda.row,7).value
        polimero = armaduras_worksheet.cell(celda.row,8).value
        sustrato = armaduras_worksheet.cell(celda.row,9).value

        if img!=None:
            embed_armadura.set_image(url=img)
        if fibra!=None:
            embed_armadura.add_field(name="fibra", value=fibra)
        if piel!=None:
            embed_armadura.add_field(name="piel", value=piel)
        if metal!=None:
            embed_armadura.add_field(name="metal", value=metal)
        if perlas!=None:
            embed_armadura.add_field(name="perlas", value=perlas)
        if cristal!=None:
            embed_armadura.add_field(name="cristal", value=cristal)
        if polimero!=None:
            embed_armadura.add_field(name="polimero", value=polimero)
        if sustrato!=None:
            embed_armadura.add_field(name="sustrato", value=sustrato)

        await interaction.response.send_message(embed=embed_armadura)

    select.callback = my_callback
    view_armadura = discord.ui.View()
    view_armadura.add_item(select)

    await ctx.send("Selecciona un bp de armadura:", view=view_armadura)

@bot.command()
async def montura(ctx):
    monturas_worksheet = client.open('Bp').worksheet('Montura')

    monturas = [
        discord.SelectOption(label="Carbo", value="carbo"),
        discord.SelectOption(label="trike", value="trike"),
        discord.SelectOption(label="Stego", value="stego"),
        discord.SelectOption(label="Racer", value="racer"),
        discord.SelectOption(label="Bronto", value="bronto"),
        discord.SelectOption(label="Basilo", value="basilo"),
        discord.SelectOption(label="Mosa", value="mosa"),
        discord.SelectOption(label="Tuso", value="tuso"),
        discord.SelectOption(label="Giga", value="giga"),
        discord.SelectOption(label="Spino", value="spino"),
        discord.SelectOption(label="Rex", value="rex"),
        discord.SelectOption(label="Rhino", value="rhino"),
        discord.SelectOption(label="Theri", value="theri"),
        discord.SelectOption(label="Deino", value="deino"),
        discord.SelectOption(label="Thyla", value="thyla"),
        discord.SelectOption(label="Mamuth", value="mamuth"),
        discord.SelectOption(label="Mantis", value="mantis"),
        discord.SelectOption(label="Ptera", value="ptera"),
        discord.SelectOption(label="Quetzal", value="quetzal"),
        discord.SelectOption(label="Tapejara", value="tapejara"),
        discord.SelectOption(label="Golem", value="golem"),
        discord.SelectOption(label="Yuti", value="yuti"),
    ]

    select = discord.ui.Select(
        placeholder="Qué montura buscas",
        options=monturas,
        custom_id="menu_montura"
    )

    async def my_callback(interaction):
        selected_option = interaction.data["values"][0]
        embed_monturas = discord.Embed(title=f"Coste bp de {selected_option} ", color=0x00ff00)
        celda = monturas_worksheet.find(str(selected_option))

        img = monturas_worksheet.cell(celda.row,2).value
        fibra = monturas_worksheet.cell(celda.row,3).value
        piel = monturas_worksheet.cell(celda.row,4).value
        metal = monturas_worksheet.cell(celda.row,5).value
        madera = monturas_worksheet.cell(celda.row,6).value
        chitin = monturas_worksheet.cell(celda.row,7).value
        perlas = monturas_worksheet.cell(celda.row,8).value
        cemento = monturas_worksheet.cell(celda.row,9).value

        if img!=None:
            embed_monturas.set_image(url=img)
        if fibra!=None:
            embed_monturas.add_field(name="fibra", value=fibra)
        if piel!=None:
            embed_monturas.add_field(name="piel", value=piel)
        if madera!=None:
            embed_monturas.add_field(name="madera", value=madera)
        if metal!=None:
            embed_monturas.add_field(name="metal", value=metal)
        if perlas!=None:
            embed_monturas.add_field(name="perlas", value=perlas)
        if chitin!=None:
            embed_monturas.add_field(name="chitin", value=chitin)
        if cemento!=None:
            embed_monturas.add_field(name="cemento", value=cemento)
        

        await interaction.response.send_message(embed=embed_monturas)

    select.callback = my_callback
    view_montura = discord.ui.View()
    view_montura.add_item(select)

    await ctx.send("Selecciona un bp de montura:", view=view_montura)

####    Calcular Coste De Bps       ####

@bot.command()
async def costbp(ctx, cantidad):
    global cantidades
    cantidades = cantidad

    async def my_callback(interaction):
        selected_option = interaction.data["values"][0]
        if selected_option == "arma":
            await costarma(ctx)
        elif selected_option == "armadura":
            await costarmadura(ctx)
        elif selected_option == "montura":
            await costmontura(ctx)
        # Agrega más opciones aquí si es necesario

    options = [
        discord.SelectOption(label="Armaduras", value="armadura"),
        discord.SelectOption(label="Monturas", value="montura"),
        discord.SelectOption(label="Armas", value="arma"),
    ]

    select = discord.ui.Select(
        placeholder="Qué BP buscas",
        options=options,
        custom_id="menu_desplegable"
    )

    select.callback = my_callback
    view = discord.ui.View()
    view.add_item(select)

    await ctx.send("Selecciona una opción:", view=view)

@bot.command()
async def costarma(ctx):
    global cantidades

    armas_worksheet = client.open('Bp').worksheet('Arma')

    armas = [
        discord.SelectOption(label="Hacha", value="hacha"),
        discord.SelectOption(label="Pico", value="pico"),
        discord.SelectOption(label="Espada", value="espada"),
        discord.SelectOption(label="Ballesta", value="ballesta"),
        discord.SelectOption(label="Garrote", value="garrote"),
        discord.SelectOption(label="Sniper", value="sniper"),
        discord.SelectOption(label="Escopeta", value="escopeta"),
        discord.SelectOption(label="Arco Compuesto", value="bow"),
        discord.SelectOption(label="Latigo", value="latigo"),
    ]

    select = discord.ui.Select(
        placeholder="Qué arma buscas",
        options=armas,
        custom_id="menu_arma"
    )

    async def my_callback(interaction):
        selected_option = interaction.data["values"][0]
        embed_armas = discord.Embed(title=f"Coste bp de {selected_option} ", color=0x00ff00)
        celda = armas_worksheet.find(str(selected_option))

        img = armas_worksheet.cell(celda.row,2).value
        metal = armas_worksheet.cell(celda.row,3).value
        madera = armas_worksheet.cell(celda.row,4).value
        piel = armas_worksheet.cell(celda.row,5).value
        fibra = armas_worksheet.cell(celda.row,6).value
        polimero = armas_worksheet.cell(celda.row,7).value
        cemento = armas_worksheet.cell(celda.row,8).value
        seda = armas_worksheet.cell(celda.row,9).value

        if img!=None:
            embed_armas.set_image(url=img)
        if metal!=None:
            costmetal = int(metal)*int(cantidades)
            embed_armas.add_field(name="metal", value=costmetal)
        if madera!=None:
            costmadera = int(madera)*int(cantidades)
            embed_armas.add_field(name="madera", value=costmadera)
        if piel!=None:
            costpiel = int(piel)*int(cantidades)
            embed_armas.add_field(name="piel", value=costpiel)
        if fibra!=None:
            costfibra = int(fibra)*int(cantidades)
            embed_armas.add_field(name="fibra", value=costfibra)
        if cemento!=None:
            costcemento = int(cemento)*int(cantidades)
            embed_armas.add_field(name="cemento", value=costcemento)
        if polimero!=None:
            costpolimero = int(polimero)*int(cantidades)
            embed_armas.add_field(name="polimero", value=costpolimero)
        if seda!=None:
            costseda = int(seda)*int(cantidades)
            embed_armas.add_field(name="seda", value=costseda)

        await interaction.response.send_message(embed=embed_armas)

    select.callback = my_callback
    view_arma = discord.ui.View()
    view_arma.add_item(select)

    await ctx.send("Selecciona un bp de arma:", view=view_arma)

@bot.command()
async def costarmadura(ctx):
    global cantidades

    armaduras_worksheet = client.open('Bp').worksheet('Armadura')

    armaduras = [
        discord.SelectOption(label="Casco", value="casco"),
        discord.SelectOption(label="Pechera", value="pechera"),
        discord.SelectOption(label="Guantes", value="guantes"),
        discord.SelectOption(label="Pantalones", value="pantalones"),
        discord.SelectOption(label="Botas", value="botas"),
        discord.SelectOption(label="Escudo Riot", value="escudo_riot"),
        discord.SelectOption(label="Mascara de Gas", value="mascara_gas"),
    ]

    select = discord.ui.Select(
        placeholder="Qué armadura buscas",
        options=armaduras,
        custom_id="menu_armadura"
    )

    async def my_callback(interaction):
        selected_option = interaction.data["values"][0]
        embed_armadura = discord.Embed(title=f"Coste bp de {selected_option} ", color=0x00ff00)
        celda = armaduras_worksheet.find(str(selected_option))

        img = armaduras_worksheet.cell(celda.row,2).value
        fibra = armaduras_worksheet.cell(celda.row,3).value
        piel = armaduras_worksheet.cell(celda.row,4).value
        metal = armaduras_worksheet.cell(celda.row,5).value
        perlas = armaduras_worksheet.cell(celda.row,6).value
        cristal = armaduras_worksheet.cell(celda.row,7).value
        polimero = armaduras_worksheet.cell(celda.row,8).value
        sustrato = armaduras_worksheet.cell(celda.row,9).value

        if img!=None:
            embed_armadura.set_image(url=img)
        if fibra!=None:
            costfibra = int(fibra)*int(cantidades)
            embed_armadura.add_field(name="fibra", value=costfibra)
        if piel!=None:
            costpiel = int(piel)*int(cantidades)
            embed_armadura.add_field(name="piel", value=costpiel)
        if metal!=None:
            costmetal = int(metal)*int(cantidades)
            embed_armadura.add_field(name="metal", value=costmetal)
        if perlas!=None:
            costperlas = int(perlas)*int(cantidades)
            embed_armadura.add_field(name="perlas", value=costperlas)
        if cristal!=None:
            costcristal = int(cristal)*(cantidades)
            embed_armadura.add_field(name="cristal", value=costcristal)
        if polimero!=None:
            costpolimero = int(polimero)*int(cantidades)
            embed_armadura.add_field(name="polimero", value=costpolimero)
        if sustrato!=None:
            costsustrato = int(sustrato)*int(cantidades)
            embed_armadura.add_field(name="sustrato", value=costsustrato)

        await interaction.response.send_message(embed=embed_armadura)

    select.callback = my_callback
    view_armadura = discord.ui.View()
    view_armadura.add_item(select)

    await ctx.send("Selecciona un bp de armadura:", view=view_armadura)

@bot.command()
async def costmontura(ctx):
    global cantidades

    monturas_worksheet = client.open('Bp').worksheet('Montura')

    monturas = [
        discord.SelectOption(label="Carbo", value="carbo"),
        discord.SelectOption(label="trike", value="trike"),
        discord.SelectOption(label="Stego", value="stego"),
        discord.SelectOption(label="Racer", value="racer"),
        discord.SelectOption(label="Bronto", value="bronto"),
        discord.SelectOption(label="Basilo", value="basilo"),
        discord.SelectOption(label="Mosa", value="mosa"),
        discord.SelectOption(label="Tuso", value="tuso"),
        discord.SelectOption(label="Giga", value="giga"),
        discord.SelectOption(label="Spino", value="spino"),
        discord.SelectOption(label="Rex", value="rex"),
        discord.SelectOption(label="Rhino", value="rhino"),
        discord.SelectOption(label="Theri", value="theri"),
        discord.SelectOption(label="Deino", value="deino"),
        discord.SelectOption(label="Thyla", value="thyla"),
        discord.SelectOption(label="Mamuth", value="mamuth"),
        discord.SelectOption(label="Mantis", value="mantis"),
        discord.SelectOption(label="Ptera", value="ptera"),
        discord.SelectOption(label="Quetzal", value="quetzal"),
        discord.SelectOption(label="Tapejara", value="tapejara"),
        discord.SelectOption(label="Golem", value="golem"),
        discord.SelectOption(label="Yuti", value="yuti"),
    ]

    select = discord.ui.Select(
        placeholder="Qué montura buscas",
        options=monturas,
        custom_id="menu_montura"
    )

    async def my_callback(interaction):
        selected_option = interaction.data["values"][0]
        embed_monturas = discord.Embed(title=f"Coste bp de {selected_option} ", color=0x00ff00)
        celda = monturas_worksheet.find(str(selected_option))

        img = monturas_worksheet.cell(celda.row,2).value
        fibra = monturas_worksheet.cell(celda.row,3).value
        piel = monturas_worksheet.cell(celda.row,4).value
        metal = monturas_worksheet.cell(celda.row,5).value
        madera = monturas_worksheet.cell(celda.row,6).value
        chitin = monturas_worksheet.cell(celda.row,7).value
        perlas = monturas_worksheet.cell(celda.row,8).value
        cemento = monturas_worksheet.cell(celda.row,9).value

        if img!=None:
            embed_monturas.set_image(url=img)
        if fibra!=None:
            costfibra = int(fibra)*int(cantidades)
            embed_monturas.add_field(name="fibra", value=costfibra)
        if piel!=None:
            costpiel = int(piel)*int(cantidades)
            embed_monturas.add_field(name="piel", value=costpiel)
        if madera!=None:
            costmadera = int(madera)*int(cantidades)
            embed_monturas.add_field(name="madera", value=costmadera)
        if metal!=None:
            costmetal = int(metal)*int(cantidades)
            embed_monturas.add_field(name="metal", value=costmetal)
        if perlas!=None:
            costperlas = int(perlas)*int(cantidades)
            embed_monturas.add_field(name="perlas", value=costperlas)
        if chitin!=None:
            costchitin = int(chitin)*int(cantidades)
            embed_monturas.add_field(name="chitin", value=costchitin)
        if cemento!=None:
            costcemento = int(cemento)*int(cantidades)
            embed_monturas.add_field(name="cemento", value=costcemento)
        

        await interaction.response.send_message(embed=embed_monturas)

    select.callback = my_callback
    view_montura = discord.ui.View()
    view_montura.add_item(select)

    await ctx.send("Selecciona un bp de montura:", view=view_montura)


bot.run(config.TOKEN)  # Asegúrate de definir TOKEN en tu archivo de configuración
