# Hermes Local TTS

Local Ukrainian text-to-speech for Hermes Agent.

## Status

**Stage: verified-inference spike.** The first milestone is to prove that `patriotyk/styletts2_ukrainian_single` can synthesize acceptable Ukrainian speech on the target CPU-only VPS within the agreed resource envelope.

Read first: [`canon/README.md`](canon/README.md).

## MVP

- Ukrainian-only StyleTTS2 single-speaker synthesis.
- Isolated runtime so PyTorch dependencies do not modify Hermes's venv.
- Hermes `TTSProvider` integration using the standard Telegram/Discord delivery pipeline.
- One-shot `/tts <text>` command if the current plugin command surface can deliver synchronously and origin-safely.
- Existing `/voice` behavior remains unchanged.

## Explicitly deferred

- Ukrainian/English routing and Kokoro concatenation.
- Voice cloning and multispeaker selection.
- `/tts` without arguments (“speak the previous response”).
- Background delivery queues.
- Changes to Hermes core Voice Mode.
