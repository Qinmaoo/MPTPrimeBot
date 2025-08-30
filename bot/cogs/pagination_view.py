import discord
from discord.ui import View, Button
from cogs.utils import create_message_classic
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
        
        # self.add_item(self.prev_button)
        self.add_item(self.next_button)

    def build_embed(self):
        embed = discord.Embed(title=self.embed_title, color=discord.Color.gold())

        start = self.page * 10
        end = start + 10
        primes_to_show = self.data[start:end]

        for prime in primes_to_show:
            create_message_classic(prime, embed)

        embed.set_footer(text=f"Page {self.page + 1} / {self.max_pages + 1}")
        return embed

    async def send(self):
        embed = self.build_embed()
        self.message = await self.interaction.followup.send(embed=embed, view=self)

    async def prev_page(self, interaction: discord.Interaction):
        if self.page > 0:
            self.page -= 1
            self.add_item(self.next_button)
            if self.page == 0:
                self.remove_item(self.prev_button)
            await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def next_page(self, interaction: discord.Interaction):
        if self.page < self.max_pages:
            self.page += 1
            self.add_item(self.prev_button)
            if self.page == self.max_pages:
                self.remove_item(self.next_button)
            await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def on_timeout(self):
        if self.message:
            await self.message.edit(view=None)
