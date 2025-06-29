import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from typing import Optional
import sys, io

parentPath = os.path.dirname(os.path.abspath(__file__))

with open(parentPath + '/charlist.json') as f:
    charlist = json.load(f)

with open(parentPath + '/primes.json', 'r') as f:
    primes = json.load(f)

player_list = list(set([prime['player_wanted'] for prime in primes]))
contact_list = list(set([prime['player_to_pay'] for prime in primes]))

def get_primes(player, contact):    
    if not player and not contact:
        filter_primes = primes
    elif player and contact:
        filter_primes = filter(lambda prime: prime["player_wanted"] == player and prime["player_to_pay"] == contact, primes)
    elif player:
        filter_primes = filter(lambda prime: prime["player_wanted"] == player, primes)
    elif contact:
        filter_primes = filter(lambda prime: prime["player_to_pay"] == contact, primes)
    
    for prime in filter_primes:
        print(prime)
    return filter_primes
    
class GetPrimes(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
    
    @app_commands.command(
        name = "getprimes",
        description = "Récupérer les primes en cours"
    )
    
    @app_commands.describe(
        player = "Le joueur wanted",
        contact = "La personne qui paye"
    )

    @app_commands.choices(
        player = [app_commands.Choice(name=player, value=player) for player in player_list],
        contact = [app_commands.Choice(name=contact, value=contact) for contact in contact_list],
    )
    
    async def getbx(
        self,
        interaction: discord.Interaction,
        player: Optional[app_commands.Choice[str]],
        contact: Optional[app_commands.Choice[str]],
    ) -> None:
        
        await interaction.response.defer(thinking=True)

        id = interaction.user.id
        player = player.value if player else None
        contact = contact.value if contact else None
        
        data = get_primes(player, contact)
            
        buffer = io.BytesIO()
        data.save(buffer, format="PNG")
        buffer.seek(0)

        file = discord.File(buffer, filename="image.png")
        embed = discord.Embed(
            title=f""
        )
        embed.set_image(url="attachment://image.png")

        await interaction.followup.send(embed=embed, files=[file])

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GetPrimes(bot))

# Test command line

if __name__ == '__main__':
    get_primes(player=None, contact="Payeur 2")