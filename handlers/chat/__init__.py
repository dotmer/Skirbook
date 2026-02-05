import asyncio
from contextlib import asynccontextmanager
from collections import deque
from pathlib import Path

from aiogram import Router, Bot
from aiogram.enums import ChatAction

router = Router()

SYSTEM = Path("system_prompt.txt").read_text(encoding="utf-8")
histories: dict[int, deque] = {}
HISTORY_LIMIT = 6

def get_history(user_id: int) -> deque:
    if user_id not in histories:
        histories[user_id] = deque(maxlen=HISTORY_LIMIT)
    return histories[user_id]


@asynccontextmanager
async def typing_action(bot: Bot, chat_id: int, interval: float = 4.0):
    stop_event = asyncio.Event()
    
    async def keep_typing():
        while not stop_event.is_set():
            try:
                await bot.send_chat_action(chat_id, ChatAction.TYPING)
                await asyncio.wait_for(stop_event.wait(), timeout=interval)
            except asyncio.TimeoutError:
                continue
            except Exception:
                break
    
    task = asyncio.create_task(keep_typing())
    try:
        yield
    finally:
        stop_event.set()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


# Импорты В КОНЦЕ файла
from . import clear_handler
from . import chat_handler

__all__ = ["router"]