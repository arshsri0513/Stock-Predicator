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
_finbert_pipeline = None


def _get_finbert_pipeline():
    global _finbert_pipeline
    if _finbert_pipeline is None:
        from transformers import pipeline
        _finbert_pipeline = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
        )
    return _finbert_pipeline


def score_text_finbert(text: str) -> dict:
    """
    Score a single piece of text using FinBERT.

    Returns a dict with the predicted label (positive/negative/neutral)
    and FinBERT's confidence score for that label (0 to 1).

    Note: FinBERT truncates input to 512 tokens (a BERT architecture
    limit) -- for headlines this is never an issue, but worth knowing if
    you ever feed it full long articles instead of just headlines.
    """
    classifier = _get_finbert_pipeline()
    result = classifier(text, truncation=True)[0]

    return {
        "label": result["label"],
        "confidence": round(float(result["score"]), 4),
    }


def score_headlines_finbert(headlines: list[str]) -> list[dict]:
    """
    Score a list of headlines with FinBERT. Uses a single batched call
    rather than looping one-by-one -- batching is significantly more
    efficient for neural network inference, since the model can process
    multiple inputs in parallel rather than paying the per-call overhead
    repeatedly.
    """
    if not headlines:
        return []

    classifier = _get_finbert_pipeline()
    raw_results = classifier(headlines, truncation=True)

    return [
        {
            "text": headline,
            "label": result["label"],
            "confidence": round(float(result["score"]), 4),
        }
        for headline, result in zip(headlines, raw_results)
    ]