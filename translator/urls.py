from django.urls import path

from . import views

app_name = "translator"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/languages/", views.get_languages, name="api-languages"),
    path("api/detect/", views.api_detect_language, name="api-detect"),
    path("api/translate/", views.api_translate, name="api-translate"),
    path("api/translate/file/", views.api_translate_file, name="api-translate-file"),
    path("api/file/preview/", views.api_file_preview, name="api-file-preview"),
    path("api/ocr/translate/", views.api_ocr_translate, name="api-ocr-translate"),
]
