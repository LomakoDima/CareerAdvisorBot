import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from services.handlers import register_handlers
from services.ai_service import is_openai_available
from database.database_service import db_service
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN не найден в .env файле!")
    exit(1)

if not OPENAI_KEY:
    logger.warning("⚠️ OPENAI_API_KEY не найден. ИИ-режим будет недоступен.")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

register_handlers(dp, bot)


async def on_startup():
    logger.info("🤖 Карьерный советник v2.0 запускается...")

    try:
        logger.info("🗄️ Инициализация базы данных SQLite...")

        db_stats = db_service.get_database_stats()
        logger.info(f"📊 База данных готова: {db_stats['total_users']} пользователей, {db_stats['total_tests']} тестов")

        ai_available = await is_openai_available()
        if ai_available:
            logger.info("✅ OpenAI API доступен - ИИ-режим активен")
        else:
            logger.warning("❌ OpenAI API недоступен - только классический режим")

        logger.info("🚀 Бот успешно запущен!")

    except Exception as e:
        logger.error(f"💥 Ошибка при запуске: {e}")
        raise


async def on_shutdown():
    logger.info("🛑 Карьерный советник завершает работу...")

    try:
        backup_path = db_service.backup_database("shutdown_backup.db")
        if backup_path:
            logger.info(f"💾 Резервная копия создана: {backup_path}")

        await bot.session.close()
        logger.info("✅ Бот корректно завершил работу")

    except Exception as e:
        logger.error(f"❌ Ошибка при завершении: {e}")


async def main():
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