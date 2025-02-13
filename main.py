import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Завантажуємо Cogs
cogs = ["cogs.roles", "cogs.voice", "cogs.chat", "cogs.moderation"]


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    for cog in cogs:
        await bot.load_extension(cog)


if __name__ == '__main__':
    load_dotenv()
    bot.run(os.getenv('TOKEN'))
