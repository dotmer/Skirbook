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