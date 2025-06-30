import discord
from discord.ui import View, button, Button
import os, json

parentPath = os.path.dirname(os.path.abspath(__file__))

with open(parentPath + '/charlist.json') as f:
    charlist = json.load(f)

def load_primes():
    with open(parentPath + '/primes.json', 'r', encoding='utf-8') as f:
        primes = json.load(f)
    return primes

class ClaimView(View):
    def __init__(self, prime_id: int, current_state: dict, author_id: int):
        super().__init__(timeout=None)
        self.prime_id = prime_id
        self.claimed = current_state["is_claimed"]
        self.collected = current_state["collected"]
        self.author_id = author_id

        if not self.claimed:
            self.claim_button = Button(label="Claim", style=discord.ButtonStyle.green)
            self.claim_button.callback = self.claim_callback
            self.add_item(self.claim_button)
        elif self.claimed and not self.collected:
            self.collect_button = Button(label="Récupérer", style=discord.ButtonStyle.blurple)
            self.collect_button.callback = self.collect_callback
            self.add_item(self.collect_button)

    async def claim_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Tu ne peux pas claim cette prime.", ephemeral=True)
            return

        # Mise à jour dans le JSON
        primes = load_primes()
        prime = None
        for p in primes:
            if p["id"] == self.prime_id:
                p["is_claimed"] = True
                prime = p
                break
        with open(parentPath + '/primes.json', 'w', encoding='utf-8') as f:
            json.dump(primes, f, indent=4, ensure_ascii=False)

        # Reconstruction de l'embed
        is_claimed = "✅"
        is_collected = "✅" if prime["collected"] else "❌"
        contactid = prime["player_to_pay_id"]
        payer_line = f"👤 **Payeur :** <@{contactid}>\n"

        updated_embed = discord.Embed(
            title=interaction.message.embeds[0].title,
            color=discord.Color.gold()
        )
        updated_embed.add_field(
            name=f"{prime['player_wanted']} ({prime['characters_played']})",
            value=(
                f"💰 **Récompense :** {prime['reward']}\n"
                f"{payer_line}"
                f"📌 **Réclamée :** {is_claimed} | **Récupérée :** {is_collected}"
            ),
            inline=False
        )

        await interaction.response.edit_message(embed=updated_embed, view=None)
        await interaction.followup.send(f"<@{contactid}>, ta prime sur **{prime['player_wanted']}** a été claim par **{interaction.user.display_name}**! Va raquer {prime['reward']} :index_pointing_at_the_viewer:")


    async def collect_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Tu ne peux pas récupérer cette prime.", ephemeral=True)
            return

        # Mise à jour dans le JSON
        primes = load_primes()
        prime = None
        for p in primes:
            if p["id"] == self.prime_id:
                p["collected"] = True
                prime = p
                break
        with open(parentPath + '/primes.json', 'w', encoding='utf-8') as f:
            json.dump(primes, f, indent=4, ensure_ascii=False)

        # Reconstruction de l'embed
        is_claimed = "✅"
        is_collected = "✅"
        contactid = prime["player_to_pay_id"]
        payer_line = f"👤 **Payeur :** <@{contactid}>\n"

        updated_embed = discord.Embed(
            title=interaction.message.embeds[0].title,
            color=discord.Color.gold()
        )
        updated_embed.add_field(
            name=f"{prime['player_wanted']} ({prime['characters_played']})",
            value=(
                f"💰 **Récompense :** {prime['reward']}\n"
                f"{payer_line}"
                f"📌 **Réclamée :** {is_claimed} | **Récupérée :** {is_collected}"
            ),
            inline=False
        )

        await interaction.response.edit_message(embed=updated_embed, view=None)

