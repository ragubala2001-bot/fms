import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from .services.openai_service import detect_language, translate_text_stream

logger = logging.getLogger(__name__)


class TranslationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for realtime streaming translation."""

    async def connect(self):
        await self.accept()
        self._current_task = None

    async def disconnect(self, close_code):
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            action = data.get("action", "translate")

            if action == "detect":
                await self._handle_detect(data)
            elif action == "translate":
                await self._handle_translate(data)
            elif action == "cancel":
                await self._handle_cancel()
        except json.JSONDecodeError:
            await self.send(
                text_data=json.dumps({"type": "error", "message": "Invalid JSON"})
            )
        except Exception as e:
            logger.exception("WebSocket error")
            await self.send(
                text_data=json.dumps({"type": "error", "message": str(e)})
            )

    async def _handle_detect(self, data):
        text = data.get("text", "").strip()
        if not text:
            return

        result = await detect_language(text)
        await self.send(
            text_data=json.dumps(
                {
                    "type": "detection",
                    "language": result.get("language", "Unknown"),
                    "code": result.get("code", "unknown"),
                    "confidence": result.get("confidence", 0),
                }
            )
        )

    async def _handle_translate(self, data):
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()

        text = data.get("text", "").strip()
        target = data.get("target_language", "en")
        source = data.get("source_language", "auto")
        request_id = data.get("request_id", "")

        if not text:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "translation_complete",
                        "translated_text": "",
                        "request_id": request_id,
                    }
                )
            )
            return

        import asyncio

        self._current_task = asyncio.current_task()

        await self.send(
            text_data=json.dumps(
                {"type": "translation_start", "request_id": request_id}
            )
        )

        full_text = ""
        try:
            async for chunk in translate_text_stream(text, target, source):
                full_text += chunk
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "translation_chunk",
                            "chunk": chunk,
                            "full_text": full_text,
                            "request_id": request_id,
                        }
                    )
                )
        except asyncio.CancelledError:
            return
        except Exception as e:
            logger.exception("Translation stream error")
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "error",
                        "message": str(e),
                        "request_id": request_id,
                    }
                )
            )
            return

        await self.send(
            text_data=json.dumps(
                {
                    "type": "translation_complete",
                    "translated_text": full_text,
                    "request_id": request_id,
                }
            )
        )

    async def _handle_cancel(self):
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
        await self.send(text_data=json.dumps({"type": "cancelled"}))
