import discord
from discord.ext import commands
import gspread
from google.oauth2 import service_account

KEY = "credentials.json"
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
creds = service_account.Credentials.from_service_account_file(KEY, scopes=SCOPES)
client = gspread.authorize(creds)

class bps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bp(self,ctx):
        await ctx.message.delete()
        async def my_callback(interaction):
            selected_option = interaction.data["values"][0]
            if selected_option == "arma":
                await message.delete()
                await self.arma(ctx)
            elif selected_option == "armadura":
                await message.delete()
                await self.armadura(ctx)
            elif selected_option == "montura":
                await message.delete()
                await self.montura(ctx)
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

        message = await ctx.send("Selecciona una opción:", view=view)

    @commands.command()
    async def arma(self,ctx):
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
                embed_armas.add_field(name="Metal", value=metal)
            if madera!=None:
                embed_armas.add_field(name="Madera", value=madera)
            if piel!=None:
                embed_armas.add_field(name="Piel", value=piel)
            if fibra!=None:
                embed_armas.add_field(name="Fibra", value=fibra)
            if cemento!=None:
                embed_armas.add_field(name="Cemento", value=cemento)
            if polimero!=None:
                embed_armas.add_field(name="Polimero", value=polimero)
            if seda!=None:
                embed_armas.add_field(name="Seda", value=seda)

            await interaction.response.send_message(embed=embed_armas)
            await menssage.delete() 


        select.callback = my_callback
        view_arma = discord.ui.View()
        view_arma.add_item(select)

        menssage = await ctx.send("Selecciona un bp de arma:", view=view_arma)

    @commands.command()
    async def armadura(self,ctx):
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
                embed_armadura.add_field(name="Fibra", value=fibra)
            if piel!=None:
                embed_armadura.add_field(name="Piel", value=piel)
            if metal!=None:
                embed_armadura.add_field(name="Metal", value=metal)
            if perlas!=None:
                embed_armadura.add_field(name="Perlas", value=perlas)
            if cristal!=None:
                embed_armadura.add_field(name="Cristal", value=cristal)
            if polimero!=None:
                embed_armadura.add_field(name="Polimero", value=polimero)
            if sustrato!=None:
                embed_armadura.add_field(name="Sustrato", value=sustrato)

            await interaction.response.send_message(embed=embed_armadura)
            await menssage.delete() 

        select.callback = my_callback
        view_armadura = discord.ui.View()
        view_armadura.add_item(select)

        menssage = await ctx.send("Selecciona un bp de armadura:", view=view_armadura)

    @commands.command()
    async def montura(self,ctx):
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
                embed_monturas.add_field(name="Fibra", value=fibra)
            if piel!=None:
                embed_monturas.add_field(name="Piel", value=piel)
            if madera!=None:
                embed_monturas.add_field(name="Madera", value=madera)
            if metal!=None:
                embed_monturas.add_field(name="Metal", value=metal)
            if perlas!=None:
                embed_monturas.add_field(name="Perlas", value=perlas)
            if chitin!=None:
                embed_monturas.add_field(name="Chitin", value=chitin)
            if cemento!=None:
                embed_monturas.add_field(name="Cemento", value=cemento)
            

            await interaction.response.send_message(embed=embed_monturas)
            await menssage.delete() 

        select.callback = my_callback
        view_montura = discord.ui.View()
        view_montura.add_item(select)

        menssage = await ctx.send("Selecciona un bp de montura:", view=view_montura)

async def setup(bot):
    await bot.add_cog(bps(bot))
