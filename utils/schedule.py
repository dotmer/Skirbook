from datetime import datetime, timedelta, timezone
from db import get_schedule_for_day, get_homework_by_date, normalize_day

# Маппинг английских названий → русские полные
DAY_NAMES = {
    1: 'Понедельник',
    2: 'Вторник',
    3: 'Среда',
    4: 'Четверг',
    5: 'Пятница',
    6: 'Суббота',
    7: 'Воскресенье',
}

# Маппинг коротких/полных русских → номер дня
DAY_MAP = {
    'пн': 1, 'понедельник': 1,
    'вт': 2, 'вторник': 2,
    'ср': 3, 'среда': 3,
    'чт': 4, 'четверг': 4,
    'пт': 5, 'пятница': 5,
    'сб': 6, 'суббота': 6,
    'вс': 7, 'воскресенье': 7,
}


def get_next_date_for_day(day_num: int) -> str:
    """Ближайшая будущая дата для дня недели (включая сегодня)."""
    today = datetime.now(timezone(timedelta(hours=5)))
    today_weekday = today.isoweekday()

    diff = day_num - today_weekday
    if diff < 0:
        diff += 7
    # diff == 0 значит сегодня этот день

    target = today + timedelta(days=diff)
    return target.strftime("%d.%m")


async def get_schedule(class_id: int, day_arg: str):
    key = day_arg.lower().strip()
    day_num = DAY_MAP.get(key)

    if day_num is None:
        return None, None, None

    day_name = DAY_NAMES[day_num]
    schedule = await get_schedule_for_day(class_id, day_num)

    # Ищем ближайшую БУДУЩУЮ дату этого дня (включая сегодня)
    today = datetime.now()
    today_weekday = today.isoweekday()

    diff = day_num - today_weekday
    if diff < 0:
        diff += 7

    target_date = (today + timedelta(days=diff)).strftime("%d.%m")
    homework = await get_homework_by_date(class_id, target_date)

    return day_name, schedule, homework if homework else None


def format_schedule_message(day_name: str, schedule, homework) -> str:
    """Форматирует расписание + домашку в одно сообщение."""

    msg = f"📅 <b>{day_name}</b>\n\n"

    # ── Расписание ──
    if not schedule:
        msg += "Уроков нет 🎉\n"
    else:
        # Собираем ДЗ в словарь {предмет: текст} для быстрого поиска
        hw_dict = {}
        if homework:
            for subject, task in homework:
                hw_dict[subject.lower()] = task

        for lesson_num, subject, start_time, room in schedule:
            time_text = start_time or "—"
            room_text = f" (каб. {room})" if room else ""

            line = f"<code>{time_text}</code> — {lesson_num}. <b>{subject}</b>{room_text}"

            # Если есть ДЗ по этому предмету — показываем под уроком
            hw_task = hw_dict.get(subject.lower())
            if hw_task:
                line += f"\n     📝 <i>{hw_task}</i>"

            msg += line + "\n"

    # ── Отдельный блок ДЗ, если есть задания без урока в этот день ──
    if homework and schedule:
        schedule_subjects = {subj.lower() for _, subj, _, _ in schedule}
        extra_hw = [(s, t) for s, t in homework if s.lower() not in schedule_subjects]

        if extra_hw:
            msg += "\n📚 <b>Также задано:</b>\n"
            for subject, task in extra_hw:
                msg += f"  📝 {subject} — <i>{task}</i>\n"

    elif homework and not schedule:
        msg += "\n📚 <b>Домашнее задание:</b>\n"
        for subject, task in homework:
            msg += f"  📝 {subject} — <i>{task}</i>\n"

    return msg