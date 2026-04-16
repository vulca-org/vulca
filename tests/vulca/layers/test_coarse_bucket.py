"""Phase 0 Task 3: coarse_bucket extraction for multi-layer content_type."""
from vulca.layers.coarse_bucket import coarse_bucket_of, is_background


def test_exact_background_is_background():
    assert coarse_bucket_of("background") == "background"


def test_dotted_background_is_background():
    assert coarse_bucket_of("background.catch_all") == "background"
    assert coarse_bucket_of("background.sky") == "background"


def test_exact_subject_is_subject():
    assert coarse_bucket_of("subject") == "subject"


def test_dotted_subject_is_subject():
    assert coarse_bucket_of("subject.face.eyes") == "subject"


def test_person_indexed_is_subject():
    assert coarse_bucket_of("person[0].face") == "subject"
    assert coarse_bucket_of("person[3].hair") == "subject"


def test_unknown_bucket_returns_as_is():
    assert coarse_bucket_of("detail") == "detail"
    assert coarse_bucket_of("atmosphere") == "atmosphere"


def test_empty_string_defaults_to_background():
    assert coarse_bucket_of("") == "background"


def test_false_positive_background_noise_is_subject():
    assert coarse_bucket_of("background_noise") == "background_noise"


def test_is_background_helper():
    assert is_background("background") is True
    assert is_background("background.catch_all") is True
    assert is_background("subject") is False
    assert is_background("person[0].face") is False
    assert is_background("background_noise") is False
    assert is_background("") is True
