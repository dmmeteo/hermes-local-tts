from prototype.language_router import Segment, segment_languages


def test_routes_full_english_phrase() -> None:
    assert segment_languages("Це initial results look promising. Далі тест.") == [
        Segment("uk", "Це"), Segment("en", "initial results look promising."), Segment("uk", "Далі тест.")]


def test_keeps_lone_technical_tokens_with_ukrainian() -> None:
    assert segment_languages("CPU і RAM працюють у Hermes.") == [Segment("uk", "CPU і RAM працюють у Hermes.")]


def test_routes_selected_mixed_sentence() -> None:
    assert segment_languages("Українська частина, а потім the initial results look promising. І знову українська.") == [
        Segment("uk", "Українська частина, а потім"), Segment("en", "the initial results look promising."), Segment("uk", "І знову українська.")]
