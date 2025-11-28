import asyncio
import logging
from aiogram import Bot, Dispatcher
from database import create_tables
from handlers import register_handlers

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Токен бота
API_TOKEN = '7507292737:AAFaPrHceSq27qs_61yD_pCv5lYxNxHVnq4'

async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    
    # Регистрация обработчиков
    register_handlers(dp)
    
    # Создание таблиц БД
    await create_tables()
    
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    