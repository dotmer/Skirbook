import base64
import asyncio
from io import BytesIO
from typing import Dict, List, Optional

import re

from aiogram import types, Bot, F
from aiogram.filters import StateFilter

from logger import log_to_file
from llm import chat
from . import router, SYSTEM, get_history, typing_action

_albums: Dict[str, List[types.Message]] = {}
_pending_photos: Dict[int, dict] = {}
_pending_text: Dict[int, dict] = {}
TIMEOUT = 0.5


async def _download_photo(bot: Bot, photo: types.PhotoSize) -> str:
    """Загружает одно фото и возвращает base64"""
    file = await bot.get_file(photo.file_id)
    buf = BytesIO()
    await bot.download_file(file.file_path, buf)
    return base64.b64encode(buf.getvalue()).decode()


def _get_optimal_photo(msg: types.Message) -> types.PhotoSize:
    """Выбирает оптимальный размер фото (не слишком большой)"""
    photos = msg.photo
    for p in photos:
        if p.width >= 800 or p.height >= 800:
            return p
    return photos[-1]

async def _process(messages: List[types.Message], bot: Bot, text: Optional[str] = None):
    msg = messages[0]
    user_id = msg.from_user.id
    history = get_history(user_id)
    is_photo = bool(msg.photo)

    try:
        async with typing_action(bot, msg.chat.id):
            if is_photo:
                photos = [_get_optimal_photo(m) for m in messages]
                b64_images = await asyncio.gather(*[_download_photo(bot, p) for p in photos])
                
                content = [{"type": "text", "text": text or "Что на изображении?"}]
                for b64 in b64_images:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                    })
                log_text = f"[{len(messages)} фото] {text or ''}".strip()
            else:
                content = log_text = text

            answer = await chat(content=content, system=SYSTEM, history=list(history))

        history.append({"role": "user", "content": log_text})
        history.append({"role": "assistant", "content": answer})
        await log_to_file(user_id, "user", log_text)
        await log_to_file(user_id, "skirbook", answer)
        
        try:
            await msg.answer(answer, parse_mode="HTML")
        except Exception:
            # Очищаем от HTML-тегов и отправляем как plain text
            clean_answer = re.sub(r'<[^>]+>', '', answer)
            await msg.answer(clean_answer)

    except Exception as e:
        await msg.answer(f"❌ Ошибка: {e}")


def _cancel(storage: dict, key: int):
    if key in storage:
        storage.pop(key)["task"].cancel()


async def _delayed_process(user_id: int, storage: dict, messages: List[types.Message], bot: Bot, text: Optional[str] = None):
    await asyncio.sleep(TIMEOUT)
    if user_id in storage:
        del storage[user_id]
        await _process(messages, bot, text)


async def _resolve_photos(messages: List[types.Message], bot: Bot):
    user_id = messages[0].from_user.id
    caption = next((m.caption for m in messages if m.caption), None)

    if caption:
        await _process(messages, bot, caption)
    elif user_id in _pending_text:
        text_data = _pending_text.pop(user_id)
        text_data["task"].cancel()
        await _process(messages, bot, text_data["text"])
    else:
        _pending_photos[user_id] = {
            "messages": messages,
            "task": asyncio.create_task(_delayed_process(user_id, _pending_photos, messages, bot))
        }


async def _collect_album(media_group_id: str, bot: Bot):
    await asyncio.sleep(TIMEOUT)
    if messages := _albums.pop(media_group_id, []):
        await _resolve_photos(messages, bot)


@router.message(F.photo, StateFilter(None))
async def photo_handler(msg: types.Message, bot: Bot):
    _cancel(_pending_photos, msg.from_user.id)

    if msg.media_group_id:
        if msg.media_group_id not in _albums:
            _albums[msg.media_group_id] = []
            asyncio.create_task(_collect_album(msg.media_group_id, bot))
        _albums[msg.media_group_id].append(msg)
    else:
        await _resolve_photos([msg], bot)


@router.message(F.text & ~F.text.startswith("/"), StateFilter(None))
async def text_handler(msg: types.Message, bot: Bot):
    user_id = msg.from_user.id

    if user_id in _pending_photos:
        photos = _pending_photos.pop(user_id)
        photos["task"].cancel()
        await _process(photos["messages"], bot, msg.text)
        return

    _cancel(_pending_text, user_id)
    _pending_text[user_id] = {
        "text": msg.text,
        "task": asyncio.create_task(_delayed_process(user_id, _pending_text, [msg], bot, msg.text))
    }