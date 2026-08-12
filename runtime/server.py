#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import tempfile
import urllib.request
import wave
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from unicodedata import normalize

import soundfile as sf
import torch
from huggingface_hub import hf_hub_download
from ipa_uk import ipa
from styletts2_inference.models import StyleTTS2
from ukrainian_word_stress import Stressifier, StressSymbol

from prototype.language_router import segment_languages

MODEL_ID = "patriotyk/styletts2_ukrainian_single"
ENGLISH_URL = "http://127.0.0.1:8766/synthesize"
SENTENCE_RE = re.compile(r"(?<=[.!?:])\s+")
LOCK = Lock()

torch.set_num_threads(min(6, os.cpu_count() or 1)); torch.set_num_interop_threads(1)
MODEL = StyleTTS2(hf_path=MODEL_ID, device="cpu")
STYLE = torch.load(hf_hub_download(MODEL_ID, "style.pt"), map_location="cpu")
STRESSIFIER = Stressifier()


def prepare_uk(text: str) -> str:
    text = normalize("NFKC", text.replace("+", StressSymbol.CombiningAcuteAccent))
    text = re.sub(r"[᠆‐‑‒–—―⁻₋−⸺⸻]", "-", text)
    if text and text[-1] not in ".?!:-": text += "."
    return ipa(STRESSIFIER(text))


def segments(text: str):
    for segment in segment_languages(text):
        yield segment.language, segment.text


def synth_uk(text: str, speed: float) -> tuple[bytes, int]:
    phonemes = prepare_uk(text)
    tokens = MODEL.tokenizer.encode(phonemes)
    with torch.inference_mode(): audio = MODEL(tokens, speed=speed, s_prev=STYLE).cpu().numpy()
    out = io.BytesIO(); sf.write(out, audio, 24000, format="WAV"); return out.getvalue(), 24000


def synth_en(text: str, speed: float) -> tuple[bytes, int]:
    payload = json.dumps({"text": text, "speed": speed}).encode()
    req = urllib.request.Request(ENGLISH_URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as response: data = response.read()
    with wave.open(io.BytesIO(data), "rb") as wav: return data, wav.getframerate()


def synthesize(text: str, speed: float, output_format: str) -> bytes:
    with tempfile.TemporaryDirectory(prefix="local-tts-") as tmp:
        paths=[]
        index=0
        for sentence in [s.strip() for s in SENTENCE_RE.split(text) if s.strip()]:
            for language, part in segments(sentence):
                data, _ = synth_en(part, speed) if language == "en" else synth_uk(part, speed)
                path=Path(tmp)/f"{index:04d}.wav"; path.write_bytes(data); paths.append(path); index += 1
        if not paths: raise ValueError("text is required")
        concat=Path(tmp)/"concat.txt"; concat.write_text("".join(f"file '{p}'\n" for p in paths))
        extension = "ogg" if output_format in {"ogg", "opus"} else "wav"
        result=Path(tmp)/f"result.{extension}"
        codec=["-c:a","libopus","-b:a","48k"] if extension=="ogg" else ["-c:a","pcm_s16le"]
        subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-af","aresample=24000,loudnorm=I=-18:TP=-2:LRA=7",*codec,str(result)],check=True,timeout=120)
        return result.read_bytes()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/health": self.send_error(404); return
        try:
            with urllib.request.urlopen("http://127.0.0.1:8766/health", timeout=1) as r: english=json.loads(r.read()).get("ready",False)
        except Exception: english=False
        self._send_json({"ready": english, "ukrainian": True, "english": english})

    def do_POST(self):
        if self.path != "/v1/audio/speech": self.send_error(404); return
        try:
            body=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))))
            with LOCK: payload=synthesize(str(body.get("text","")),float(body.get("speed",1.25)),str(body.get("format","ogg")))
            self.send_response(200); self.send_header("Content-Type","audio/ogg" if payload[:4]==b"OggS" else "audio/wav")
            self.send_header("Content-Length",str(len(payload))); self.end_headers(); self.wfile.write(payload)
        except Exception as exc: self._send_json({"error":str(exc)},400)

    def log_message(self, format, *args): return
    def _send_json(self,value,status=200):
        payload=json.dumps(value).encode(); self.send_response(status); self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(payload))); self.end_headers(); self.wfile.write(payload)


if __name__ == "__main__": ThreadingHTTPServer(("127.0.0.1",8765),Handler).serve_forever()
