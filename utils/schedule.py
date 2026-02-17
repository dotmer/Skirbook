from db import get_schedule_for_day
from utils.day_normal import get_day
async def get_schedule(class_id: int, day_name: str) -> tuple[str, list]:
    result = get_day(day_name.lower())

    if result is None:
        print(f"Ошибка: Не удалось распознать день недели '{day_name}'")
        return None, []  # ← тоже исправьте: было просто return без значения
    
    day_index, full_name = result

    if day_index is None:
        return None, []
    
    schedule = await get_schedule_for_day(class_id, full_name)  # ← full_name вместо day_index
    return full_name, schedule

def format_schedule_message(day_name: str, schedule: list) -> str:
    """
    Форматирование расписания в текст сообщения
    """
    if not schedule:
        return f"📅 На <b>{day_name}</b>\n\nУроков нет!"
    
    response = f"📅 На <b>{day_name}</b>\n\n"
    for lesson in schedule:
        lesson_num = lesson[0]
        subject = lesson[1]
        start_time = lesson[2]
        room = lesson[3]
        
        room_text = f"(каб. {room})" if room else ""
        response += f"<code>{start_time}</code> - {lesson_num}. {subject} {room_text}\n"
    
    return response
