# The target's own suite covers ordinary values only (like the real targets in Study E,
# it does not exercise the rare NullSentinel path).
from missing import count_missing, is_missing


def test_none_is_missing():
    assert is_missing(None)


def test_zero_is_not_missing():
    assert not is_missing(0)


def test_empty_string_is_not_missing():
    assert not is_missing("")


def test_list_is_not_missing():
    assert not is_missing([1, 2])


def test_count_plain():
    assert count_missing([None, 1, None, "a"]) == 2


def test_count_empty():
    assert count_missing([]) == 0
