import os

import discord
from discord.ext import commands

import cfg  # Файл з GUILD_ID, ADMINS_IDS і NOTIFICATION_CHAT_ID

from dotenv import load_dotenv

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.dm_messages = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

voice_notified = {}  # Словник для відстеження повідомлених каналів


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


@bot.event
async def on_voice_state_update(member, before, after):
    print(f"🎤 Voice state update: {member.display_name} (before={before.channel}, after={after.channel})")

    guild = bot.get_guild(cfg.GUILD_ID)
    if not guild:
        print("❌ Гільдія не знайдена!")
        return

    notification_channel = guild.get_channel(cfg.NOTIFICATION_CHAT_ID)
    if not notification_channel:
        print("❌ Помилка: Канал для сповіщень не знайдено!")
        return

    for voice_channel in guild.voice_channels:
        members = [m for m in voice_channel.members if not m.bot]

        # Перевірка, чи потрібно оновлювати стан
        if len(members) < 2:
            voice_notified.pop(voice_channel.id, None)
            continue

        if voice_notified.get(voice_channel.id) == set(members):
            continue  # Якщо склад учасників не змінився, не повідомляємо повторно

        voice_notified[voice_channel.id] = set(members)  # Оновлюємо стан

        admin_in_voice = next((guild.get_member(admin_id) for admin_id in cfg.ADMINS_IDS if guild.get_member(admin_id) in members), None)

        member_names = ", ".join(m.display_name for m in members)

        if admin_in_voice:
            print(f"📩 Запитуємо причину у {admin_in_voice.display_name} в {voice_channel.name}")
            try:
                await admin_in_voice.send(
                    f"🔎 Ти в войсі **{voice_channel.name}** з {member_names}. Яка причина збору?"
                )
            except discord.Forbidden:
                print(f"❌ Не вдалося написати в ДМ {admin_in_voice.display_name}")
                return

            def check(msg):
                return msg.author == admin_in_voice and isinstance(msg.channel, discord.DMChannel)

            try:
                response = await bot.wait_for("message", check=check, timeout=60)
                reason = response.content.strip()
                if not reason:
                    return  # Якщо адмін просто нічого не написав, нічого не повідомляємо
            except Exception:
                return  # Якщо час вийшов або помилка, просто не відправляємо повідомлення

            message = f"⚠️ У голосовому каналі **{voice_channel.name}** зібралися: {member_names}.\nПричина: {reason}"
            print(f"✅ Надсилаємо повідомлення: {message}")
            await notification_channel.send(message)
            return

        # Якщо адмінів немає, бот пише в чат без запиту
        message = f"⚠️ У голосовому каналі **{voice_channel.name}** зібралися: {member_names}."
        try:
            await notification_channel.send(message)
            print(f"✅ Повідомлення надіслано: {message}")
        except discord.Forbidden:
            print("❌ Бот не має прав писати в канал сповіщень!")


if __name__ == "__main__":
    load_dotenv()
    bot.run(os.getenv("TOKEN"))
