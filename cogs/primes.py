import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from typing import Optional
from cogs.claim_view import ClaimView
from cogs.make_poster import create_wanted_poster

parentPath = os.path.dirname(os.path.abspath(__file__))

with open(parentPath + '/charlist.json') as f:
    charlist = json.load(f)

def load_primes():
    with open(parentPath + '/primes.json', 'r', encoding='utf-8') as f:
        primes = json.load(f)
    return primes

def get_primes(player: Optional[str], contact: Optional[str], guild: discord.Guild):    
    primes = load_primes()

    def resolve_contact_name(prime):
        contactid = prime.get("player_to_pay_id")
        if not contactid:
            return None
        member = guild.get_member(int(contactid))
        return member.display_name if member else str(contactid)

    primes = [p for p in primes if not p["collected"]]

    def prime_matches(prime):
        if player and prime["player_wanted"] != player:
            return False
        if contact:
            contact_display = resolve_contact_name(prime)
            return contact_display == contact
        return True

    filtered_primes = [p for p in primes if prime_matches(p)]
    
    return filtered_primes

class Primes(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="primes",
        description="Récupérer les primes en cours"
    )
    @app_commands.describe(
        player="Le joueur wanted",
        contact="La personne qui paye"
    )
    async def primes(
        self,
        interaction: discord.Interaction,
        player: Optional[str],
        contact: Optional[str],
    ) -> None:
        
        await interaction.response.defer(thinking=True)
        guild = interaction.guild
        data = get_primes(player, contact, guild)
        
        if not player and not contact:
            embed_title = "🏆 Primes en cours"
        elif contact and not player:
            embed_title = f"🏆 Primes posées par {contact}"
        else:
            embed_title = f"🏆 Prime sur {player}"
        
        
        embed = discord.Embed(
            title = embed_title,
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

        if len(data) == 1:
            prime = data[0]
            contactid = int(prime["player_to_pay_id"])
            member = guild.get_member(contactid)
            contact_display = member.display_name if member else str(contactid)
            
            buffer = create_wanted_poster(player, prime["characters_played"], prime["reward"], contact_display)
            file = discord.File(buffer, filename="wanted.png")
            embed.set_image(url="attachment://wanted.png")
            
            if not prime["collected"]:
                view = ClaimView(prime_id=prime["id"], current_state=prime, author_id=interaction.user.id)

            await interaction.followup.send(embed=embed, view=view, file=file)
        else:
            await interaction.followup.send(embed=embed)

    @primes.autocomplete('player')
    async def player_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:
        
        primes = load_primes()
        primes = [p for p in primes if not p["collected"]]
        players = list(set(prime['player_wanted'] for prime in primes))
        return [
            app_commands.Choice(name=p, value=p)
            for p in players if current.lower() in p.lower()
        ][:25]

    @primes.autocomplete('contact')
    async def contact_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:
        
        primes = load_primes()
        guild = interaction.guild
        
        contacts = []
        for prime in primes:
            contactid = prime['player_to_pay_id']
            member = guild.get_member(int(contactid))
            contact_display = member.display_name if member else contactid
            contacts.append(contact_display)
    
        contacts = list(set(contacts))
        return [
            app_commands.Choice(name=c, value=c)
            for c in contacts if current.lower() in c.lower()
        ][:25]

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Primes(bot))
