import discord
from discord.ui import View, button, Button
import os, json
from cogs.make_poster import create_wanted_poster
from io import BytesIO

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
        self.payer_id = int(current_state["player_to_pay_id"])
        
        if not self.claimed:
            self.claim_button = Button(label="Claim", style=discord.ButtonStyle.green)
            self.claim_button.callback = self.claim_callback
            self.add_item(self.claim_button)
        elif self.claimed and not self.collected:
            self.collect_button = Button(label="Récupérer", style=discord.ButtonStyle.blurple)
            self.collect_button.callback = self.collect_callback
            self.add_item(self.collect_button)
            
        if author_id == self.payer_id:
            self.delete_button = Button(label="🗑 Supprimer", style=discord.ButtonStyle.red)
            self.delete_button.callback = self.delete_callback
            self.add_item(self.delete_button)

    async def claim_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Tu ne peux pas claim cette prime.", ephemeral=True)
            return

        contactid_claimer = interaction.user.id

        primes = load_primes()
        prime = None
        for p in primes:
            if p["id"] == self.prime_id:
                p["is_claimed"] = True
                p["player_who_claimed_id"] = str(contactid_claimer)
                prime = p
                break
        with open(parentPath + '/primes.json', 'w', encoding='utf-8') as f:
            json.dump(primes, f, indent=4, ensure_ascii=False)

        is_claimed = "✅"
        is_collected = "✅" if prime["collected"] else "❌"
        contactid = prime["player_to_pay_id"]
        payer_line = f"👤 **Payeur :** <@{contactid}>\n"
        claim_line = f"📌 **Réclamée :** {is_claimed} par :** <@{contactid_claimer}>\n"

        updated_embed = discord.Embed(
            title=interaction.message.embeds[0].title,
            color=discord.Color.gold()
        )
        print(prime)
        updated_embed.add_field(
            name=f"{prime['player_wanted']} ({prime['characters_played']})",
            value=(
                f"💰 **Récompense :** {prime['reward']}\n"
                f"{payer_line}"
                f"{claim_line}"
                f"**Récupérée :** {is_collected}"
            ),
            inline=False
        )
        
        await interaction.message.delete()
        
        guild = interaction.guild
        member = guild.get_member(int(contactid))
        contact_display = member.display_name
        buffer = create_wanted_poster(
            prime['player_wanted'],
            prime["characters_played"],
            prime["reward"],
            contact_display
        )
        notify_string = f"<@{contactid}>, ta prime sur **{prime['player_wanted']}** a été claim par **{interaction.user.display_name}**! Va raquer {prime['reward']} :index_pointing_at_the_viewer:"
        file = discord.File(buffer, filename="wanted.png")
        updated_embed.set_image(url="attachment://wanted.png")

        await interaction.channel.send(content=notify_string, embed=updated_embed, file=file)
        


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
        contactid_claimer = prime.get("player_who_claimed_id")
        payer_line = f"👤 **Payeur :** <@{contactid}>\n"
        claim_line = f"📌 **Réclamée :** {is_claimed} par : <@{contactid_claimer}>\n"

        updated_embed = discord.Embed(
            title=interaction.message.embeds[0].title,
            color=discord.Color.gold()
        )
        updated_embed.add_field(
            name=f"{prime['player_wanted']} ({prime['characters_played']})",
            value=(
                f"💰 **Récompense :** {prime['reward']}\n"
                f"{payer_line}"
                f"{claim_line}"
                f"**Récupérée :** {is_collected}"
            ),
            inline=False
        )

        await interaction.response.edit_message(embed=updated_embed, view=None)

    async def delete_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.payer_id:
            await interaction.response.send_message("❌ Tu n'es pas le payeur de cette prime.", ephemeral=True)
            return

        primes = load_primes()
        primes = [p for p in primes if p["id"] != self.prime_id]

        with open(parentPath + '/primes.json', 'w', encoding='utf-8') as f:
            json.dump(primes, f, indent=4, ensure_ascii=False)

        await interaction.response.edit_message(content="🗑 La prime a été supprimée par le payeur.", embed=None, attachments=[], view=None)