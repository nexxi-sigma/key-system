import discord
from discord.ext import commands
import requests
import asyncio

TOKEN = "MTM0OTAwNTU3NTYxODQzMzA1Nw.GoIb7f.fbsTxybHWNZ_i7A3dt9VohVDWrydtTRhPm9Ga4"
SERVER_URL = "http://your-server-ip"  # Podmień na adres Twojej strony

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())
role_to_assign = None  # Przechowuje ID roli ustawionej przez /roleset

async def assign_role(user, guild):
    if role_to_assign:
        role = guild.get_role(role_to_assign)
        if role:
            await user.add_roles(role)
            await asyncio.sleep(3600)
            await user.remove_roles(role)
        else:
            return "❌ Nie znaleziono ustawionej roli!"
    else:
        return "❌ Nie ustawiono roli do przypisania!"
    return None

@bot.command()
async def keyset(ctx):
    view = discord.ui.View()
    
    class RedeemKey(discord.ui.Modal, title="Wpisz swój klucz"):
        key = discord.ui.TextInput(label="Klucz", placeholder="Wpisz swój klucz tutaj")

        async def on_submit(self, interaction: discord.Interaction):
            try:
                response = requests.post(f"{SERVER_URL}/validate", json={'key': self.key.value})
                response_data = response.json()
                if response_data.get('valid'):
                    error_message = await assign_role(interaction.user, interaction.guild)
                    if error_message:
                        await interaction.response.send_message(error_message, ephemeral=True)
                    else:
                        await interaction.response.send_message(f"✅ Klucz poprawny! Dodano rolę na 1 godzinę.", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Niepoprawny lub już użyty klucz!", ephemeral=True)
            except requests.exceptions.RequestException:
                await interaction.response.send_message("❌ Błąd połączenia z serwerem!", ephemeral=True)
    
    @discord.ui.button(label="Redeem Key", style=discord.ButtonStyle.green)
    async def redeem_button(interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RedeemKey())
    
    @discord.ui.button(label="Generate Key", style=discord.ButtonStyle.blurple, url=f"{SERVER_URL}/generate-key")
    async def generate_button(interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔗 Kliknij poniższy przycisk, aby wygenerować klucz na stronie.", ephemeral=True)
    
    view.add_item(redeem_button)
    view.add_item(generate_button)
    
    await ctx.send("🔑 Wybierz opcję:", view=view)

@bot.command()
async def roleset(ctx, role: discord.Role):
    global role_to_assign
    role_to_assign = role.id
    await ctx.send(f"✅ Ustawiono rolę **{role.name}** do przypisywania po zweryfikowaniu klucza.")

bot.run(TOKEN)
