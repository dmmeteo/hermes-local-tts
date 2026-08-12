from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

Language = Literal["uk", "en"]

# One or more Latin-script tokens. Digits are allowed after the first letter so
# product/model names such as StyleTTS2 are routed to the English voice too.
_ENGLISH_RE = re.compile(
    r"(?<![A-Za-z0-9])"
    r"[A-Za-z][A-Za-z0-9]*(?:[-'][A-Za-z0-9]+)*"
    r"(?:[ \t]+[A-Za-z][A-Za-z0-9]*(?:[-'][A-Za-z0-9]+)*)*"
    r"(?:[.,!?;:]?(?=\s|$))"
)


@dataclass(frozen=True)
class Segment:
    language: Language
    text: str


def segment_languages(text: str, *, min_english_words: int = 1) -> list[Segment]:
    """Route Latin-script words and phrases to the English voice."""
    if min_english_words != 1:
        raise ValueError("router currently supports min_english_words=1")

    segments: list[Segment] = []
    cursor = 0
    for match in _ENGLISH_RE.finditer(text):
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
