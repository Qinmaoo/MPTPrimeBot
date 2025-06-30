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

def get_primes(player: Optional[str], contact: Optional[str], guild: discord.Guild):    
    primes = load_primes()

    def resolve_contact_name(prime):
        if prime["player_to_pay"]:
            return prime["player_to_pay"]
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
    print(filtered_primes)
    return filtered_primes

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
        guild = interaction.guild

        data = get_primes(player, contact, guild)
        
        if contact and contact.isdigit():
            member = guild.get_member(int(contact))
            if member:
                contact_display = member.display_name
            else:
                contact_display = f"<@{contact}>"
        else:
            contact_display = contact
            
        if not player and not contact:
            embed_title = "🏆 Primes en cours"
        elif contact and not player:
            embed_title = f"🏆 Primes posées par {contact_display}"
        else:
            embed_title = f"🏆 Prime sur {player}"
        
        
        embed = discord.Embed(
            title = embed_title,
            color=discord.Color.gold()
        )

        for prime in data:
            contact = prime['player_to_pay']
            contactid = prime['player_to_pay_id']

            is_claimed = "✅" if prime["is_claimed"] else "❌"
            is_collected = "✅" if prime["collected"] else "❌"

            embed.add_field(
                name=f"{prime['player_wanted']} ({prime['characters_played']})",
                value=(
                    f"💰 **Récompense :** {prime['reward']}\n"
                    f"👤 **Payeur :** <@{contactid}>\n"
                    f"📌 **Réclamée :** {is_claimed} | **Récupérée :** {is_collected}"
                ),
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
        guild = interaction.guild
        
        contacts = []
        for prime in primes:
            contact = prime['player_to_pay']
            contactid = prime['player_to_pay_id']
            if contact:
                contacts.append(contact)
            else: 
                member = guild.get_member(int(contactid))
                contact_display = member.display_name if member else contactid
                contacts.append(contact_display)
    
        contacts = list(set(contacts))
        return [
            app_commands.Choice(name=c, value=c)
            for c in contacts if current.lower() in c.lower()
        ][:25]

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GetPrimes(bot))
