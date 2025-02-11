import discord
import asyncio
from discord.ext import commands
import cfg
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await send_console_input()


async def send_console_input():
    await bot.wait_until_ready()
    channel = bot.get_channel(cfg.MAIN_CHAT_ID)
    if channel is None:
        print("Помилка: Канал не знайдено.")
        return

    while not bot.is_closed():
        msg = await asyncio.to_thread(input, "Введіть повідомлення: ")
        if msg.lower() == "exit":
            await bot.close()
            break
        await channel.send(msg)

if __name__ == '__main__':
    load_dotenv()
    bot.run(os.getenv('TOKEN'))
