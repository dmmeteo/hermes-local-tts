from __future__ import annotations

import json
import os
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional

from agent.tts_provider import TTSProvider

DEFAULT_ENDPOINT = "http://127.0.0.1:8765"


def _endpoint() -> str:
    # Runtime endpoint is an internal deployment detail. User-facing behavior
    # belongs in config.yaml once this experiment grows setup UX.
    return os.environ.get("HERMES_LOCAL_TTS_ENDPOINT", DEFAULT_ENDPOINT).rstrip("/")


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


def _mode_status() -> dict[str, Any]:
    return json.loads(_request("/mode", timeout=3))


def _handle_mode(raw_args: str) -> str:
    value = (raw_args or "status").strip().lower()
    if value == "status":
        status = _mode_status()
        return f"Hermes Local TTS mode: **{status['mode']}** ({'ready' if status.get('ready') else 'starting'})"
    if value not in {"fast", "quality"}:
        return "Usage: /tts-mode <fast|quality|status>"
    status = json.loads(_request("/mode", {"mode": value}, timeout=330))
    return f"Hermes Local TTS switched to **{value}** ({'ready' if status.get('ready') else 'starting'})"


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
        return [
            {"id": "fast", "display": "Fast — Supertonic Robert", "language": "uk-UA/en-GB", "gender": "male"},
            {"id": "quality", "display": "Quality — StyleTTS2 + bm_george", "language": "uk-UA/en-GB", "gender": "male"},
        ]

    def list_models(self) -> list[dict[str, Any]]:
        return [{"id": "local-uk-en-v1", "display": "Local Ukrainian/English v1", "languages": ["uk", "en"], "max_text_length": 12000}]

    def get_setup_schema(self) -> dict[str, Any]:
        return {"name": self.display_name, "badge": "local", "tag": "Experimental StyleTTS2 + Kokoro", "env_vars": []}

    def synthesize(self, text: str, output_path: str, *, voice: Optional[str] = None,
                   model: Optional[str] = None, speed: Optional[float] = None,
                   format: str = "wav", **extra: Any) -> str:
        if not text.strip():
            raise ValueError("Text must not be empty")
        audio = _request("/v1/audio/speech", {
            "text": text,
            "speed": float(speed or 1.25),
            "format": format,
        })
        target = Path(output_path)
        target.write_bytes(audio)
        if not target.is_file() or target.stat().st_size < 44:
            raise RuntimeError("Worker returned an empty or invalid audio payload")
        return str(target)


_PROVIDER = LocalTTSProvider()


def _handle_tts(raw_args: str) -> str:
    text = (raw_args or "").strip()
    if not text:
        return "Usage: /tts <text>"
    fd, path = tempfile.mkstemp(prefix="hermes-local-tts-", suffix=".ogg")
    os.close(fd)
    _PROVIDER.synthesize(text, path, speed=1.25, format="ogg")
    return f"[[audio_as_voice]]\nMEDIA:{path}"


def register(ctx) -> None:
    ctx.register_tts_provider(_PROVIDER)
    ctx.register_command(
        "tts",
        handler=_handle_tts,
        description="Synthesize one local Ukrainian/English voice message.",
        args_hint="<text>",
    )
    ctx.register_command(
        "tts-mode",
        handler=_handle_mode,
        description="Switch Hermes Local TTS between fast and quality modes.",
        args_hint="<fast|quality|status>",
    )
