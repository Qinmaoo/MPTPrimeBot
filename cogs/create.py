import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from typing import Optional
import sys, io

parentPath = os.path.dirname(os.path.abspath(__file__))


def create_prime(player, character, reward, contact):
    pass

class Create(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
    
    @app_commands.command(
        name = "create",
        description = "Créer une prime"
    )
    
    @app_commands.describe(
        player = "Le joueur wanted",
        character = "Son personnage à battre",
        reward = "La récompense associée",
        contact = "La personne qui paye"
    )

    @app_commands.choices(
    character = [app_commands.Choice(name=gamemetadata["display_name"], value=gameid) for gameid, gamemetadata in game_list.items()],
)
    
    async def getbx(
        self,
        interaction: discord.Interaction,
        player: str,
        character: app_commands.Choice[str],
        reward: str,
        contact: Optional[str] = None
    ) -> None:
        
        await interaction.response.defer(thinking=True)

        id = interaction.user.id
        character = character.value
        contact = contact.value if contact else interaction.user.name
        
        data = create_prime(player, character, reward, contact)
            
        buffer = io.BytesIO()
        data.save(buffer, format="PNG")
        buffer.seek(0)

        file = discord.File(buffer, filename="image.png")
        embed = discord.Embed(
            title=f"Nouvelle prime: {player} ({character}) - {reward}"
        )
        embed.set_image(url="attachment://image.png")

        await interaction.followup.send(embed=embed, files=[file])


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Create(bot))