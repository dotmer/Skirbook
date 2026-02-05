from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from states.editor import EditorState

router = Router()

@router.callback_query(F.data == "editor_exit")
async def exit_editor(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.answer("Редактор закрыт.")
    await callback.message.edit_text("Вы вышли из режима редактирования")