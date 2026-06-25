"""
VADER sentiment analysis -- a fast, rule-based (NOT deep learning) sentiment
scorer. VADER stands for "Valence Aware Dictionary and sEntiment Reasoner."

How it works (so this isn't a black box): VADER has a built-in dictionary of
thousands of words, each pre-scored for sentiment intensity (e.g. "great"
scores positive, "terrible" scores negative). It also has hand-coded rules
for negation ("not good" flips the sentiment), intensifiers ("very good" is
stronger than "good"), capitalization, and punctuation (multiple "!!!"
increases intensity). It combines all of this into a single normalized
score, with NO machine learning involved -- it's a fast, deterministic,
rule-based system.

This makes VADER fast and require no training, but also means it has no
real understanding of financial language specifically -- it was originally
built and tuned for social media text. We use it here as our FAST baseline,
the same role Linear Regression played in Phase 5.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Created once, reused for every call -- VADER's analyzer loads its lexicon
# dictionary at construction time, so creating a new one per request would
# be wasteful.
_analyzer = SentimentIntensityAnalyzer()


def score_text_vader(text: str) -> dict:
    """
    Score a single piece of text (headline, article snippet, etc.) using VADER.

    Returns a dict with four scores:
    - neg, neu, pos: proportions of negative/neutral/positive content
      (these three always sum to 1.0)
    - compound: a single normalized score from -1 (most negative) to +1
      (most positive) -- this is the one we'll primarily use as a feature,
      since it's the most convenient single number to feed into other code.
    """
    scores = _analyzer.polarity_scores(text)
    return {
        "negative": round(scores["neg"], 4),
        "neutral": round(scores["neu"], 4),
        "positive": round(scores["pos"], 4),
        "compound": round(scores["compound"], 4),
    }


def classify_sentiment(compound_score: float) -> str:
    """
    Convert a compound score into a human-readable label.
    Thresholds of +-0.05 are VADER's own documented convention, not
    something we invented -- using their established convention keeps our
    labels consistent with how VADER is used elsewhere.
    """
    if compound_score >= 0.05:
        return "positive"
    elif compound_score <= -0.05:
        return "negative"
    else:
        return "neutral"


def score_headlines_vader(headlines: list[str]) -> list[dict]:
    """
    Score a list of headlines, returning one result dict per headline,
    each annotated with its classified label.
    """
    results = []
    for headline in headlines:
        scores = score_text_vader(headline)
        results.append({
            "text": headline,
            **scores,
            "label": classify_sentiment(scores["compound"]),
        })
    return results
