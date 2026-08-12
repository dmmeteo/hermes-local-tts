from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional

import yaml
from agent.tts_provider import TTSProvider
from hermes_constants import get_hermes_home

DEFAULT_ENDPOINT = "http://127.0.0.1:8765"
VALID_MODES = {"fast", "quality"}


def _endpoint() -> str:
    return os.environ.get("HERMES_LOCAL_TTS_ENDPOINT", DEFAULT_ENDPOINT).rstrip("/")


def _configured_mode() -> str:
    config_path = get_hermes_home() / "config.yaml"
    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        value = config.get("tts", {}).get("local_tts", {}).get("mode", "fast")
    except (OSError, TypeError, yaml.YAMLError):
        value = "fast"
    value = str(value).strip().lower()
    if value not in VALID_MODES:
        raise RuntimeError("tts.local_tts.mode must be 'fast' or 'quality'")
    return value


def _request(path: str, payload: dict[str, Any] | None = None, timeout: float = 900) -> bytes:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{_endpoint()}{path}", data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method="POST" if data else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Hermes Local TTS worker returned HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Hermes Local TTS worker is unavailable at {_endpoint()}: {exc.reason}") from exc


class LocalTTSProvider(TTSProvider):
    @property
    def name(self) -> str:
        return "local_tts"

    @property
    def display_name(self) -> str:
        return "Hermes Local TTS"

    @property
    def voice_compatible(self) -> bool:
        return True

    def is_available(self) -> bool:
        try:
            status = json.loads(_request("/health", timeout=1.5))
            return bool(status.get("ready"))
        except Exception:
            return False

    def list_voices(self) -> list[dict[str, Any]]:
        return [{"id": "active", "display": "Configured local mode", "language": "uk-UA/en-GB", "gender": "male"}]

    def list_models(self) -> list[dict[str, Any]]:
        return [{"id": "local-uk-en-v1", "display": "Local Ukrainian/English v1", "languages": ["uk", "en"], "max_text_length": 12000}]

    def get_setup_schema(self) -> dict[str, Any]:
        return {"name": self.display_name, "badge": "local", "tag": "Fast Supertonic or quality StyleTTS2", "env_vars": []}

    def synthesize(self, text: str, output_path: str, *, voice: Optional[str] = None,
                   model: Optional[str] = None, speed: Optional[float] = None,
                   format: str = "wav", **extra: Any) -> str:
        if not text.strip():
            raise ValueError("Text must not be empty")
        audio = _request("/v1/audio/speech", {
            "text": text,
            "speed": float(speed or 1.25),
            "format": format,
            "mode": _configured_mode(),
        })
        target = Path(output_path)
        target.write_bytes(audio)
        if not target.is_file() or target.stat().st_size < 44:
            raise RuntimeError("Worker returned an empty or invalid audio payload")
        return str(target)


_PROVIDER = LocalTTSProvider()


def register(ctx) -> None:
    ctx.register_tts_provider(_PROVIDER)
