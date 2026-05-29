import asyncio
import base64
import logging

from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from .serializers import (
    DetectLanguageSerializer,
    FileTranslateSerializer,
    OCRTranslateSerializer,
    TranslateTextSerializer,
)
from .services.file_service import extract_text_from_file, translate_file
from .services.language_data import LANGUAGES
from .services.ocr_service import process_image_ocr
from .services.openai_service import detect_language, translate_text

logger = logging.getLogger(__name__)


def index(request):
    """Main translator page."""
    return render(request, "translator/index.html")


@api_view(["GET"])
def get_languages(request):
    """Return the list of supported languages."""
    return Response({"languages": LANGUAGES})


@api_view(["POST"])
def api_detect_language(request):
    """Detect language of provided text."""
    serializer = DetectLanguageSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    text = serializer.validated_data["text"]

    result = asyncio.run(detect_language(text))
    return Response(result)


@api_view(["POST"])
def api_translate(request):
    """Translate text (non-streaming)."""
    serializer = TranslateTextSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    text = serializer.validated_data["text"]
    target = serializer.validated_data["target_language"]
    source = serializer.validated_data.get("source_language", "auto")

    translated = asyncio.run(translate_text(text, target, source))
    return Response({"translated_text": translated})


@csrf_exempt
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def api_translate_file(request):
    """Translate an uploaded file."""
    serializer = FileTranslateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    uploaded_file = serializer.validated_data["file"]
    target = serializer.validated_data["target_language"]
    source = serializer.validated_data.get("source_language", "auto")

    file_bytes = uploaded_file.read()
    filename = uploaded_file.name

    translated_bytes, output_filename, content_type = asyncio.run(
        translate_file(file_bytes, filename, target, source)
    )

    response = HttpResponse(translated_bytes, content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{output_filename}"'
    return response


@csrf_exempt
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def api_file_preview(request):
    """Extract and preview file content before translation."""
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return Response({"error": "No file provided"}, status=400)

    file_bytes = uploaded_file.read()
    filename = uploaded_file.name

    text = asyncio.run(extract_text_from_file(file_bytes, filename))
    language_info = asyncio.run(detect_language(text[:500])) if text.strip() else {}

    return Response(
        {
            "text": text[:5000],
            "total_length": len(text),
            "filename": filename,
            "detected_language": language_info,
        }
    )


@csrf_exempt
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def api_ocr_translate(request):
    """OCR extract text from image and translate."""
    serializer = OCRTranslateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    image_file = serializer.validated_data["image"]
    target = serializer.validated_data["target_language"]
    source = serializer.validated_data.get("source_language", "auto")

    image_bytes = image_file.read()

    result = asyncio.run(process_image_ocr(image_bytes, target, source))
    return Response(result)
