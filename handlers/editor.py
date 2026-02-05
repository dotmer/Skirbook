from typing import Union

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from states.editor import EditorState
from db import get_user_class

router = Router()


@router.message(Command("editor"))
@router.callback_query(F.data == "editor")
async def cmd_editor(
    event: Union[types.Message, types.CallbackQuery], 
    state: FSMContext
):
    await state.clear()

    if isinstance(event, types.CallbackQuery):
        await event.answer()
        user_id = event.from_user.id
        message = event.message
        send_func = message.edit_text
    else:
        user_id = event.from_user.id
        message = event
        send_func = message.answer

    class_id = await get_user_class(user_id)
    if not class_id:
        await message.answer("Вы не зарегистрированы! Напишите /start для регистрации.")
        return
    
    await state.set_state(EditorState.choosing_day)

    await state.update_data(class_id=class_id)

    builder = InlineKeyboardBuilder()
    
    weekdays_dict = {
        "Понедельник": "monday",
        "Вторник": "tuesday",
        "Среда": "wednesday",
        "Четверг": "thursday",
        "Пятница": "friday",
        "Суббота": "saturday",
        "Воскресенье": "sunday"
    }

    for rus_day, eng_day in weekdays_dict.items():
        builder.button(text=rus_day, callback_data=eng_day)
    
    builder.button(text="❌ Выход", callback_data="editor_exit")
    builder.adjust(1)

    await send_func(
        '🛠 <b>Режим редактирования</b>\n\nВыберите день недели:',
        reply_markup=builder.as_markup()
    )