"""
Unit tests for app.services.sentiment_vader's classify_sentiment().

This function is pure logic with no external calls (the VADER analyzer
itself isn't being tested here -- that's a third-party library's
responsibility, not ours; we test OUR code, the threshold classification
built on top of its output).
"""

from app.services.sentiment_vader import classify_sentiment


def test_classify_sentiment_positive():
    assert classify_sentiment(0.8) == "positive"
    assert classify_sentiment(0.05) == "positive"  # boundary, inclusive


def test_classify_sentiment_negative():
    assert classify_sentiment(-0.8) == "negative"
    assert classify_sentiment(-0.05) == "negative"  # boundary, inclusive


def test_classify_sentiment_neutral():
    assert classify_sentiment(0.0) == "neutral"
    assert classify_sentiment(0.049) == "neutral"  # just inside the neutral band
    assert classify_sentiment(-0.049) == "neutral"
