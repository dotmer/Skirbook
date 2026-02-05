from collections import deque

from aiogram import types, F

from . import router, histories


@router.message(F.text == "/clear")
async def clear_handler(msg: types.Message):
    histories[msg.from_user.id] = deque(maxlen=6)
    await msg.answer("✅ История очищена")