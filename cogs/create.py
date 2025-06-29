import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from typing import Optional
import io

parentPath = os.path.dirname(os.path.abspath(__file__))

with open(parentPath + '/charlist.json') as f:
    charlist = json.load(f)

def create_prime(player, character, reward, contact, contactid):
    print(f"{player} ({character}) - {reward} (by {contact})")
    
    with open(parentPath + '/primes.json', 'r', encoding='utf-8') as f:
        primes = json.load(f)
    
    json_to_append = {
        "id": len(primes),
        "player_wanted": player,
        "characters_played": character,
        "player_to_pay": contact,
        "player_to_pay_id": str(contactid),
        "reward": reward,
        "is_claimed": False,
        "collected": False
    } 
    primes.append(json_to_append)
    with open(parentPath + '/primes.json', 'w', encoding='utf-8') as f:
        json.dump(primes, f)

class Create(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="create",
        description="Créer une prime"
    )
    @app_commands.describe(
        player="Le joueur wanted",
        character="Son personnage à battre",
        reward="La récompense associée",
        contact="La personne qui paye"
    )
    async def create(
        self,
        interaction: discord.Interaction,
        player: str,
        character: str,
        reward: str,
        contact: Optional[str] = None
    ) -> None:
        await interaction.response.defer(thinking=True)

        contact = contact if contact else None
        contactid = None if contact else interaction.user.id
        
        create_prime(player, character, reward, contact, contactid)

        embed = discord.Embed(
            title=f"Nouvelle prime: {player} ({character}) - {reward}"
        )

        await interaction.followup.send(embed=embed)

    @create.autocomplete('character')
    async def character_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=fighter.lower().replace(".",""), value=fighter)
            for fighter in charlist["fighters"]
            if current.lower() in fighter.lower()
        ][:25]  

# Setup du cog
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Create(bot))
