from aiogram.fsm.state import StatesGroup, State

class EditorState(StatesGroup):
    choosing_day = State()
    choosing_lesson = State()
    editing_lesson = State()
    adding_lessons = State()
    entering_subject = State()
    entering_room = State()
    entering_time = State()