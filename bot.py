import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from services.handlers import register_handlers
from dotenv import load_dotenv
import os

load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

register_handlers(dp, bot)

async def main():
    print("🤖 Карьерный советник запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())