from aiogram import Router, types
from aiogram.filters import Command, CommandObject

from db import get_user_class
from utils.schedule import format_schedule_message, get_schedule

router = Router()

@router.message(Command("schedule"))
async def cmd_schedule(message: types.Message, command: CommandObject):
    user_id = message.from_user.id

    # 1. Узнаем класс пользователя
    class_id = await get_user_class(user_id)
    if not class_id:
        await message.answer("Вы не зарегистрированы! Напишите /start для регистрации.")
        return

    # 2. Проверяем аргумент команды
    if not command.args:
        await message.answer(
            "❌ Укажите день недели!\n\n"
            "Примеры:\n"
            "/schedule пн\n"
            "/schedule вторник\n"
            "/schedule ср"
        )
        return

    # 3. Получаем расписание через локальную функцию
    day_name, schedule = await get_schedule(class_id, command.args)
    print(day_name, schedule)
    
    if day_name is None:
        await message.answer(
            "❌ Неверный день недели!\n\n"
            "Используйте: пн, вт, ср, чт, пт, сб, вс\n"
            "или полные названия: понедельник, вторник и т.д."
        )
        return

    # 4. Форматируем и отправляем
    response = format_schedule_message(day_name, schedule)
    await message.answer(response, parse_mode="HTML")