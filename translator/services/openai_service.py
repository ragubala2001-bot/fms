import os
import json
import logging
from typing import AsyncGenerator

from openai import AsyncOpenAI

from .language_data import get_language_name

logger = logging.getLogger(__name__)

_client = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _client = AsyncOpenAI(api_key=api_key)
    return _client


async def detect_language(text: str) -> dict:
    """Detect the language of the given text using OpenAI."""
    client = get_client()
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a language detection expert. Detect the language of the given text. "
                    "Respond with ONLY a JSON object: "
                    '{"language": "<language name>", "code": "<ISO 639-1 code>", "confidence": <0-1>}. '
                    "No other text."
                ),
            },
            {"role": "user", "content": text},
        ],
        temperature=0,
        max_tokens=100,
    )
    content = response.choices[0].message.content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"language": "Unknown", "code": "unknown", "confidence": 0}


async def translate_text(
    text: str,
    target_language: str,
    source_language: str = "auto",
) -> str:
    """Translate text using OpenAI (non-streaming)."""
    client = get_client()
    target_name = get_language_name(target_language)

    system_prompt = (
        f"You are a professional translator. Translate the following text to {target_name}. "
        "Preserve all formatting, paragraphs, line breaks, and structure. "
        "Only output the translated text, nothing else."
    )
    if source_language and source_language != "auto":
        source_name = get_language_name(source_language)
        system_prompt += f" The source language is {source_name}."

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content


async def translate_text_stream(
    text: str,
    target_language: str,
    source_language: str = "auto",
) -> AsyncGenerator[str, None]:
    """Translate text using OpenAI with streaming response."""
    client = get_client()
    target_name = get_language_name(target_language)

    system_prompt = (
        f"You are a professional translator. Translate the following text to {target_name}. "
        "Preserve all formatting, paragraphs, line breaks, and structure. "
        "Only output the translated text, nothing else."
    )
    if source_language and source_language != "auto":
        source_name = get_language_name(source_language)
        system_prompt += f" The source language is {source_name}."

    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.3,
        stream=True,
    )

    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


async def translate_document_text(
    text: str,
    target_language: str,
    source_language: str = "auto",
) -> str:
    """Translate document text, handling large content by chunking."""
    max_chunk = 4000
    if len(text) <= max_chunk:
        return await translate_text(text, target_language, source_language)

    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 > max_chunk:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = para
        else:
            current_chunk = current_chunk + "\n\n" + para if current_chunk else para
    if current_chunk:
        chunks.append(current_chunk)

    translated_chunks = []
    for chunk in chunks:
        translated = await translate_text(chunk, target_language, source_language)
        translated_chunks.append(translated)

    return "\n\n".join(translated_chunks)


async def extract_text_from_image(image_base64: str) -> dict:
    """Extract text from an image using OpenAI Vision."""
    client = get_client()
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an OCR expert. Extract ALL text visible in the image. "
                    "Preserve the layout and structure as much as possible. "
                    "Also detect the language of the text. "
                    "Respond with a JSON object: "
                    '{"text": "<extracted text>", "language": "<detected language>", '
                    '"code": "<ISO 639-1 code>"}. No other text.'
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}",
                        },
                    },
                ],
            },
        ],
        temperature=0,
        max_tokens=4096,
    )
    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"text": content, "language": "Unknown", "code": "unknown"}
