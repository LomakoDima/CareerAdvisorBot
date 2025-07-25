import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from services.handlers import register_handlers
from services.ai_service import is_openai_available
from dotenv import load_dotenv
import os

# Загружаем переменные окружения
load_dotenv()

# Получаем токены
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Проверка наличия токенов
if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN не найден в .env файле!")
    exit(1)

if not OPENAI_KEY:
    logger.warning("⚠️ OPENAI_API_KEY не найден. ИИ-режим будет недоступен.")

# Создание бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрация обработчиков
register_handlers(dp, bot)


async def on_startup():
    """Функция выполняется при запуске бота"""
    logger.info("🤖 Карьерный советник v2.0 запускается...")

    # Проверяем доступность OpenAI
    ai_available = await is_openai_available()
    if ai_available:
        logger.info("✅ OpenAI API доступен - ИИ-режим активен")
    else:
        logger.warning("❌ OpenAI API недоступен - только классический режим")

    logger.info("🚀 Бот успешно запущен!")


async def on_shutdown():
    """Функция выполняется при остановке бота"""
    logger.info("🛑 Карьерный советник завершает работу...")
    await bot.session.close()


async def main():
    """Основная функция запуска бота"""
    try:
        await on_startup()
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("⏹️ Получен сигнал остановки...")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
    finally:
        await on_shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")