import discord
from discord.ext import commands
import cfg


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Barak Obama!")

    @commands.command(aliases=["кс"])
    async def cs(self, ctx, *args):
        guild = self.bot.get_guild(cfg.GUILD_ID)
        if ctx.channel.id != cfg.MAIN_CHAT_ID:
            await ctx.send("❌ Цю команду можна використовувати тільки у головному чаті.")
            return

        player_ids = {"kl": cfg.KLEN_ID, "olg": cfg.OLEG_ID, "dim": cfg.DIMA_ID, "and": cfg.ANDREY_ID}
        mentions = [f"<@{player_ids[name]}>" for name in args if name in player_ids]

        if not mentions:
            await ctx.send("❌ Не знайдено жодного користувача для тегання.")
            return

        mention_text = " ".join(mentions)
        await ctx.send(f"🎮 {ctx.author.mention} зве {mention_text} в CS!")

    @commands.command(aliases=["войс"])
    async def voice(self, ctx, *args):
        guild = self.bot.get_guild(cfg.GUILD_ID)
        if ctx.channel.id != cfg.MAIN_CHAT_ID:
            await ctx.send("❌ Цю команду можна використовувати тільки у головному чаті.")
            return

        player_ids = {"kl": cfg.KLEN_ID, "olg": cfg.OLEG_ID, "dim": cfg.DIMA_ID, "and": cfg.ANDREY_ID}
        mentions = [f"<@{player_ids[name]}>" for name in args if name in player_ids]

        if not mentions:
            await ctx.send("❌ Не знайдено жодного користувача для тегання.")
            return

        mention_text = " ".join(mentions)
        await ctx.send(f"🎮 {ctx.author.mention} зве {mention_text} в войс!")

    @commands.command(name="helpme")
    async def help_command(self, ctx):
        """Відправляє вміст README.md у чат"""
        try:
            with open("HELPME.md", "r", encoding="utf-8") as file:
                content = file.read()

            if len(content) > 2000:
                content = content[:1997] + "..."  # Обрізаємо, щоб вмістилося в одне повідомлення

            await ctx.send(content)
        except Exception as e:
            await ctx.send(f"❌ Помилка: {e}")


async def setup(bot):
    await bot.add_cog(Chat(bot))
