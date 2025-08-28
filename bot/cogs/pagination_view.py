import discord
from discord.ui import View, Button

class PrimesPaginationView(discord.ui.View):
    def __init__(self, data, embed_title, interaction: discord.Interaction):
        super().__init__(timeout=120)
        self.data = data
        self.page = 0
        self.embed_title = embed_title
        self.interaction = interaction
        self.message = None
        self.max_pages = (len(data) - 1) // 10

        self.prev_button = discord.ui.Button(label="⬅️ Précédent", style=discord.ButtonStyle.secondary)
        self.next_button = discord.ui.Button(label="➡️ Suivant", style=discord.ButtonStyle.secondary)

        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page

        self.add_item(self.prev_button)
        self.add_item(self.next_button)

    def build_embed(self):
        embed = discord.Embed(title=self.embed_title, color=discord.Color.gold())

        start = self.page * 10
        end = start + 10
        primes_to_show = self.data[start:end]

        for prime in primes_to_show:
            contactid = prime.get('player_to_pay_id')
            contactid_claimer = prime.get("player_who_claimed_id")
            # contact_display = f"<@{contactid}>" if contactid else prime.get('player_to_pay', "Inconnu")
            paying_line = f"👤 **Payeur :** <@{contactid}>\n"
            is_claimed = "✅" if prime["is_claimed"] else "❌"
            is_collected = "✅" if prime["collected"] else "❌"
            claim_line = ""
            if is_claimed == "✅":
                print("is claimed")
                print(f"prime: {prime}")
                contactid_claimer = prime.get("player_who_claimed_id")
                if contactid_claimer:
                    claim_line += f"📌 **Réclamée {is_claimed} par :** <@{contactid_claimer}>\n"
            else:
                print("is not claimed")
                claim_line += f"📌 **Réclamée :** {is_claimed}\n"
            embed.add_field(
                name=f"{prime['player_wanted']} ({prime['characters_played']})",
                value=(
                    f"💰 **Récompense :** {prime['reward']}\n"
                    f"{paying_line}"
                    f"{claim_line}"
                    f"**Récupérée :** {is_collected}"
                ),
                inline=False
            )

        embed.set_footer(text=f"Page {self.page + 1} / {self.max_pages + 1}")
        return embed

    async def send(self):
        embed = self.build_embed()
        self.message = await self.interaction.followup.send(embed=embed, view=self)

    async def prev_page(self, interaction: discord.Interaction):
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def next_page(self, interaction: discord.Interaction):
        if self.page < self.max_pages:
            self.page += 1
            await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def on_timeout(self):
        if self.message:
            await self.message.edit(view=None)
