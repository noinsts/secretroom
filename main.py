import os
import discord
from discord.ext import commands
import cfg
from dotenv import load_dotenv


intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.id == cfg.SOURCE_CHANNEL_ID:
        messages = []
        for admin_id in cfg.ADMIN_IDS:
            admin = bot.get_user(admin_id)
            if admin:
                msg = await admin.send(f'Чи можна перемістити {member.display_name}?')
                await msg.add_reaction("✅")
                await msg.add_reaction("❌")
                messages.append((msg, admin))

        def check(reaction, user):
            return user.id in cfg.ADMIN_IDS and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)
            if str(reaction.emoji) == "✅":
                destination = discord.utils.get(member.guild.voice_channels, id=cfg.DESTINATION_CHANNEL_ID)
                if destination:
                    await member.move_to(destination)
            elif str(reaction.emoji) == "❌":
                if member.voice and member.voice.channel:
                    await member.move_to(None)  # Кікає з голосового каналу
        except:
            for msg, admin in messages:
                await admin.send("Час на відповідь минув. Перекидання скасовано.")

    if after.channel and after.channel.id == cfg.WAITING_CHANNEL_ID:
        for admin_id in cfg.ADMIN_IDS:
            admin = bot.get_user(admin_id)
            if admin:
                await admin.send(f'{member.display_name} зайшов у канал очікування!')


@bot.command()
@commands.has_permissions(administrator=True)
async def eliteup(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, id=cfg.ELITE_ROLE_ID)
    if role:
        await member.add_roles(role)
        await ctx.send(f'Елітку надано користувачу {member.mention}')
    else:
        await ctx.send('Проблемка... попробуй знову.')


@bot.command()
@commands.has_permissions(administrator=True)
async def elitedown(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, id=cfg.ELITE_ROLE_ID)
    if role:
        await member.remove_roles(role)
        await ctx.send(f'Елітку забрано у {member.mention}')
    else:
        await ctx.send('Проблемка... попробуй знову.')


@bot.command()
async def connect(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

        if voice_client and voice_client.is_connected():
            await voice_client.move_to(channel)
        else:
            await channel.connect()

        await ctx.send(f'Підключився до {channel.name}')
    else:
        await ctx.send('Ви повинні бути у голосовому каналі, щоб викликати цю команду!')


@bot.command(aliases=["fullgrade"])
async def elitegrade(ctx):
    """Переміщує всіх з CHANNEL_1 у CHANNEL_2"""
    guild = bot.get_guild(cfg.GUILD_ID)
    channel_1 = guild.get_channel(cfg.CHANNEL_1_ID)
    channel_2 = guild.get_channel(cfg.CHANNEL_2_ID)

    if channel_1 and channel_2:
        for member in channel_1.members:
            await member.move_to(channel_2)
        await ctx.send(f"✅ Учасники переміщені у `{channel_2.name}`.")


@bot.command()
async def duograde(ctx):
    """Переміщує всіх з CHANNEL_2 у CHANNEL_1"""
    guild = bot.get_guild(cfg.GUILD_ID)
    channel_1 = guild.get_channel(cfg.CHANNEL_1_ID)
    channel_2 = guild.get_channel(cfg.CHANNEL_2_ID)

    if channel_1 and channel_2:
        for member in channel_2.members:
            await member.move_to(channel_1)
        await ctx.send(f"✅ Учасники переміщені у `{channel_1.name}`")


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


@bot.command(aliases=["callme"])
async def private(ctx, *usernames):
    """Переміщує викликача і вказаних користувачів у вільний голосовий канал."""
    guild = bot.get_guild(cfg.GUILD_ID)

    # Перевірка, чи команда виконана в особистих повідомленнях
    if not guild:
        await ctx.send("❌ Ця команда працює лише в особистих повідомленнях.")
        return

    caller = guild.get_member(ctx.author.id)

    if not caller or not caller.voice or not caller.voice.channel:
        await ctx.send("❌ Ти повинен бути у голосовому каналі, щоб викликати когось.")
        return

    # Отримання ID користувачів з cfg
    name_to_id = {
        "kl": cfg.KLEN_ID,
        "olg": cfg.OLEG_ID,
        "dim": cfg.DIMA_ID,
        "noi": cfg.ANDREY_ID
    }

    target_members = []

    for username in usernames:
        if username.lower() in name_to_id:
            target_id = name_to_id[username.lower()]
            target_member = guild.get_member(target_id)

            if not target_member or not target_member.voice or not target_member.voice.channel:
                await ctx.send(f"❌ `{username}` не в голосовому каналі.")
                return

            target_members.append(target_member)
        else:
            await ctx.send(f"❌ `{username}` не знайдено в списку.")
            return

    # Отримуємо канал duo або інший вільний канал
    duo_channel = guild.get_channel(cfg.CHANNEL_1_ID)
    available_channels = [
        ch for ch in guild.voice_channels if len(ch.members) == 0
    ]

    target_channel = duo_channel if duo_channel and len(duo_channel.members) == 0 else (
        available_channels[0] if available_channels else None)

    if not target_channel:
        await ctx.send("❌ Немає доступних вільних каналів.")
        return

    # Переміщуємо всіх
    await caller.move_to(target_channel)
    for member in target_members:
        await member.move_to(target_channel)

    await ctx.send(f"✅ `{', '.join(usernames)}` переміщено до `{target_channel.name}`.")


@bot.command(aliases=["кс"])
async def cs(ctx, *args):
    """Тегає вибраних людей або всіх (окрім того, хто викликав) для гри в CS"""
    guild = bot.get_guild(cfg.GUILD_ID)

    if ctx.channel.id != cfg.MAIN_CHAT_ID:
        await ctx.send("❌ Цю команду можна використовувати тільки у головному чаті.")
        return

    # Словник із ніками та їхніми ID
    player_ids = {
        "kl": cfg.KLEN_ID,
        "olg": cfg.OLEG_ID,
        "dim": cfg.DIMA_ID,
        "and": cfg.ANDREY_ID,
    }

    # Якщо написали "cs full" – беремо всіх, окрім того, хто викликав
    if "full" in args:
        mentions = [f"<@{pid}>" for name, pid in player_ids.items() if pid != ctx.author.id]
    else:
        mentions = [f"<@{player_ids[name]}>" for name in args if name in player_ids]

    if not mentions:
        await ctx.send("❌ Не знайдено жодного користувача для тегання.")
        return

    mention_text = " ".join(mentions)
    await ctx.send(f"🎮 {ctx.author.mention} зве {mention_text} в CS!")


@bot.command(aliases=["войс"])
async def voice(ctx, *args):
    """Тегає вибраних людей або всіх (окрім того, хто викликав) заклику в войс"""
    guild = bot.get_guild(cfg.GUILD_ID)

    if ctx.channel.id != cfg.MAIN_CHAT_ID:
        await ctx.send("❌ Цю команду можна використовувати тільки у головному чаті.")
        return

    # Словник із ніками та їхніми ID
    player_ids = {
        "kl": cfg.KLEN_ID,
        "olg": cfg.OLEG_ID,
        "dim": cfg.DIMA_ID,
        "and": cfg.ANDREY_ID,
    }

    # Якщо написали "voice full" – беремо всіх, окрім того, хто викликав
    if "full" in args:
        mentions = [f"<@{pid}>" for name, pid in player_ids.items() if pid != ctx.author.id]
    else:
        mentions = [f"<@{player_ids[name]}>" for name in args if name in player_ids]

    if not mentions:
        await ctx.send("❌ Не знайдено жодного користувача для тегання.")
        return

    mention_text = " ".join(mentions)

    # Перевіряємо, чи викликач у войсі
    if ctx.author.voice and ctx.author.voice.channel:
        channel_name = ctx.author.voice.channel.name
        await ctx.send(f"🎮 {ctx.author.mention} зве {mention_text} в войс! (Чекає у **{channel_name}**)")
    else:
        await ctx.send(f"🎮 {ctx.author.mention} зве {mention_text} в войс!")


if __name__ == '__main__':
    load_dotenv()
    bot.run(os.getenv('TOKEN'))
