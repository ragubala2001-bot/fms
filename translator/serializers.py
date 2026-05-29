from rest_framework import serializers


class TranslateTextSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=50000)
    target_language = serializers.CharField(max_length=10)
    source_language = serializers.CharField(max_length=10, default="auto")


class DetectLanguageSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=10000)


class FileTranslateSerializer(serializers.Serializer):
    file = serializers.FileField()
    target_language = serializers.CharField(max_length=10)
    source_language = serializers.CharField(max_length=10, default="auto")


class OCRTranslateSerializer(serializers.Serializer):
    image = serializers.FileField()
    target_language = serializers.CharField(max_length=10)
    source_language = serializers.CharField(max_length=10, default="auto")
