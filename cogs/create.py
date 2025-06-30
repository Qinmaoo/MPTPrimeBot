import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from typing import Optional
from io import BytesIO
from cogs.make_poster import create_wanted_poster

parentPath = os.path.dirname(os.path.abspath(__file__))


with open(parentPath + '/charlist.json') as f:
    charlist = json.load(f)

def create_prime(player, character, reward, contactid, guild:discord.Guild):
    
    try:
        with open(parentPath + '/primes.json', 'r', encoding='utf-8') as f:
            primes = json.load(f)
        
        if len([prime for prime in primes if prime["player_wanted"] == player]) != 0:
            return {"status":"failure", "output": f"**{player}** est déjà ciblé par une prime!"}
            
        json_to_append = {
            "id": len(primes),
            "player_wanted": player,
            "characters_played": character,
            "player_to_pay_id": str(contactid),
            "reward": reward,
            "is_claimed": False,
            "collected": False
        } 
        primes.append(json_to_append)
        with open(parentPath + '/primes.json', 'w', encoding='utf-8') as f:
            json.dump(primes, f)
        
        contact_display = guild.get_member(contactid).display_name
        poster_bytes = create_wanted_poster(player, character, reward, contact_display)
        return {"status":"success", "output": poster_bytes}
    except Exception as e:
        return {"status":"failure", "output": f"Error: {e}"}

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
    )
    async def create(
        self,
        interaction: discord.Interaction,
        player: str,
        character: str,
        reward: str,
    ) -> None:
        await interaction.response.defer(thinking=True)

        contactid = interaction.user.id
        
        data = create_prime(player, character, reward, contactid, interaction.guild)
        
        if data["status"] == "failure":
            await interaction.followup.send(content=data["output"])
        
        else:
            embed = discord.Embed(
                title=f"⚔️ Nouvelle prime",
                color=discord.Color.gold()
            )
            buffer = data["output"]
            file = discord.File(buffer, filename="wanted.png")
            embed.set_image(url="attachment://wanted.png")
            
            payer_line = f"👤 **Payeur :** <@{contactid}>\n"
            is_claimed = "❌"
            is_collected = "❌"

            embed.add_field(
                name=f"{player} ({character})",
                value=(
                    f"💰 **Récompense :** {reward}\n"
                    f"{payer_line}"
                    f"📌 **Réclamée :** {is_claimed} | **Récupérée :** {is_collected}"
                ),
                inline=False
            )

            await interaction.followup.send(embed=embed, file=file)

    @create.autocomplete('character')
    async def character_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=fighter, value=fighter)
            for fighter in charlist["fighters"]
            if current.lower() in fighter.lower()
        ][:25]  

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Create(bot))
