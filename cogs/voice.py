import discord
from discord.ext import commands
import cfg

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def private(self, ctx, *usernames):
        guild = self.bot.get_guild(cfg.GUILD_ID)
        if not guild:
            await ctx.send("❌ Ця команда працює лише в особистих повідомленнях.")
            return

        caller = guild.get_member(ctx.author.id)
        if not caller or not caller.voice or not caller.voice.channel:
            await ctx.send("❌ Ти повинен бути у голосовому каналі, щоб викликати когось.")
            return

        name_to_id = {"kl": cfg.KLEN_ID, "olg": cfg.OLEG_ID, "dim": cfg.DIMA_ID, "noi": cfg.ANDREY_ID}
        target_members = [guild.get_member(name_to_id[username.lower()]) for username in usernames if username.lower() in name_to_id]

        duo_channel = guild.get_channel(cfg.CHANNEL_1_ID)
        available_channels = [ch for ch in guild.voice_channels if len(ch.members) == 0]
        target_channel = duo_channel if duo_channel and len(duo_channel.members) == 0 else (available_channels[0] if available_channels else None)

        if not target_channel:
            await ctx.send("❌ Немає доступних вільних каналів.")
            return

        await caller.move_to(target_channel)
        for member in target_members:
            await member.move_to(target_channel)
        await ctx.send(f"✅ {', '.join(usernames)} переміщено до {target_channel.name}.")

    @commands.command(aliases=["fullgrade"])
    async def elitegrade(self, ctx):
        guild = self.bot.get_guild(cfg.GUILD_ID)
        channel_1 = guild.get_channel(cfg.CHANNEL_1_ID)
        channel_2 = guild.get_channel(cfg.CHANNEL_2_ID)
        if channel_1 and channel_2:
            for member in channel_1.members:
                await member.move_to(channel_2)
            await ctx.send(f"✅ Учасники переміщені у {channel_2.name}.")

    @commands.command()
    async def duograde(self, ctx):
        guild = self.bot.get_guild(cfg.GUILD_ID)
        channel_1 = guild.get_channel(cfg.CHANNEL_1_ID)
        channel_2 = guild.get_channel(cfg.CHANNEL_2_ID)
        if channel_1 and channel_2:
            for member in channel_2.members:
                await member.move_to(channel_1)
            await ctx.send(f"✅ Учасники переміщені у {channel_1.name}")


async def setup(bot):
    await bot.add_cog(Voice(bot))
