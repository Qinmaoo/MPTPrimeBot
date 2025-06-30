import discord
from discord.ext import commands
import aiohttp
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

class MyBot(commands.Bot):

	def __init__(self):
		super().__init__(
			command_prefix="$",
			intents=discord.Intents.all()
		)

		self.initial_extensions = ["cogs.create", "cogs.primes"]
	
	async def setup_hook(self):
		self.session = aiohttp.ClientSession()

		for ext in self.initial_extensions:
			try:
				await self.load_extension(ext)
				print(f"Extension chargée : {ext}")
			except Exception as e:
				print(f"Erreur lors du chargement de {ext}: {e}")

		try:
			global_commands = await self.tree.sync()
			print(f"{len(global_commands)} commandes synchronisées globalement")
		except Exception as e:
			print(f"Erreur lors de la synchronisation : {e}")

	async def on_ready(self):
		for guild in self.guilds:
			print(f"Connecté à : {guild.name} (ID: {guild.id})")

	async def close(self):
		await super().close()
		await self.session.close()

bot = MyBot()
bot.run(BOT_TOKEN)