#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import subprocess
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock

import numpy as np
import soundfile as sf
from supertonic import TTS

ENGINE = TTS(auto_download=True)
STYLE = ENGINE.get_voice_style("M3")
LOCK = Lock()


def encode_audio(wav: np.ndarray, requested_format: str) -> tuple[bytes, str]:
    samples = np.asarray(wav).squeeze()
    if requested_format.lower() != "ogg":
        output = io.BytesIO()
        sf.write(output, samples, ENGINE.sample_rate, format="WAV")
        return output.getvalue(), "audio/wav"
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "audio.wav"
        target = Path(directory) / "audio.ogg"
        sf.write(source, samples, ENGINE.sample_rate, format="WAV")
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source), "-c:a", "libopus", "-b:a", "48k", str(target)],
            check=True,
            timeout=60,
        )
        return target.read_bytes(), "audio/ogg"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path != "/health":
            self.send_error(404)
            return
        self.send_json({"ready": True, "mode": "fast", "backend": "supertonic-3", "voice": "M3/Robert", "steps": 16})

    def do_POST(self) -> None:
        try:
            if self.path != "/v1/audio/speech":
                self.send_error(404)
                return
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
            text = str(body.get("text", "")).strip()
            if not text:
                raise ValueError("text is required")
            with LOCK:
                wav, _ = ENGINE.synthesize(text, voice_style=STYLE, total_steps=16, speed=1.05)
            payload, content_type = encode_audio(wav, str(body.get("format", "wav")))
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except ValueError as exc:
            self.send_json({"error": str(exc)}, 400)
        except Exception as exc:
            self.send_json({"error": str(exc)}, 500)

    def log_message(self, format: str, *args: object) -> None:
        pass

    def send_json(self, value: object, status: int = 200) -> None:
        payload = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8767), Handler).serve_forever()
