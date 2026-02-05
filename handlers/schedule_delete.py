from aiogram import Router, types
from aiogram.filters import Command, CommandObject

from db import delete_lesson, get_class_by_name
from utils.day_normal import get_day

router = Router()

@router.message(Command("delete"))
async def cmd_delete(message: types.Message, command: CommandObject):
    # Проверка наличия аргументов
    if not command.args:
        await message.answer(
            '❌ Ошибка ввода.\n'
            '📝 Пример: /delete 10А пн 3\n\n'
            'Где:\n'
            '• 10А - название класса\n'
            '• пн - день недели\n'
            '• 3 - номер урока'
        )
        return
    
    # Разбиваем аргументы
    args = command.args.strip().split()
    
    # Проверка количества аргументов
    if len(args) != 3:
        await message.answer(
            f'❌ Неверное количество параметров (указано {len(args)}, нужно 3).\n'
            '📝 Пример: /delete 10А пн 3'
        )
        return
    
    class_name = args[0]
    day_name = args[1]
    lesson_number = args[2]
    
    # Проверка номера урока (должен быть числом)
    if not lesson_number.isdigit():
        await message.answer(
            f'❌ Номер урока должен быть числом, а не "{lesson_number}".\n'
            '📝 Пример: /delete 10А пн 3'
        )
        return
    
    lesson_number = int(lesson_number)
    
    # Проверка диапазона номера урока
    if lesson_number < 1 or lesson_number > 10:
        await message.answer(
            f'❌ Номер урока должен быть от 1 до 10 (указано: {lesson_number}).'
        )
        return
    
    # Получение дня недели
    day_id, _ = get_day(day_name)
    if day_id is None:
        await message.answer(
            f'❌ Неверный день недели: "{day_name}".\n'
            '📅 Допустимые значения: пн, вт, ср, чт, пт, сб, вс'
        )
        return
    
    # Получение класса
    class_id = get_class_by_name(class_name.capitalize())
    if class_id is None:
        await message.answer(
            f'❌ Класс "{class_name}" не найден в базе данных.\n'
            '💡 Проверьте правильность написания.'
        )
        return
    
    # Удаление урока
    success = delete_lesson(class_id, day_id, lesson_number)
    
    if success:
        await message.answer(
            f"✅ Урок успешно удалён!\n\n"
            f"Класс: {class_name}\n"
            f"День: {day_name}\n"
            f"Номер урока: {lesson_number}"
        )
    else:
        await message.answer(
            f"⚠️ Урок не найден.\n\n"
            f"Класс: {class_name}\n"
            f"День: {day_name}\n"
            f"Номер урока: {lesson_number}\n\n"
            f"Возможно, этот урок уже отсутствует в расписании."
        )