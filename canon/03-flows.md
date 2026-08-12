# Flows

## Standard Hermes Voice Mode

1. Hermes generates and sends its text response.
2. Existing `/voice on` or `/voice tts` policy decides whether TTS is requested.
3. Hermes calls the selected `local_tts` provider.
4. The provider obtains WAV from the local worker.
5. Hermes converts/delivers it as an appropriate voice bubble or attachment.
6. Any audio failure leaves the text response intact.

## One-shot explicit synthesis

MVP command:

```text
/tts <text>
```

1. Plugin receives explicit text.
2. It performs synchronous bounded synthesis through the same provider/service.
3. Hermes delivers the returned audio to the invoking origin where the current plugin command API permits this safely.
4. Empty input receives usage help.

Argument-free `/tts` is deferred because reliably reading the prior assistant message and binding asynchronous delivery to the invoking platform/chat/thread are separate upstream concerns.
