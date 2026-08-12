# Vision

Hermes Local TTS gives the operator a pleasant, self-hosted Ukrainian audio rendering of Hermes responses without replacing the text response or depending on paid cloud TTS.

## Target operator

A Hermes operator using Discord and Telegram from a CPU-only VPS who wants to listen selectively when reading is inconvenient.

## MVP promise

Given Ukrainian text, produce one truthful audio file using Patriotyk's StyleTTS2 Ukrainian single-speaker model and hand it to Hermes's existing cross-platform TTS delivery path.

## Success

- Voice quality is materially better than the rejected Piper baseline.
- The target VPS can complete short synthesis without OOM or destabilizing the gateway.
- Text remains available; audio supplements it.
- Provider installation and failure behavior are inspectable and reversible.
