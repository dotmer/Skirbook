from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from states.editor import EditorState
from db import get_schedule_for_day
from utils.day_normal import get_day

router = Router()


async def show_lessons_menu(target: types.Message, state: FSMContext, edit: bool = True):
    """Показывает список уроков выбранного дня с кнопками редактирования."""
    data = await state.get_data()
    class_id = data.get('class_id')
    selected_day = data.get('selected_day')

    _, day_full_name = get_day(selected_day)
    schedule = await get_schedule_for_day(class_id, day_full_name)

    builder = InlineKeyboardBuilder()
    msg_text = f"📅 <b>{day_full_name}</b>\n\n"

    if not schedule:
        msg_text += "Уроков нет\n"
    else:
        for lesson_num, subject, start_time, room in schedule:
            room_text = f" (каб. {room})" if room else ""
            time_text = start_time or "—"
            msg_text += f"<code>{time_text}</code> — {lesson_num}. {subject}{room_text}\n"

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


# ─── Выбор дня → показать уроки ───

@router.callback_query(EditorState.choosing_day, F.data.in_([
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
]))
async def process_day_selection(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(selected_day=callback.data)
    await callback.answer()
    await show_lessons_menu(callback.message, state, edit=True)


# ─── Назад к выбору дня (из меню урока) ───

@router.callback_query(F.data == "editor")
async def back_to_days(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    from handlers.editor import show_day_selector
    await show_day_selector(callback.message, state, edit=True)