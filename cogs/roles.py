import discord
from discord.ext import commands
import cfg


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def eliteup(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, id=cfg.ELITE_ROLE_ID)
        if role:
            await member.add_roles(role)
            await ctx.send(f'Елітку надано користувачу {member.mention}')
        else:
            await ctx.send('Проблемка... попробуй знову.')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def elitedown(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, id=cfg.ELITE_ROLE_ID)
        if role:
            await member.remove_roles(role)
            await ctx.send(f'Елітку забрано у {member.mention}')
        else:
            await ctx.send('Проблемка... попробуй знову.')


async def setup(bot):
    await bot.add_cog(Roles(bot))