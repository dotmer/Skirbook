from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from states.editor import EditorState
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import get_schedule_for_day
from utils.day_normal import get_day
from utils.schedule import get_schedule

router = Router()

@router.callback_query(EditorState.choosing_day, F.data.in_([
    "monday","tuesday", "wednesday","thursday","friday","saturday","sunday"
]))
async def process_day_selection(callback: types.CallbackQuery, state: FSMContext):
    selected_day_data = callback.data

    #сохраняем выбранный день
    await state.update_data(selected_day=selected_day_data)

    #следующее состояние
    await state.set_state(EditorState.choosing_lesson)

    # получаем данные с class_id
    data = await state.get_data()
    class_id = data.get('class_id')

    _, day_full_name = get_day(selected_day_data)
    schedule = await get_schedule_for_day(class_id, day_full_name)
    schedule2 = await get_schedule(class_id, day_full_name)
    print(day_full_name, schedule)
    print(schedule2)

    builder = InlineKeyboardBuilder()

    msg_text = f"📅 <b>{day_full_name}</b>\n\n"

    if not schedule:
        builder.button(text="Уроков нет", callback_data="lesson_0")
    else:
        for lesson in schedule:
            lesson_num, subject, start_time, room = lesson
            
            room_text = f"(каб. {room})" if room else ""
            msg_text += f"<code>{start_time}</code> - {lesson_num}. {subject} {room_text}\n"

            builder.button(text=f"✏️ {subject}", callback_data=f"edit_ls_{lesson_num}")
        builder.adjust(2)
    
    builder.button(text="➕ Добавить урок", callback_data="add_lesson")
    builder.button(text="⬅️ Назад к выбору дня", callback_data="editor")
    builder.adjust(1)

    await callback.answer()
    await callback.message.edit_text(
        msg_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
        )