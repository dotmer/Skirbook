from datetime import datetime

DAY_MAPS = {
    "Понедельник": ["пн", "monday"],
    "Вторник": ["вт", "tuesday"],
    "Среда": ["ср", "wednesday"],
    "Четверг": ["чт", "thursday"],
    "Пятница": ["пт", "friday"],
    "Суббота": ["сб", "saturday"],
    "Воскресенье": ["вс", "sunday"],
}

def get_day(dayName: str) -> tuple[int, str] | None:
    """
    Получить индекс и полное название дня недели
    
    Args:
        dayName: название дня (полное или сокращение)
    
    Returns:
        tuple: (индекс_дня, полное_название) или None если не найдено
    """
    for i, (dayFullName, abbrs) in enumerate(DAY_MAPS.items(), start=1):
        if dayName in abbrs or dayFullName.lower() == dayName.lower():
            return i, dayFullName
    return None


def get_today() -> tuple[int, str]:
    """
    Получить индекс и полное название текущего дня недели
    
    Returns:
        tuple: (индекс_дня 1-7, полное_название на русском)
    """
    days_list = list(DAY_MAPS.keys())
    weekday_index = datetime.now().weekday()  # 0 = Monday, 6 = Sunday
    day_name = days_list[weekday_index]
    return weekday_index + 1, day_name