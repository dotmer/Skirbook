import asyncio
from contextlib import asynccontextmanager
from collections import deque
from pathlib import Path
from datetime import datetime
from utils.schedule import get_schedule

from aiogram import Router, Bot
from aiogram.enums import ChatAction

router = Router()

# Загружаем базовый промпт один раз
_BASE_SYSTEM = Path("system_prompt.txt").read_text(encoding="utf-8")

WEEKDAYS = [
    "Понедельник", "Вторник", "Среда", "Четверг",
    "Пятница", "Суббота", "Воскресенье"
]


async def get_system_prompt() -> str:
    """
    Генерирует системный промпт с АКТУАЛЬНЫМИ датой, временем, расписанием и домашкой.
    """
    now = datetime.now()
    current_day = now.weekday()
    day_name = WEEKDAYS[current_day]

    date_str = now.strftime("%d.%m.%Y")
    time_str = now.strftime("%H:%M")

    # Получаем расписание и домашку
    full_name, schedule_today, homework_today = await get_schedule(1, day_name)

    # Форматируем расписание
    if schedule_today:
        schedule_text = "\n".join(
            f"  {i}. {lesson}" for i, lesson in enumerate(schedule_today, 1)
        )
    else:
        schedule_text = "  No Lessons"

    # Форматируем домашнее задание
    # homework_today: [(subject_name, task_text), ...] или None
    if homework_today:
        homework_text = "\n".join(
            f"  • {subject}: {task}" for subject, task in homework_today
        )
    else:
        homework_text = "  No Homework"

    context_block = (
        f"\n\n--- Current Context ---\n"
        f"Date: {date_str} ({day_name})\n"
        f"Time: {time_str}\n"
        f"\nSchedule for today:\n{schedule_text}\n"
        f"\nHomework for today:\n{homework_text}"
    )

    return _BASE_SYSTEM + context_block


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


from . import clear_handler
from . import chat_handler

__all__ = ["router"]