import aiosqlite

DB_NAME = 'databases/school.db'

# Маппинг строковых названий дней в числа
DAY_NAME_TO_NUMBER = {
    'понедельник': 1, 'пн': 1,
    'вторник': 2, 'вт': 2,
    'среда': 3, 'ср': 3,
    'четверг': 4, 'чт': 4,
    'пятница': 5, 'пт': 5,
    'суббота': 6, 'сб': 6,
    'воскресенье': 7, 'вс': 7,
}

def normalize_day(day_of_week) -> int:
    """Приводит день недели к числу 1-7, принимает int или str."""
    if isinstance(day_of_week, int):
        return day_of_week
    if isinstance(day_of_week, str):
        # Если это строка-число ("1", "5")
        if day_of_week.isdigit():
            return int(day_of_week)
        # Если это название дня
        return DAY_NAME_TO_NUMBER.get(day_of_week.lower().strip(), -1)
    return -1


async def create_tables():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')

        await db.execute("INSERT OR IGNORE INTO classes (name) VALUES ('10А')")

        await db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            class_id INTEGER,
            role TEXT DEFAULT 'student',
            FOREIGN KEY (class_id) REFERENCES classes(id)
        )
         ''')
        
        await db.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER,
        day_of_week INTEGER,
        lesson_number INTEGER,
        subject_name TEXT,
        start_time TEXT,
        room TEXT,
        UNIQUE(class_id, day_of_week, lesson_number)
        )        
''')
        await db.execute('''
        CREATE TABLE IF NOT EXISTS homework (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER,
        subject_name TEXT,
        task_text TEXT,
        for_date DATE
                         )
''')
        
        # Очистка старого расписания для 1 класса (10А), чтобы не дублировалось при перезапуске
        await db.execute("DELETE FROM schedule WHERE class_id = 1")

        # --- ЗАПОЛНЕНИЕ РАСПИСАНИЯ ПО ФОТО ---
        
        # Понедельник (1)
        await db.execute('''
            INSERT OR REPLACE INTO schedule (class_id, day_of_week, lesson_number, subject_name, start_time, room)
            VALUES 
            (1, 1, 1, 'Разговор о важном', '08:00', ''),
            (1, 1, 2, 'История', '08:50', ''),
            (1, 1, 3, 'ОБЗР', '09:50', '206'),
            (1, 1, 4, 'Обществознание', '10:40', ''),
            (1, 1, 5, 'Ин пр', '11:30', ''),
            (1, 1, 6, 'Физкультура', '12:20', 'Спортзал'),
            (1, 1, 7, 'Алгебра', '13:10', '203'),
            (1, 1, 8, 'Вер. и статистика', '14:00', '203')
        ''')

        # Вторник (2)
        await db.execute('''
            INSERT OR REPLACE INTO schedule (class_id, day_of_week, lesson_number, subject_name, start_time, room)
            VALUES 
            (1, 2, 1, 'Русский язык', '08:00', '301'),
            (1, 2, 2, 'Биология', '08:50', '333'),
            (1, 2, 3, 'Английский язык', '09:50', '322'),
            (1, 2, 4, 'Обществознание', '10:40', ''),
            (1, 2, 5, 'Геометрия', '11:30', '203'),
            (1, 2, 6, 'Осн. пом', '12:20', ''),
            (1, 2, 7, 'Физика', '13:10', '231')
        ''')

        # Среда (3)
        await db.execute('''
            INSERT OR REPLACE INTO schedule (class_id, day_of_week, lesson_number, subject_name, start_time, room)
            VALUES 
            (1, 3, 2, 'Физкультура', '08:50', 'Спортзал'),
            (1, 3, 3, 'Текст осн', '09:50', '301'),
            (1, 3, 4, 'Русский язык', '10:40', '301'),
            (1, 3, 5, 'Биология', '11:30', '333'),
            (1, 3, 6, 'Английский язык', '12:20', '322'),
            (1, 3, 7, 'География', '13:10', '319'),
            (1, 3, 8, 'Физика', '14:00', '231')
        ''')

        # Четверг (4)
        await db.execute('''
            INSERT OR REPLACE INTO schedule (class_id, day_of_week, lesson_number, subject_name, start_time, room)
            VALUES 
            (1, 4, 1, 'Россия - мои горизонты', '08:00', ''),
            (1, 4, 2, 'Химия', '08:50', '331'),
            (1, 4, 3, 'Литература', '09:50', ''),
            (1, 4, 4, 'Литература', '10:40', ''),
            (1, 4, 5, 'Обществознание', '11:30', ''),
            (1, 4, 6, 'Текст осн', '12:20', '301'),
            (1, 4, 7, 'Биология', '13:10', '333')
        ''')

        # Пятница (5)
        await db.execute('''
            INSERT OR REPLACE INTO schedule (class_id, day_of_week, lesson_number, subject_name, start_time, room)
            VALUES 
            (1, 5, 2, 'Информатика', '08:50', '317'),
            (1, 5, 3, 'Обществознание', '09:50', ''),
            (1, 5, 4, 'Английский язык', '10:40', '322'),
            (1, 5, 5, 'Геометрия', '11:30', '203'),
            (1, 5, 6, 'История', '12:20', ''),
            (1, 5, 7, 'Литература', '13:10', '301'),
            (1, 5, 8, 'Алгебра', '14:00', '203')
        ''')

        await db.commit()
        print("База данных обновлена и расписание для 10А загружено!")


#---------------------- USERS ----------------------

async def get_user_class(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT class_id FROM users WHERE user_id = ?", (user_id, )) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def register_user(user_id, class_name):
    async with aiosqlite.connect(DB_NAME) as db:

        # находим id класса по имени
        async with db.execute("SELECT id FROM classes WHERE name = ?", (class_name, )) as cursor:
            row = await cursor.fetchone()
            if not row:
                return False # такого класса нет
            class_id = row[0]
        
        await db.execute(
            "INSERT OR REPLACE INTO users (user_id, class_id) VALUES (?, ?)",
            (user_id, class_id)
        )
        await db.commit()
        return True



#---------------------- SCHEDULE ----------------------

# Время звонков согласно фото (начало урока)
DEFAULT_TIMES = {
    1: '08:00',
    2: '08:50', 
    3: '09:50',
    4: '10:40',
    5: '11:30',
    6: '12:20',
    7: '13:10',
    8: '14:00'
}

def get_lesson_time(lesson_number: int, custom_time: str = None) -> str:
    return custom_time or DEFAULT_TIMES.get(lesson_number, '—')

async def get_schedule_formatted(class_id, day_of_week) -> str:
    rows = await get_schedule_for_day(class_id, day_of_week)
    if not rows:
        return "Нет уроков"
    
    lines = []
    for num, subj, time, room in rows:
        t = time or DEFAULT_TIMES.get(num, '—')
        r = f"({room})" if room else ""
        lines.append(f"{num}. {t} | {subj} {r}")
    return "\n".join(lines)

async def get_schedule_for_day(class_id, day_of_week):
    day_num = normalize_day(day_of_week)
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''
        SELECT lesson_number, subject_name, start_time, room
        FROM schedule
        WHERE class_id = ? AND day_of_week = ?
        ORDER BY lesson_number ASC
''', (class_id, day_num)) as cursor:
            rows = await cursor.fetchall()
            return rows if rows else None
        
async def set_lesson(class_id, day, les_number, subject, room, start_time=None):
    day_num = normalize_day(day)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
        INSERT OR REPLACE INTO schedule
        (class_id, day_of_week, lesson_number, subject_name, room, start_time)
        VALUES (?, ?, ?, ?, ?, ?)
''', (class_id, day_num, les_number, subject, room, start_time))
        await db.commit()

async def delete_lesson(class_id, day, les_number):
    day_num = normalize_day(day)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
        DELETE FROM schedule
        WHERE class_id = ? AND day_of_week = ? AND lesson_number = ?
''', (class_id, day_num, les_number))
        await db.commit()

#---------------------- UTILITY ----------------------

async def get_class_by_name(value: str) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''
        SELECT id
        FROM classes
        WHERE name = ?
''', (value, )) as cursor:  
            row = await cursor.fetchone()
            if row:
                return row[0]
            else:
                return None