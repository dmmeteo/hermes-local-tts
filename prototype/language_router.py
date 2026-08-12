from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

Language = Literal["uk", "en"]


@dataclass(frozen=True)
class Segment:
    language: Language
    text: str


def segment_languages(text: str) -> list[Segment]:
    """Classify one sentence as fully English or Ukrainian/mixed."""
    value = text.strip()
    if not value:
        return []
    cyrillic = len(re.findall(r"[А-Яа-яІіЇїЄєҐґ]", value))
    words = re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", value)
    language: Language = "en" if words and cyrillic == 0 else "uk"
    return [Segment(language, value)]
