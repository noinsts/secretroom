import os

import discord
from discord.ext import commands

import cfg  # Файл з GUILD_ID, ADMINS_IDS і NOTIFICATION_CHAT_ID

from dotenv import load_dotenv

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.dm_messages = True
intents.members = True  # Потрібно для отримання списку учасників
intents.message_content = True  # Додаємо, щоб бот міг надсилати повідомлення

bot = commands.Bot(command_prefix="!", intents=intents)


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
        print(f"📢 Войс {voice_channel.name}: {len(members)} учасників")

        if len(members) >= 2:
            admin_in_voice = None
            for admin_id in cfg.ADMINS_IDS:
                admin = guild.get_member(admin_id)
                if admin and admin in members:
                    admin_in_voice = admin
                    break

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
                    response = await bot.wait_for("message", check=check, timeout=60)  # 60 сек очікування
                    reason = response.content.strip()
                except TimeoutError:
                    reason = "❌ Адмін не відповів на запит."

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
