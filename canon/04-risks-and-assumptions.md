# Risks and assumptions

| Risk / assumption | Current treatment |
|---|---|
| StyleTTS2 may be slower than real time on 6 VPS vCPU | Measure cold/warm RTF before production architecture |
| Peak RAM may destabilize the gateway | Isolated process, one model, concurrency 1, measure peak RSS |
| Existing swap is heavily used | Avoid simultaneous heavy model work; fail closed on low-memory startup |
| PyTorch packages may conflict with Hermes | Dedicated venv/runtime |
| Ukrainian verbalization may introduce grammatical errors | Optional and A/B tested; support raw-normalized fallback |
| English words sound poor | Accepted MVP limitation; bilingual routing is deferred |
| Plugin command origin context is incomplete upstream | Start with provider path; keep one-shot command bounded and synchronous or defer |
| Model downloads/artifacts may change | Pin model revision after the spike |
| Licenses may differ across code/model/data | Record and verify each dependency before release |
