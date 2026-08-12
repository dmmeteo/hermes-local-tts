from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

Language = Literal["uk", "en"]

# Require at least two Latin-script words. This deliberately keeps lone
# technical tokens such as CPU, RAM, Hermes, and ONNX in the Ukrainian stream.
_ENGLISH_PHRASE_RE = re.compile(
    r"(?<![A-Za-z])"
    r"[A-Za-z]+(?:[-'][A-Za-z]+)*"
    r"(?:[ \t]+[A-Za-z]+(?:[-'][A-Za-z]+)*)+"
    r"(?:[.,!?;:]?(?=\s|$))"
)


@dataclass(frozen=True)
class Segment:
    language: Language
    text: str


def segment_languages(text: str, *, min_english_words: int = 2) -> list[Segment]:
    """Route complete English phrases while retaining isolated Latin tokens."""
    if min_english_words != 2:
        raise ValueError("prototype router currently supports min_english_words=2")

    segments: list[Segment] = []
    cursor = 0
    for match in _ENGLISH_PHRASE_RE.finditer(text):
        before = text[cursor:match.start()].strip()
        if before:
            segments.append(Segment("uk", before))
        phrase = match.group(0).strip()
        if phrase:
            segments.append(Segment("en", phrase))
        cursor = match.end()

    remainder = text[cursor:].strip()
    if remainder:
        segments.append(Segment("uk", remainder))

    if not segments and text.strip():
        return [Segment("uk", text.strip())]
    return segments
