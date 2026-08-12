# Implementation packets

## Packet 1 — verified inference spike

**Goal:** prove or disprove StyleTTS2 Ukrainian Single viability on the target CPU-only VPS.

**Canon:** `00-vision`, `01-principles`, `04-risks-and-assumptions`.

**Scope:**

- Dedicated disposable venv.
- Pinned Patriotyk inference code and single model.
- Ukrainian stress + IPA path.
- Three known test texts: short, medium, normalization edge cases.
- Capture cold start, warm synthesis time, audio duration, RTF, peak RSS, CPU, output size.
- Produce audio for user dogfood.

**Non-scope:** plugin, server lifecycle, bilingual routing, production installer.

**Acceptance criteria:**

- Real audio generated and playable.
- No host OOM or gateway disruption.
- Measurements come from the target VPS.
- Decision recorded: proceed, optimize, or reject.

**Resource gate:** begin with short text; stop before longer tests if available memory falls below 1 GiB, the process enters sustained swap thrash, or short warm RTF exceeds 4.

## Packet 2 — isolated worker

Blocked on Packet 1. Public seams: `GET /health`, `POST /v1/audio/speech`, PCM WAV output, bounded errors.

## Packet 3 — Hermes provider

Blocked on Packet 2. Public seam: Hermes `TTSProvider.synthesize()` through real plugin discovery and `text_to_speech`.

## Packet 4 — one-shot command

Blocked on Packet 3 and command-context verification. Public seam: `/tts <text>` from Discord and Telegram.
