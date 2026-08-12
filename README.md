# Hermes Local TTS

Opinionated local Ukrainian/English TTS for [Hermes Agent](https://hermes-agent.nousresearch.com/) with two modes:

| Mode | Pipeline | Best for |
|---|---|---|
| `fast` | Supertonic 3, Robert/M3, 16 steps | everyday voice mode, low RAM, lower latency |
| `quality` | Ukrainian/mixed: Patriotyk verbalizer + StyleTTS2; full English sentences: Kokoro `bm_george` | more natural Ukrainian when quality matters |

The plugin preserves Hermes's normal text response and adds audio through the standard Discord/Telegram delivery pipeline.

> **Status:** experimental dogfood release. Linux, Python 3.11, `uv`, `ffmpeg`, systemd user services, and a CPU with enough RAM are currently required. Supertonic's upstream open-source repository is being archived; the local weights still work, but long-term support is uncertain.

## Install

```bash
git clone https://github.com/dmmeteo/hermes-local-tts
cd hermes-local-tts
./scripts/hermes-local-tts install --default fast
```

The installer:

- creates isolated runtimes for fast, quality, and English synthesis;
- downloads the required local model assets;
- installs and enables the Hermes plugin;
- installs user-level systemd services;
- sets `tts.provider=local_tts`;
- starts only the selected backend.

Restart the Hermes gateway once after first installation so Discord/Telegram load the plugin commands.

## Use

Set the mode in each Hermes profile config:

```yaml
tts:
  provider: local_tts
  local_tts:
    mode: fast  # fast | quality
```

The plugin intentionally registers no slash commands. Hermes's standard command remains unchanged:

```text
/voice
/voice on
/voice off
/voice tts
/voice status
/voice join
/voice leave
```

Hermes's standard persistent `/voice` mode uses the configured local mode. Change `tts.local_tts.mode` and restart the profile gateway when switching modes.

## Resource profile observed on a 6-vCPU CPU-only VPS

| Mode | Cold test | Peak/persistent RAM | Notes |
|---|---:|---:|---|
| fast | ~48 s for a 13.3 s bilingual sample | ~0.5–0.6 GiB | one ONNX runtime |
| quality | ~4:14 for a 14.4 s cold bilingual sample | ~3.9–4.0 GiB when both workers stay loaded | highest tested Ukrainian quality |

Warm persistent-service latency is lower than process-cold measurements.

## Routing

Quality mode classifies each sentence:

- fully English sentence → Kokoro `bm_george`;
- Ukrainian or mixed Ukrainian/Latin sentence → Patriotyk verbalizer → StyleTTS2;
- clean Ukrainian sentence bypasses verbalization.

Fast mode uses one Supertonic Robert/M3 voice for all text. Automatic Ukrainian stress placement is intentionally not enabled: the tested stressifier produced confident but incorrect stresses. This remains an open improvement area.

## Privacy

All synthesis is local after model download. Workers bind only to localhost.

## Project notes

The design canon and benchmark history live under [`canon/`](canon/) and [`spike/`](spike/). Generated audio, model files, and virtual environments are excluded from Git.
