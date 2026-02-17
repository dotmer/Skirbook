from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from states.editor import EditorState
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import get_schedule_for_day
from utils.day_normal import get_day

router = Router()


async def show_lessons_menu(target: types.Message, state: FSMContext, edit: bool = True):
    """Показать меню уроков. target — объект Message."""
    data = await state.get_data()
    class_id = data.get('class_id')
    selected_day_data = data.get('selected_day')

    _, day_full_name = get_day(selected_day_data)
    schedule = await get_schedule_for_day(class_id, day_full_name)
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

    await state.set_state(EditorState.choosing_lesson)

    if edit:
        await target.edit_text(msg_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        await target.answer(msg_text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(EditorState.choosing_day, F.data.in_([
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
]))
async def process_day_selection(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(selected_day=callback.data)
    await callback.answer()
    await show_lessons_menu(callback.message, state, edit=True)