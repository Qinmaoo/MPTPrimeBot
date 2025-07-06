import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from typing import Optional
from cogs.claim_view import ClaimView
from cogs.pagination_view import PrimesPaginationView

parentPath = os.path.dirname(os.path.abspath(__file__))

def load_primes():
    with open(parentPath + '/primes.json', 'r', encoding='utf-8') as f:
        primes = json.load(f)
    return primes

def get_primes(guild: discord.Guild):
    primes = load_primes()

    def resolve_contact_name(prime):
        contact_id = prime.get("player_to_pay_id")
        if not contact_id:
            return None
        member = guild.get_member(int(contact_id))
        return member.display_name if member else str(contact_id)
    
    primes = [p for p in primes if not p["collected"]]

    return primes

class Edit(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="edit",
        description="Modifier une prime que vous avez faite"
    )
    @app_commands.describe(
        player="Le joueur wanted"
    )
    async def edit(
        self,
        interaction: discord.Interaction,
        player: Optional[str]
    ) -> None:
        
        await interaction.response.defer(thinking=True)

        guild = interaction.guild
        data = get_primes(guild)

        data = [p for p in data if data['player_to_pay_id'] == interaction.user.id]

        embed = discord.Embed(
            title = "Test",
            color=discord.Color.gold()
        )
            
        for prime in data:
            contactid = prime['player_to_pay_id']

            paying_line = f"👤 **Payeur :** <@{contactid}>\n"
            is_claimed = "✅" if prime["is_claimed"] else "❌"
            is_collected = "✅" if prime["collected"] else "❌"

            embed.add_field(
                name=f"{prime['player_wanted']} ({prime['characters_played']})",
                value=(
                    f"💰 **Récompense :** {prime['reward']}\n"
                    f"{paying_line}"
                    f"📌 **Réclamée :** {is_claimed} | **Récupérée :** {is_collected}"
                ),
                inline=False
            )

        embed = discord.Embed(title="Test", color=discord.Color.gold())
        for prime in data:
            contactid = prime['player_to_pay_id']
            paying_line = f"👤 **Payeur :** <@{contactid}>\n"
            is_claimed = "✅" if prime["is_claimed"] else "❌"
            is_collected = "✅" if prime["collected"] else "❌"

            embed.add_field(
                name=f"{prime['player_wanted']} ({prime['characters_played']})",
                value=(
                    f"💰 **Récompense :** {prime['reward']}\n"
                    f"{paying_line}"
                    f"📌 **Réclamée :** {is_claimed} | **Récupérée :** {is_collected}"
                ),
                inline=False
            )
        await interaction.followup.send(embed=embed)

    @edit.autocomplete('player')
    async def player_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:
        
        primes = load_primes()
        primes = [p for p in primes if not p["collected"] and p["player_to_pay_id"] == interaction.user.id]
        players = list(set(prime['player_wanted'] for prime in primes))
        return [
            app_commands.Choice(name=p, value=p)
            for p in players if current.lower() in p.lower()
        ][:25]

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Edit(bot))