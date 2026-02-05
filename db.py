import aiosqlite

DB_NAME = 'databases/school.db'

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
        await db.execute('''
            INSERT OR IGNORE INTO schedule (class_id, day_of_week, lesson_number, subject_name, start_time, room)
            VALUES 
            (1, 5, 1, 'Алгебра', '08:00', '305'),
            (1, 5, 2, 'Русский язык', '08:50', '201'),
            (1, 5, 3, 'Математика', '09:30', '103'),
            (1, 5, 4, 'Физика', '10:20', '302')
        ''')
        await db.commit()
        print("База данных создана!")




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

DEFAULT_TIMES = {
    1: '08:00',
    2: '08:50', 
    3: '09:40',
    4: '10:30',
    5: '11:20',
    6: '12:10',
    7: '13:00',
    8: '13:50'
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
        lines.append(f"{num}. {t} | {subj} ({room})")
    return "\n".join(lines)

async def get_schedule_for_day(class_id, day_of_week):
    async with aiosqlite.connect(DB_NAME) as db:
        # Выбираем номер урока, название и номер аудитории
        async with db.execute('''
        SELECT lesson_number, subject_name, start_time, room
        FROM schedule
        WHERE class_id = ? AND day_of_week = ?
        ORDER BY lesson_number ASC
''', (class_id, day_of_week)) as cursor:
            rows = await cursor.fetchall()
            return rows if rows else None
        
async def set_lesson(class_id, day, les_number, subject, room, start_time=None):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
        INSERT OR REPLACE INTO schedule
        (class_id, day_of_week, lesson_number, subject_name, room, start_time)
        VALUES (?, ?, ?, ?, ?, ?)
''', (class_id, day, les_number, subject, room, start_time))
        await db.commit()

async def delete_lesson(class_id, day, les_number):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
        DELETE FROM schedule
        WHERE class_id = ? AND day_of_week = ? AND lesson_number = ?
''', (class_id, day, les_number))
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