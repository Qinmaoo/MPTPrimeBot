import discord
import json
import os

from discord import app_commands
from discord.ext import commands
from typing import Optional
from cogs.claim_view import ClaimView
from cogs.pagination_view import PrimesPaginationView
from cogs.make_poster import create_wanted_poster
from cogs.utils import create_message_classic

parentPath = os.path.dirname(os.path.abspath(__file__))

with open(parentPath + '/charlist.json') as f:
    charlist = json.load(f)

# Loader du json
def load_primes():
    with open(parentPath + '/primes.json', 'r', encoding='utf-8') as f:
        primes = json.load(f)
    return primes

# Recuperer les primes, selon les filtres passer en parametres
def get_primes(player: Optional[str], characters: Optional[str], contact: Optional[str], guild: discord.Guild):    
    primes = load_primes()
    primes = [p for p in primes if not p["collected"]]

    # Recuperer le nom du contact
    def resolve_contact_name(prime):
        contactid = prime.get("player_to_pay_id")
        if not contactid:
            return None
        member = guild.get_member(int(contactid))
        return member.display_name if member else str(contactid)

    # Condition pour prendre les primes qui ont le bon player et le bon charactere
    def prime_matches(prime):
        if player and prime["player_wanted"] != player:
            return False
        if characters and prime["characters_played"] != characters:
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
        characters="Le(s) personnage(s) joué(s)",
        contact="La personne qui paye",
    )
    async def primes(
        self,
        interaction: discord.Interaction,
        player: Optional[str],
        characters: Optional[str],
        contact: Optional[str],
    ) -> None:
        
        await interaction.response.defer(thinking=True)
        
        guild = interaction.guild
        data = get_primes(player, characters, contact, guild)
        
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
            create_message_classic(prime, embed)


        if len(data) == 1:
            prime = data[0]
            contactid = int(prime["player_to_pay_id"])
            member = guild.get_member(contactid)
            payer_name = member.display_name if member else str(contactid)
            
            buffer = create_wanted_poster(prime["player_wanted"], prime["characters_played"], prime["reward"], payer_name)
            file = discord.File(buffer, filename="wanted.png")
            embed.set_image(url="attachment://wanted.png")
            
            if not prime["collected"]:
                view = ClaimView(prime_id=prime["id"], current_state=prime, author_id=interaction.user.id)

            await interaction.followup.send(embed=embed, view=view, file=file)
        
        elif len(data) > 10:
            view = PrimesPaginationView(data, embed_title, interaction)
            await view.send()

        else:
            embed = discord.Embed(title=embed_title, color=discord.Color.gold())
            for prime in data:
                create_message_classic(prime, embed)
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
    
    @primes.autocomplete('characters')
    async def characters_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:
        
        primes = load_primes()
        primes = [p for p in primes if not p["collected"]]
        characters = list(set(prime['characters_played'] for prime in primes))
        return [
            app_commands.Choice(name=c, value=c)
            for c in characters if current.lower() in c.lower()
        ][:25]

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Primes(bot))
