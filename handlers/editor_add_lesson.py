from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from states.editor import EditorState

from db import set_lesson, get_schedule_for_day, DEFAULT_TIMES
from utils.day_normal import get_day

router = Router()


def get_next_lesson_num(schedule: list) -> int:
    if not schedule:
        return 1
    used = {lesson[0] for lesson in schedule}
    num = 1
    while num in used:
        num += 1
    return num


@router.callback_query(EditorState.choosing_lesson, F.data == "add_lesson")
async def start_add_lesson(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    _, day_full = get_day(data["selected_day"])
    
    schedule = await get_schedule_for_day(data["class_id"], day_full)
    next_num = get_next_lesson_num(schedule)
    
    await state.update_data(new_lesson_num=next_num)
    await state.set_state(EditorState.entering_subject)
    
    await callback.answer()
    await callback.message.edit_text(f"📝 Урок №{next_num}\n\nВведите название предмета:")


@router.message(EditorState.entering_subject)
async def process_subject(message: types.Message, state: FSMContext):
    await state.update_data(new_subject=message.text.strip())
    await state.set_state(EditorState.entering_room)
    await message.answer("🚪 Введите кабинет (или '-' чтобы пропустить):")


@router.message(EditorState.entering_room)
async def process_room(message: types.Message, state: FSMContext):
    await state.update_data(new_room=None if message.text.strip() == "-" else message.text.strip())
    await state.set_state(EditorState.entering_time)
    
    data = await state.get_data()
    default = DEFAULT_TIMES.get(data["new_lesson_num"], "—")
    await message.answer(f"🕐 Введите время (или '-' для {default}):")


@router.message(EditorState.entering_time)
async def process_time(message: types.Message, state: FSMContext):
    data = await state.get_data()
    _, day_full = get_day(data["selected_day"])
    
    user_input = message.text.strip()
    if user_input == "-":
        time = None
        display_time = DEFAULT_TIMES.get(data["new_lesson_num"], "—")
    else:
        time = user_input
        display_time = time
    
    await set_lesson(
        data["class_id"],
        day_full,
        data["new_lesson_num"],
        data["new_subject"],
        data["new_room"],
        time
    )
    
    # Форматируем кабинет
    room_display = data['new_room'] if data['new_room'] else '—'
    
    await state.set_state(EditorState.choosing_lesson)
    await message.answer(
        f"✅ Добавлен: {data['new_subject']} | {display_time} (каб. {room_display})"
    )