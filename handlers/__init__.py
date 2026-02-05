import os
import importlib
from aiogram import Router


def setup_routers() -> Router:
    """
    Создаем главный роутер, который подключает остальные.
    
    Поддерживает:
    - Файлы: handlers/start.py (с router внутри)
    - Папки: handlers/admin/__init__.py (с router внутри)
    """
    master_router = Router()
    
    # получаем путь к текущей папке
    handlers_dir = os.path.dirname(__file__)
    
    # определяем имя пакета (handlers)
    package_name = os.path.basename(handlers_dir)

    # пробегаемся по всем элементам в папке
    for item in os.listdir(handlers_dir):
        item_path = os.path.join(handlers_dir, item)
        
        # пропускаем элементы, начинающиеся с __
        if item.startswith("__"):
            continue
        
        module = None
        module_display_name = None
        
        # Вариант 1: это .py файл
        if os.path.isfile(item_path) and item.endswith(".py"):
            module_name = item[:-3]  # убираем .py
            module_display_name = module_name
            
            try:
                module = importlib.import_module(f"{package_name}.{module_name}")
            except Exception as e:
                print(f"Failed import {item}: {e}")
                continue
        
        # Вариант 2: это папка с __init__.py
        elif os.path.isdir(item_path):
            init_file = os.path.join(item_path, "__init__.py")
            
            if os.path.exists(init_file):
                module_display_name = f"{item}/"
                
                try:
                    module = importlib.import_module(f"{package_name}.{item}")
                except Exception as e:
                    print(f"Failed import {item}/: {e}")
                    continue
        
        # Если модуль успешно загружен - ищем router
        if module is not None:
            if hasattr(module, "router"):
                print(f"Router loaded: {module_display_name}")
                master_router.include_router(module.router)
            else:
                print(f"⚠️ В {module_display_name} didn't finded 'router'")
    
    return master_router