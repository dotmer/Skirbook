import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    base_url="https://api.vsellm.ru/v1",
    api_key=os.getenv("VSELLM_API_KEY")
)

from configs.indicators import REASONING_CONFIG


def has_images(messages: list) -> bool:
    """Проверяет наличие изображений в сообщениях."""
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, list):
            if any(item.get("type") == "image_url" for item in content if isinstance(item, dict)):
                return True
    return False


def determine_reasoning_effort(content: str) -> str:
    """Определяет reasoning_effort на основе ключевых маркеров."""
    if isinstance(content, list):
        if any(isinstance(item, dict) and item.get("type") == "image_url" for item in content):
            return "high"
        text = " ".join(item.get("text", "") for item in content if isinstance(item, dict) and item.get("type") == "text")
    else:
        text = content
    
    text = text.lower().strip()
    if not text:
        return "low"
    
    word_count = len(text.split())
    
    if any(x in text for x in REASONING_CONFIG["ignore"]):
        return "none"
    
    math_signs = ["=", "²", "³", "√", "sin", "cos", "+", "*"]
    if any(s in text for s in math_signs) and word_count > 8:
        return "high"
    
    if any(marker in text for marker in REASONING_CONFIG["high"]) or word_count > 50:
        return "high"
    
    if any(marker in text for marker in REASONING_CONFIG["medium"]):
        return "medium"
    
    return "low"


async def chat(content: str, system: str = None, history: list = None) -> str:
    messages = []
    
    if system:
        messages.append({"role": "system", "content": system})
    if history:
        messages.extend(history)
    
    messages.append({"role": "user", "content": content})
    
    reasoning_effort = determine_reasoning_effort(content)
    has_img = has_images(messages)
    
    models = {
        "none": "gemini-3-flash-preview" if has_img else "gpt-oss-120b",
        "low": "gemini-3-flash-preview" if has_img else "gpt-oss-120b",
        "medium": "gemini-3-flash-preview",
        "high": "gemini-3-flash-preview"
    }
    
    resp = await client.chat.completions.create(
        model=models[reasoning_effort],
        messages=messages,
        max_tokens=4096,
        extra_body={"reasoning_effort": reasoning_effort}
    )
    
    return resp.choices[0].message.content