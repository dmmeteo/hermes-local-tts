# System shape

```text
Hermes text_to_speech or /tts <text>
              |
       Hermes plugin provider
              |
      localhost HTTP worker
              |
   spoken-text preparation (optional)
              |
 Ukrainian stress -> IPA -> StyleTTS2 single
              |
          PCM WAV file
              |
 Hermes format conversion and platform delivery
```

## Boundaries

### Hermes plugin

- Implements `agent.tts_provider.TTSProvider`.
- Registers provider name `local_tts` (display name `Hermes Local TTS`).
- Calls the local worker with bounded timeouts.
- Writes truthful audio to the path requested by Hermes.
- Does not call Telegram or Discord APIs itself.

### Local worker

- Runs in a dedicated venv.
- Binds to loopback only.
- Lazy-loads one fixed model: `patriotyk/styletts2_ukrainian_single`.
- Serializes synthesis globally.
- Exposes health/readiness separately from synthesis.
- Splits long input into bounded sentence chunks.

### Preprocessing

MVP baseline uses Hermes spoken-text cleanup plus Unicode normalization, Ukrainian stress assignment, and IPA conversion. Number/symbol/abbreviation verbalization is configurable and may be introduced only after A/B tests.
