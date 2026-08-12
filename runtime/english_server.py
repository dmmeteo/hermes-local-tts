#!/usr/bin/env python3
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock

import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / ".models/kokoro/kokoro-v1.0.int8.onnx"
VOICES = ROOT / ".models/kokoro/voices-v1.0.bin"
ENGINE = Kokoro(str(MODEL), str(VOICES))
LOCK = Lock()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/health":
            self.send_error(404); return
        self._send_json({"ready": True, "voice": "bm_george"})

    def do_POST(self):
        if self.path != "/synthesize":
            self.send_error(404); return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length))
            text = str(body.get("text", "")).strip()
            speed = float(body.get("speed", 1.25))
            if not text:
                raise ValueError("text is required")
            with LOCK:
                samples, rate = ENGINE.create(text, voice="bm_george", speed=speed, lang="en-gb")
            import io
            output = io.BytesIO()
            sf.write(output, samples, rate, format="WAV")
            payload = output.getvalue()
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers(); self.wfile.write(payload)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=400)

    def log_message(self, fmt, *args):
        return

    def _send_json(self, value, status=200):
        payload = json.dumps(value).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8766), Handler).serve_forever()
