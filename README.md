# Hermes Local TTS

Local Ukrainian text-to-speech for Hermes Agent.

## Status

**Experimental and unreleased.** The current dogfood build routes Ukrainian through `patriotyk/styletts2_ukrainian_single` and English phrases through Kokoro `bm_george`. It is being installed and tested on one CPU-only Hermes host before any compatibility or support promise.

Read first: [`canon/README.md`](canon/README.md).

## MVP

- Ukrainian StyleTTS2 single-speaker synthesis.
- English phrases synthesized with Kokoro `bm_george` (experimental routing).
- Isolated runtime so PyTorch dependencies do not modify Hermes's venv.
- Hermes `TTSProvider` integration using the standard Telegram/Discord delivery pipeline.
- One-shot `/tts <text>` command if the current plugin command surface can deliver synchronously and origin-safely.
- Existing `/voice` behavior remains unchanged.

## Explicitly deferred

- Voice cloning and multispeaker selection.
- Alternative English voices or multilingual single-model synthesis.
- `/tts` without arguments (“speak the previous response”).
- Background delivery queues.
- Changes to Hermes core Voice Mode.
