"""
FinBERT sentiment analysis -- a deep learning model (BERT architecture)
specifically fine-tuned on financial text by researchers at the
ProsusAI/ProsusAI group (the model we use is "ProsusAI/finbert" on
HuggingFace, a widely-used, well-established choice for this purpose).

Unlike VADER, FinBERT is a genuine neural network that was trained on a
large corpus of financial news/text to recognize financial sentiment
specifically. It understands context far better than a word-by-word
lexicon could -- e.g. "shares fell after the company beat expectations"
requires understanding the relationship between two clauses, something
VADER's rule-based approach can't do, but a trained language model can.

The tradeoff: FinBERT is much slower per-call than VADER (a full neural
network forward pass vs. a dictionary lookup) and requires downloading
model weights (~400MB) the first time it's used.

LAZY IMPORT (Phase 15): the `from transformers import pipeline` statement
itself is now inside _get_finbert_pipeline(), not at the top of this
file. An earlier version only deferred CREATING the pipeline object but
still imported the transformers library (and transitively, PyTorch) the
moment this module was imported -- which happened immediately on app
startup, regardless of whether anyone ever called a sentiment function.
That alone was enough memory to help exceed Render's free-tier 512MB
limit before the app could even bind to a port. Moving the import itself
inside the function means PyTorch/transformers are only loaded into
memory the first time a real sentiment request comes in.
"""

# Loaded once and reused -- this is critical for performance. Loading
# FinBERT's weights from disk takes real time (potentially several
# seconds); doing this on every request would make the API unusably slow.
import os
import requests
from app.core.config import settings
from app.services.sentiment_vader import score_text_vader, classify_sentiment

_finbert_pipeline = None
HF_API_URL = "https://api-inference.huggingface.co/models/ProsusAI/finbert"


def _get_finbert_pipeline():
    global _finbert_pipeline
    if _finbert_pipeline is None:
        from transformers import pipeline
        _finbert_pipeline = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
        )
    return _finbert_pipeline


def _query_huggingface_api(texts: list[str]) -> list[dict] | None:
    """
    Query Hugging Face's serverless Inference API to score text sentiment.
    Returns a list of scored dicts, e.g. [{'label': 'positive', 'confidence': 0.95}, ...]
    or None if the API fails / rate limits.
    """
    token = os.environ.get("HF_API_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": texts, "options": {"wait_for_model": True}},
            timeout=10,
        )
        if response.status_code == 200:
            payload = response.json()
            # Standardize Hugging Face's return formats (sometimes nested list, sometimes single list)
            if isinstance(payload, dict):
                payload = [payload]
            if len(payload) > 0 and not isinstance(payload[0], list):
                payload = [payload]

            results = []
            for item in payload:
                # Find the label with highest score
                best = max(item, key=lambda x: x["score"])
                results.append({
                    "label": best["label"].lower(),  # standardized to lowercase
                    "confidence": round(float(best["score"]), 4),
                })
            return results
    except Exception:
        pass
    return None


def score_text_finbert(text: str) -> dict:
    """
    Score a single piece of text using FinBERT.
    Tries the free Hugging Face serverless Inference API first. If that fails,
    falls back to VADER in production (to avoid memory-heavy torch imports)
    or local model pipeline in development.
    """
    # 1. Try serverless API first
    api_results = _query_huggingface_api([text])
    if api_results:
        return api_results[0]

    # 2. Fall back in production (prevent memory bloat / OOM crash)
    if settings.ENVIRONMENT == "production":
        vader_res = score_text_vader(text)
        return {
            "label": classify_sentiment(vader_res["compound"]),
            "confidence": abs(vader_res["compound"]) if vader_res["compound"] != 0 else 0.5,
        }

    # 3. Fall back in development (local transformers pipeline)
    try:
        classifier = _get_finbert_pipeline()
        result = classifier(text, truncation=True)[0]
        return {
            "label": result["label"].lower(),
            "confidence": round(float(result["score"]), 4),
        }
    except Exception:
        # Ultimate fallback to VADER if local model fails to load
        vader_res = score_text_vader(text)
        return {
            "label": classify_sentiment(vader_res["compound"]),
            "confidence": abs(vader_res["compound"]) if vader_res["compound"] != 0 else 0.5,
        }


def score_headlines_finbert(headlines: list[str]) -> list[dict]:
    """
    Score a list of headlines with FinBERT, using batching where possible.
    """
    if not headlines:
        return []

    # 1. Try serverless API first
    api_results = _query_huggingface_api(headlines)
    if api_results:
        return [
            {
                "text": headline,
                "label": res["label"],
                "confidence": res["confidence"],
            }
            for headline, res in zip(headlines, api_results)
        ]

    # 2. Fall back headline-by-headline
    results = []
    for hl in headlines:
        res = score_text_finbert(hl)
        results.append({
            "text": hl,
            "label": res["label"],
            "confidence": res["confidence"],
        })
    return results