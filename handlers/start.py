from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states.registration import Registration

from db import register_user, get_user_class

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    class_id = await get_user_class(message.from_user.id)
    if class_id:
        await message.answer(f"Ты уже зарегестрирован в классе {class_id}.")
        return
    
    await message.answer('Привет, я - Skirbook. \n Напиши свой класс (Например: 10А)')
    await state.set_state(Registration.waiting_for_class)

@router.message(Registration.waiting_for_class)
async def process_class_name(message: types.Message, state: FSMContext):
    class_name = message.text.strip().upper()

    success = await register_user(message.from_user.id, class_name)

    if success:
        await message.answer(f"Отлично! Ты зарегестрирован в классе {class_name}. \n Теперь доступны команды /schedule и /edit")
        await state.clear()
    else:
        await message.answer("Такого класса нету. Попробуй ещё раз.")