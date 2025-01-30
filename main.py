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

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


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
        try:
            await member.add_roles(role)
            await ctx.send(f'Роль "Еліт" додано користувачу {member.mention}')
        except Exception as e:
            await ctx.send(f'Виникла помилка: {e}')
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


bot.run(TOKEN)