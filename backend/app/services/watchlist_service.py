"""
Watchlist business logic.

Key design point: our Stock table (Phase 9) was defined but nothing has
written to it yet -- every /stocks endpoint so far fetches live from
yfinance rather than reading our database. Watchlist is the first feature
that actually needs a persistent Stock row to attach a foreign key to.

We handle this with a "find or create" pattern: when someone adds a ticker
to their watchlist, we check if a Stock row for that ticker already
exists; if not, we create a minimal one on the spot. This means the Stock
table grows organically as people actually use the watchlist feature,
rather than us needing to pre-populate it with every possible ticker in
existence.
"""

from sqlalchemy.orm import Session

from app.models.user import Stock
from app.models.financial import Watchlist


def get_or_create_stock(db: Session, ticker: str) -> Stock:
    """
    Find an existing Stock row by ticker, or create a minimal one if it
    doesn't exist yet.
    """
    ticker = ticker.upper()
    stock = db.query(Stock).filter(Stock.ticker == ticker).first()
    if stock is None:
        stock = Stock(ticker=ticker)
        db.add(stock)
        db.commit()
        db.refresh(stock)
    return stock


def add_to_watchlist(db: Session, user_id: str, ticker: str) -> Watchlist:
    """
    Add a ticker to a user's watchlist. Returns the existing entry if it's
    already there, rather than creating a duplicate -- watchlists are sets
    of stocks, not lists where the same stock could meaningfully appear twice.
    """
    stock = get_or_create_stock(db, ticker)

    existing = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == user_id, Watchlist.stock_id == stock.id)
        .first()
    )
    if existing:
        return existing

    entry = Watchlist(user_id=user_id, stock_id=stock.id)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def remove_from_watchlist(db: Session, user_id: str, ticker: str) -> bool:
    """
    Remove a ticker from a user's watchlist. Returns True if something was
    actually removed, False if it wasn't on the watchlist to begin with --
    lets the route give an accurate response either way.
    """
    ticker = ticker.upper()
    stock = db.query(Stock).filter(Stock.ticker == ticker).first()
    if stock is None:
        return False

    entry = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == user_id, Watchlist.stock_id == stock.id)
        .first()
    )
    if entry is None:
        return False

    db.delete(entry)
    db.commit()
    return True


def get_watchlist(db: Session, user_id: str) -> list[dict]:
    """
    Return a user's full watchlist, joining through to each Stock's
    ticker so the API response is immediately useful without a second
    round-trip to look up tickers by ID.
    """
    entries = (
        db.query(Watchlist, Stock.ticker)
        .join(Stock, Watchlist.stock_id == Stock.id)
        .filter(Watchlist.user_id == user_id)
        .all()
    )
    return [
        {"id": str(entry.id), "ticker": ticker, "added_at": entry.added_at}
        for entry, ticker in entries
    ]
