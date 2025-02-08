import os

import discord
from discord.ext import commands
import cfg
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
GUILD_ID = cfg.GUILD_ID  # ID серверу
SOURCE_CHANNEL_ID = cfg.SOURCE_CHANNEL_ID  # Канал, з якого перекидати
DESTINATION_CHANNEL_ID = cfg.DESTINATION_CHANNEL_ID  # Канал, куди перекидати
WAITING_CHANNEL_ID = cfg.WAITING_CHANNEL_ID  # Канал очікування
ADMIN_IDS = cfg.ADMIN_IDS  # Список ID адмінів
ELITE_ROLE_ID = cfg.ELITE_ROLE_ID  # ID ролі "Еліт"
CHANNEL_1_ID = cfg.CHANNEL_1_ID  # ID голосового каналу 1
CHANNEL_2_ID = cfg.CHANNEL_2_ID  # ID голосового каналу 2

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

user_last_channel = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.id == SOURCE_CHANNEL_ID:
        messages = []
        for admin_id in ADMIN_IDS:
            admin = bot.get_user(admin_id)
            if admin:
                msg = await admin.send(f'Чи можна перемістити {member.display_name}?')
                await msg.add_reaction("✅")
                await msg.add_reaction("❌")
                messages.append((msg, admin))

        def check(reaction, user):
            return user.id in ADMIN_IDS and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)
            if str(reaction.emoji) == "✅":
                destination = discord.utils.get(member.guild.voice_channels, id=DESTINATION_CHANNEL_ID)
                if destination:
                    await member.move_to(destination)
            elif str(reaction.emoji) == "❌":
                if member.voice and member.voice.channel:
                    await member.move_to(None)  # Кікає з голосового каналу
        except:
            for msg, admin in messages:
                await admin.send("Час на відповідь минув. Перекидання скасовано.")

    if after.channel and after.channel.id == WAITING_CHANNEL_ID:
        for admin_id in ADMIN_IDS:
            admin = bot.get_user(admin_id)
            if admin:
                await admin.send(f'{member.display_name} зайшов у канал очікування!')


@bot.command()
@commands.has_permissions(administrator=True)
async def eliteup(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, id=ELITE_ROLE_ID)
    if role:
        await member.add_roles(role)
        await ctx.send(f'Роль "Еліт" додано користувачу {member.mention}')
    else:
        await ctx.send('Роль "Еліт" не знайдено.')


@bot.command()
@commands.has_permissions(administrator=True)
async def elitedown(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, id=ELITE_ROLE_ID)
    if role:
        await member.remove_roles(role)
        await ctx.send(f'Роль "Еліт" забрано у {member.mention}')
    else:
        await ctx.send('Роль "Еліт" не знайдено.')


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


@bot.command()
async def elitegrade(ctx):
    """Переміщує всіх з CHANNEL_1 у CHANNEL_2"""
    guild = bot.get_guild(GUILD_ID)
    channel_1 = guild.get_channel(CHANNEL_1_ID)
    channel_2 = guild.get_channel(CHANNEL_2_ID)

    if channel_1 and channel_2:
        for member in channel_1.members:
            await member.move_to(channel_2)
        await ctx.send("✅ Учасники переміщені у канал 2.")


@bot.command()
async def duograde(ctx):
    """Переміщує всіх з CHANNEL_2 у CHANNEL_1"""
    guild = bot.get_guild(GUILD_ID)
    channel_1 = guild.get_channel(CHANNEL_1_ID)
    channel_2 = guild.get_channel(CHANNEL_2_ID)

    if channel_1 and channel_2:
        for member in channel_2.members:
            await member.move_to(channel_1)
        await ctx.send("✅ Учасники повернені у канал 1.")


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


@bot.command(aliases=["callme"])
async def private(ctx, *usernames):
    """Переміщує викликача і вказаних користувачів у вільний голосовий канал."""
    guild = bot.get_guild(GUILD_ID)

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
        "noi": cfg.AND_ID
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
    duo_channel = guild.get_channel(CHANNEL_1_ID)
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


@bot.command()
async def retu(ctx):
    """Повертає всіх користувачів назад у їхні попередні голосові канали"""
    guild = bot.get_guild(GUILD_ID)

    if not guild:
        await ctx.send("❌ Ця команда працює лише на сервері.")
        return

    caller = guild.get_member(ctx.author.id)

    if not caller or not caller.voice or not caller.voice.channel:
        await ctx.send("❌ Ти маєш бути в голосовому каналі, щоб повернути всіх назад.")
        return

    moved_users = [uid for uid, _ in user_last_channel.items() if uid in [m.id for m in caller.voice.channel.members]]

    if not moved_users:
        await ctx.send("❌ Немає користувачів, яких можна повернути.")
        return

    for user_id in moved_users:
        member = guild.get_member(user_id)
        last_channel_id = user_last_channel.get(user_id)

        if member and last_channel_id:
            last_channel = guild.get_channel(last_channel_id)

            if last_channel and isinstance(last_channel, discord.VoiceChannel):
                await member.move_to(last_channel)
                await ctx.send(f"🔄 {member.display_name} повернуто в `{last_channel.name}`.")
            else:
                await ctx.send(f"❌ Канал для {member.display_name} більше не існує.")

            # Видаляємо запис, щоб уникнути дублювання
            del user_last_channel[user_id]



bot.run(TOKEN)
