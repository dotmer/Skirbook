import asyncio
import logging
from aiogram import Bot, Dispatcher
from db import create_tables
from handlers import setup_routers
from version import __version__

from dotenv import load_dotenv
load_dotenv()

from os import getenv

TOKEN = getenv("TELEGRAM_TOKEN")
async def main():
    await create_tables()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    main_router = setup_routers()
    dp.include_router(main_router)

    print(f"Skirbook {__version__} is online...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Skirbook is offline.")