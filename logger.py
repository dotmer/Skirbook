# logger.py
import os
import aiofiles
from datetime import datetime

# Создаем папку один раз при импорте модуля
if not os.path.exists("saved"):
    os.makedirs("saved")

async def log_to_file(user_id: int, role: str, text: str):
    """
    Асинхронно пишет лог в файл saved/{user_id}.txt
    """
    filename = f"saved/{user_id}.txt"
    timestamp = datetime.now().strftime("%d.%m %H:%M:%S")
    
    # Форматирование: [ROLE] (TIME): Text
    log_entry = f"[{role.upper()}] ({timestamp}):\n{text}\n{'-'*40}\n"

    try:
        async with aiofiles.open(filename, mode='a', encoding='utf-8') as f:
            await f.write(log_entry)
    except Exception as e:
        print(f"Ошибка логирования: {e}")