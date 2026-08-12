# StyleTTS2 Ukrainian Single — CPU spike

Date: 2026-08-12  
Host: 6 AMD EPYC vCPU, 11 GiB RAM, no GPU  
Model: `patriotyk/styletts2_ukrainian_single`  
Runtime: PyTorch 2.8 CPU, six intra-op threads, one inter-op thread

## Results

| Case | Model load | Preprocess | Inference | Audio | Warm inference RTF | Peak RSS | New swaps |
|---|---:|---:|---:|---:|---:|---:|---:|
| Short, first run | 28.834 s | 1.834 s | 8.862 s | 9.700 s | 0.914 | 2,629,040 KiB | 0 |
| Medium, cached model files | 6.634 s | 3.587 s | 23.279 s | 28.600 s | 0.814 | 2,656,720 KiB | 0 |

`RTF < 1` means inference generated audio faster than playback duration. The resident process should avoid the repeated 6.6-second model load. End-to-end process measurements are longer than the script's internal totals due to interpreter/runtime teardown and file-system activity, which is another reason to use a persistent worker.

## Decision

The model passes the technical resource gate:

- warm inference RTF is below 1 on both samples;
- peak RSS is approximately 2.66 GiB;
- no swap allocations were attributed by `/usr/bin/time`;
- valid 24 kHz PCM WAV and Opus/OGG were produced.

Proceed to a persistent isolated worker **only if the user accepts the listening quality** of the generated sample.

## Reproduction

```bash
/usr/bin/time -v .spike-venv/bin/python spike/benchmark.py \
  --text '...' \
  --output spike/output.wav
```
