import discord
from discord.ext import commands
from collections import defaultdict
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

    @commands.command()
    async def stats(self, ctx):
        guild = self.bot.get_guild(cfg.GUILD_ID)
        if not guild:
            await ctx.send("Не вдалося знайти сервер.")
            return

        activities = defaultdict(list)
        voice_channels = defaultdict(list)

        for member in guild.members:
            if member.bot:
                continue  # Пропускаємо ботів

            activity_name = "```Онлайн```"
            if member.activity:
                if isinstance(member.activity, discord.Game):
                    activity_name = f"```{member.activity.name}```"
                elif isinstance(member.activity, discord.Streaming):
                    activity_name = f"```{member.activity.name}``` (📺 Стрім)"
                elif isinstance(member.activity, discord.Spotify):
                    activity_name = f"```Spotify: {member.activity.title}```"
                elif isinstance(member.activity, discord.Activity) and member.activity.name:
                    activity_name = f"```{member.activity.name}```"

            if member.status in (discord.Status.online, discord.Status.idle, discord.Status.dnd):
                activities[activity_name].append(member.display_name)

            if member.voice and member.voice.channel:
                voice_channels[member.voice.channel.name].append(member.display_name)

        # Формуємо текст
        text = "**📡 Люди онлайн:**\n\n"
        if activities:
            for activity, users in activities.items():
                text += f"{activity}\n" + "\n".join(f"➤ {user}" for user in users) + "\n"
        else:
            text += "Немає онлайн користувачів.\n"

        text += "\n**🔊 Люди в голосових каналах:**\n"
        if voice_channels:
            for channel, users in voice_channels.items():
                text += f"**{channel}**\n" + ", ".join(users) + "\n"
        else:
            text += "Немає учасників у голосових каналах."

        await ctx.send(text)


async def setup(bot):
    await bot.add_cog(Chat(bot))
