import base64
import logging

from .openai_service import extract_text_from_image, translate_text

logger = logging.getLogger(__name__)


async def process_image_ocr(
    image_bytes: bytes,
    target_language: str,
    source_language: str = "auto",
) -> dict:
    """Process an image: OCR extract text, detect language, translate."""
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    ocr_result = await extract_text_from_image(image_base64)

    extracted_text = ocr_result.get("text", "")
    detected_language = ocr_result.get("language", "Unknown")
    detected_code = ocr_result.get("code", "unknown")

    if not extracted_text.strip():
        return {
            "extracted_text": "",
            "detected_language": detected_language,
            "detected_code": detected_code,
            "translated_text": "",
            "error": "No text found in image",
        }

    translated_text = await translate_text(
        extracted_text, target_language, source_language
    )

    return {
        "extracted_text": extracted_text,
        "detected_language": detected_language,
        "detected_code": detected_code,
        "translated_text": translated_text,
    }
