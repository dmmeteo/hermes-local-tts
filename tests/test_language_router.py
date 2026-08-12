from prototype.language_router import Segment, segment_languages


def test_routes_full_english_sentence() -> None:
    assert segment_languages("The initial results look promising.") == [
        Segment("en", "The initial results look promising.")
    ]


def test_routes_short_english_sentence() -> None:
    assert segment_languages("Hello world.") == [Segment("en", "Hello world.")]


def test_keeps_mixed_sentence_together_for_verbalization() -> None:
    assert segment_languages("Hermes використовує CPU і RAM.") == [
        Segment("uk", "Hermes використовує CPU і RAM.")
    ]


def test_keeps_ukrainian_sentence() -> None:
    assert segment_languages("Система працює локально.") == [
        Segment("uk", "Система працює локально.")
    ]
