# Principles

## Goals

- Local Ukrainian synthesis with StyleTTS2 single speaker.
- Plugin-first Hermes integration.
- Isolated dependencies and localhost-only runtime.
- One inference at a time across the VPS.
- Optional, inspectable spoken-text preprocessing.
- Preserve Hermes text responses and standard delivery.

## Non-goals for MVP

- Bilingual synthesis, Kokoro, or language routing.
- Multispeaker support or voice cloning.
- Modifying `/voice` semantics.
- Continuous background worker queues beyond the model service itself.
- Speaking the previous response via argument-free `/tts`.
- Public network exposure.

## Failure policy

TTS failure must not suppress or delay the canonical text answer. Report a concise error for explicit one-shot requests; auto-TTS paths remain best-effort.
