#!/usr/bin/env python3
"""Disposable StyleTTS2 Ukrainian CPU viability benchmark."""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from unicodedata import normalize

import soundfile as sf
import torch
from ipa_uk import ipa
from styletts2_inference.models import StyleTTS2
from ukrainian_word_stress import Stressifier, StressSymbol

MODEL_ID = "patriotyk/styletts2_ukrainian_single"


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    return [part.strip() for part in re.split(r"(?<=[.!?:])\s+", text) if part.strip()]


def prepare(text: str, stressifier: Stressifier) -> str:
    text = text.replace("+", StressSymbol.CombiningAcuteAccent)
    text = normalize("NFKC", text)
    text = re.sub(r"[᠆‐‑‒–—―⁻₋−⸺⸻]", "-", text)
    if text[-1] not in ".?!:-":
        text += "."
    text = re.sub(r" - ", ": ", text)
    return ipa(stressifier(text))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--threads", type=int, default=6)
    args = parser.parse_args()

    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(1)
    started = time.monotonic()
    model = StyleTTS2(hf_path=MODEL_ID, device="cpu")
    loaded = time.monotonic()
    stressifier = Stressifier()
    style = torch.load(model.model_dir / "style.pt", map_location="cpu") if hasattr(model, "model_dir") else None
    if style is None:
        from huggingface_hub import hf_hub_download
        style = torch.load(hf_hub_download(MODEL_ID, "style.pt"), map_location="cpu")

    waves = []
    prep_seconds = 0.0
    infer_seconds = 0.0
    for sentence in split_sentences(args.text):
        t0 = time.monotonic()
        phonemes = prepare(sentence, stressifier)
        prep_seconds += time.monotonic() - t0
        if not phonemes:
            continue
        tokens = model.tokenizer.encode(phonemes)
        t0 = time.monotonic()
        with torch.inference_mode():
            waves.append(model(tokens, speed=1.0, s_prev=style))
        infer_seconds += time.monotonic() - t0

    if not waves:
        raise RuntimeError("No audio generated")
    audio = torch.concatenate(waves).cpu().numpy()
    sf.write(args.output, audio, 24000)
    duration = len(audio) / 24000
    result = {
        "model": MODEL_ID,
        "threads": args.threads,
        "load_seconds": round(loaded - started, 3),
        "preprocess_seconds": round(prep_seconds, 3),
        "inference_seconds": round(infer_seconds, 3),
        "total_seconds": round(time.monotonic() - started, 3),
        "audio_duration_seconds": round(duration, 3),
        "warm_inference_rtf": round(infer_seconds / duration, 3),
        "output": str(Path(args.output).resolve()),
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
