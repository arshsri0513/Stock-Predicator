"""
News and sentiment API routes.

Same thin-route pattern as the rest of the project -- this file fetches
news via app.services.stock_data, scores it via both sentiment services,
and combines the results into one response. All real logic lives in the
service modules; this file only orchestrates and formats.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.news_schemas import NewsResponse, NewsItem
from app.services.stock_data import fetch_news
from app.services.sentiment_vader import score_text_vader, classify_sentiment
from app.services.sentiment_finbert import score_text_finbert

router = APIRouter()


@router.get("/{ticker}", response_model=NewsResponse)
def get_news_with_sentiment(ticker: str, limit: int = 10):
    """
    Fetch recent news for a ticker and score each headline with BOTH VADER
    (fast, rule-based) and FinBERT (slower, finance-specific deep learning),
    so the results can be directly compared.

    Note: the first call to this endpoint after server startup will be
    noticeably slower than subsequent calls -- FinBERT's model weights
    (~400MB) get downloaded and loaded into memory on first use, then
    cached in memory for every call after that.

    Example: GET /news/AAPL?limit=10
    """
    try:
        articles = fetch_news(ticker, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch news for '{ticker}': {str(e)}",
        )

    if not articles:
        return NewsResponse(
            ticker=ticker.upper(),
            article_count=0,
            articles=[],
            average_vader_compound=0.0,
        )

    scored_articles = []
    compound_scores = []

    for article in articles:
        vader_result = score_text_vader(article["title"])
        finbert_result = score_text_finbert(article["title"])

        compound_scores.append(vader_result["compound"])

        scored_articles.append(NewsItem(
            title=article["title"],
            publisher=article["publisher"],
            link=article["link"],
            published=article["published"],
            vader_compound=vader_result["compound"],
            vader_label=classify_sentiment(vader_result["compound"]),
            finbert_label=finbert_result["label"],
            finbert_confidence=finbert_result["confidence"],
        ))

    return NewsResponse(
        ticker=ticker.upper(),
        article_count=len(scored_articles),
        articles=scored_articles,
        average_vader_compound=round(sum(compound_scores) / len(compound_scores), 4),
    )
