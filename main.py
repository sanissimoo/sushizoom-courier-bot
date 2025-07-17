import asyncio
from aiogram import Bot

import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def main():
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text="✅ Бот успішно підключений до групи!")
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
