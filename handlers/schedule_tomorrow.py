from datetime import datetime
from aiogram import Router, types
from aiogram.filters import Command
from db import get_user_class, get_schedule_for_day
from utils.schedule import format_schedule_message

router = Router()

@router.message(Command("tomorrow"))
async def cmd_tomorrow(message: types.Message):
    user_id = message.from_user.id

    # 1. Узнаем класс пользователя
    class_id = await get_user_class(user_id)
    if not class_id:
        await message.answer("Вы не зарегистрированы! Напишите /start для регистрации.")
        return

    # 2. Узнаем завтрашний день
    tomorrow_day = (datetime.now().weekday() + 1) % 7
    weekdays = [
        "Понедельник", "Вторник", "Среда", "Четверг", 
        "Пятница", "Суббота", "Воскресенье"
    ]
    day_name = weekdays[tomorrow_day]

    # 3. Получаем расписание
    schedule = await get_schedule_for_day(class_id, tomorrow_day)
    
    # 4. Форматируем и отправляем
    response = format_schedule_message(day_name, schedule)
    await message.answer(response, parse_mode="HTML")