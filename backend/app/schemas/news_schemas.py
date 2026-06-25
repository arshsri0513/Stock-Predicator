"""
Request/response schemas for the news and sentiment analysis endpoints.
"""

from pydantic import BaseModel


class NewsItem(BaseModel):
    title: str
    publisher: str
    link: str
    published: str
    vader_compound: float
    vader_label: str
    finbert_label: str
    finbert_confidence: float


class NewsResponse(BaseModel):
    ticker: str
    article_count: int
    articles: list[NewsItem]
    average_vader_compound: float
