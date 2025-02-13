import discord
from discord.ext import commands
import cfg


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """COMMANDS HERE"""


async def setup(bot):
    await bot.add_cog(Moderation(bot))
