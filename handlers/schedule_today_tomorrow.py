from datetime import datetime, timedelta, timezone
from aiogram import Router, types
from aiogram.filters import Command
from db import get_user_class, get_schedule_for_day, get_homework_by_date
from utils.schedule import format_schedule_message

router = Router()

WEEKDAYS = [
    "Понедельник", "Вторник", "Среда", "Четверг",
    "Пятница", "Суббота", "Воскресенье"
]

# Твой часовой пояс (МСК = UTC+3), поменяй если другой
MSK = timezone(timedelta(hours=5))


@router.message(Command("today"))
async def cmd_today(message: types.Message):
    user_id = message.from_user.id

    class_id = await get_user_class(user_id)
    if not class_id:
        await message.answer("Вы не зарегистрированы! Напишите /start для регистрации.")
        return

    today = datetime.now(MSK)
    day_num = today.isoweekday()
    day_name = WEEKDAYS[day_num - 1]
    date_str = today.strftime("%d.%m")

    schedule = await get_schedule_for_day(class_id, day_num)
    homework = await get_homework_by_date(class_id, date_str)

    response = format_schedule_message(day_name, schedule, homework)
    await message.answer(response, parse_mode="HTML")


@router.message(Command("tomorrow"))
async def cmd_tomorrow(message: types.Message):
    user_id = message.from_user.id

    class_id = await get_user_class(user_id)
    if not class_id:
        await message.answer("Вы не зарегистрированы! Напишите /start для регистрации.")
        return

    tomorrow = datetime.now(MSK) + timedelta(days=1)
    day_num = tomorrow.isoweekday()
    day_name = WEEKDAYS[day_num - 1]
    date_str = tomorrow.strftime("%d.%m")

    schedule = await get_schedule_for_day(class_id, day_num)
    homework = await get_homework_by_date(class_id, date_str)

    response = format_schedule_message(day_name, schedule, homework)
    await message.answer(response, parse_mode="HTML")