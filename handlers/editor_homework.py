from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from states.editor import EditorState
from db import add_homework_safe, get_homework_by_subject_and_date, delete_homework

router = Router()


# ─── Меню урока: показывает ДЗ + кнопки ───

async def show_lesson_menu(target: types.Message, state: FSMContext, edit: bool = True):
    data = await state.get_data()
    lesson_num = data.get('selected_lesson_num')
    subject = data.get('selected_subject')

    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Добавить/изменить ДЗ", callback_data="set_hw")
    builder.button(text="🗑 Удалить ДЗ", callback_data="delete_hw")
    builder.button(text="⬅️ Назад к урокам", callback_data="back_to_lessons")
    builder.adjust(1)

    msg = f"📚 <b>{subject}</b> (урок №{lesson_num})\n\n"
    msg += "Выберите действие:"

    await state.set_state(EditorState.editing_lesson)

    if edit:
        await target.edit_text(msg, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        await target.answer(msg, reply_markup=builder.as_markup(), parse_mode="HTML")


# ─── Нажали на урок из списка ───

@router.callback_query(EditorState.choosing_lesson, F.data.startswith("edit_ls_"))
async def process_lesson_selected(callback: types.CallbackQuery, state: FSMContext):
    lesson_num = int(callback.data.split("_")[-1])

    data = await state.get_data()
    class_id = data.get('class_id')
    selected_day = data.get('selected_day')

    from db import get_schedule_for_day
    from utils.day_normal import get_day
    _, day_name = get_day(selected_day)
    schedule = await get_schedule_for_day(class_id, day_name)

    subject = None
    for num, subj, _, _ in schedule:
        if num == lesson_num:
            subject = subj
            break

    await state.update_data(selected_lesson_num=lesson_num, selected_subject=subject)
    await callback.answer()
    await show_lesson_menu(callback.message, state, edit=True)


# ─── Добавить/изменить ДЗ: запрос даты ───

@router.callback_query(EditorState.editing_lesson, F.data == "set_hw")
async def ask_hw_date(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(EditorState.waiting_hw_date)
    await callback.answer()
    await callback.message.edit_text(
        "📅 Введите дату, <b>на которую</b> задано ДЗ\n"
        "Формат: <code>16.02</code>",
        parse_mode="HTML"
    )


@router.message(EditorState.waiting_hw_date)
async def process_hw_date(message: types.Message, state: FSMContext):
    date_text = message.text.strip()

    # простая валидация ДД.ММ
    parts = date_text.split(".")
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        await message.answer("❌ Неверный формат. Введите дату как <code>16.02</code>", parse_mode="HTML")
        return

    await state.update_data(hw_date=date_text)
    await state.set_state(EditorState.waiting_hw_text)
    await message.answer(
        f"✏️ Введите текст домашнего задания на <b>{date_text}</b>:",
        parse_mode="HTML"
    )


# ─── Ввод текста ДЗ ───

@router.message(EditorState.waiting_hw_text)
async def process_hw_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    class_id = data['class_id']
    subject = data['selected_subject']
    hw_date = data['hw_date']
    task_text = message.text.strip()

    await add_homework_safe(class_id, subject, task_text, hw_date)

    await message.answer(
        f"✅ ДЗ сохранено!\n\n"
        f"📚 {subject}\n"
        f"📅 На: {hw_date}\n"
        f"📝 {task_text}",
        parse_mode="HTML"
    )

    await show_lesson_menu(message, state, edit=False)


# ─── Удалить ДЗ: запрос даты ───

@router.callback_query(EditorState.editing_lesson, F.data == "delete_hw")
async def ask_delete_date(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(EditorState.waiting_hw_delete_date)
    await callback.answer()
    await callback.message.edit_text(
        "🗑 Введите дату ДЗ, которое удалить\n"
        "Формат: <code>16.02</code>",
        parse_mode="HTML"
    )


@router.message(EditorState.waiting_hw_delete_date)
async def process_delete_hw(message: types.Message, state: FSMContext):
    data = await state.get_data()
    class_id = data['class_id']
    subject = data['selected_subject']
    date_text = message.text.strip()

    existing = await get_homework_by_subject_and_date(class_id, subject, date_text)

    if not existing:
        await message.answer(f"❌ ДЗ по <b>{subject}</b> на {date_text} не найдено", parse_mode="HTML")
    else:
        await delete_homework(class_id, subject, date_text)
        await message.answer(f"✅ ДЗ по <b>{subject}</b> на {date_text} удалено", parse_mode="HTML")

    await show_lesson_menu(message, state, edit=False)


# ─── Назад к урокам ───

@router.callback_query(EditorState.editing_lesson, F.data == "back_to_lessons")
async def back_to_lessons(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    from handlers.editor_lesson import show_lessons_menu
    await show_lessons_menu(callback.message, state, edit=True)