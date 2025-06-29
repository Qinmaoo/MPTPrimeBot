import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from typing import Optional

parentPath = os.path.dirname(os.path.abspath(__file__))

with open(parentPath + '/charlist.json') as f:
    charlist = json.load(f)

def load_primes():
    with open(parentPath + '/primes.json', 'r', encoding='utf-8') as f:
        primes = json.load(f)
    return primes

def get_primes(player, contact):    
    primes = load_primes()
    if not player and not contact:
        filter_primes = primes
    elif player and contact:
        filter_primes = list(filter(lambda prime: prime["player_wanted"] == player and prime["player_to_pay"] == contact, primes))
    elif player:
        filter_primes = list(filter(lambda prime: prime["player_wanted"] == player, primes))
    elif contact:
        filter_primes = list(filter(lambda prime: prime["player_to_pay"] == contact, primes))
    
    print(filter_primes)
    return filter_primes

class GetPrimes(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="getprimes",
        description="Récupérer les primes en cours"
    )
    @app_commands.describe(
        player="Le joueur wanted",
        contact="La personne qui paye"
    )
    async def getprimes(
        self,
        interaction: discord.Interaction,
        player: Optional[str],
        contact: Optional[str],
    ) -> None:
        await interaction.response.defer(thinking=True)

        data = get_primes(player, contact)

        embed = discord.Embed(
            title="Primes récupérées"
        )

        for prime in data:
            embed.add_field(
                name=f"{prime['player_wanted']} ({prime['caracters_played']})",
                value=f"Récompense: {prime['is_claimed']} - Payé par: {prime['player_to_pay']}",
                inline=False
            )

        await interaction.followup.send(embed=embed)

    @getprimes.autocomplete('player')
    async def player_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:
        
        primes = load_primes()
        players = list(set(prime['player_wanted'] for prime in primes))
        return [
            app_commands.Choice(name=p, value=p)
            for p in players if current.lower() in p.lower()
        ][:25]

    @getprimes.autocomplete('contact')
    async def contact_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:
        
        primes = load_primes()
        contacts = list(set(prime['player_to_pay'] for prime in primes))
        return [
            app_commands.Choice(name=c, value=c)
            for c in contacts if current.lower() in c.lower()
        ][:25]

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GetPrimes(bot))
