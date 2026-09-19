"""
tests/test_matcher.py - Unit tests for JobMatcher and language detection.
"""

from core.matcher import JobMatcher


def test_language_detection_russian():
    ru_vacancy = "Ищем опытного системного администратора и инженера технической поддержки в офис в Лимассоле."
    lang = JobMatcher.detect_language(ru_vacancy)
    assert lang == "ru"


def test_language_detection_english():
    en_vacancy = "We are seeking a Senior Infrastructure & Cloud Engineer to join our high-growth fintech startup."
    lang = JobMatcher.detect_language(en_vacancy)
    assert lang == "en"
