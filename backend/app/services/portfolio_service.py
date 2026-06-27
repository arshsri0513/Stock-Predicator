"""
Portfolio tracker business logic.

Reuses the same get_or_create_stock pattern from watchlist_service, since
both features need the same "find or create a Stock row" behavior.
"""

from sqlalchemy.orm import Session

from app.models.financial import PortfolioHolding
from app.services.watchlist_service import get_or_create_stock
from app.services.stock_data import fetch_recent_data


def add_holding(db: Session, user_id: str, ticker: str, quantity: float, purchase_price: float) -> PortfolioHolding:
    """
    Record a new purchase. Unlike watchlist (which treats duplicates as a
    no-op), each holding is its own row -- buying the same stock twice at
    different prices/times are two genuinely different events worth
    tracking separately (e.g. for accurate average-cost calculations
    later), not something to silently merge.
    """
    stock = get_or_create_stock(db, ticker)
    holding = PortfolioHolding(
        user_id=user_id,
        stock_id=stock.id,
        quantity=quantity,
        purchase_price=purchase_price,
    )
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return holding


def remove_holding(db: Session, user_id: str, holding_id: str) -> bool:
    """Remove a specific holding by its own ID (not by ticker, since a
    user might have multiple separate holdings of the same stock)."""
    holding = (
        db.query(PortfolioHolding)
        .filter(PortfolioHolding.id == holding_id, PortfolioHolding.user_id == user_id)
        .first()
    )
    if holding is None:
        return False
    db.delete(holding)
    db.commit()
    return True


def get_portfolio_with_gains(db: Session, user_id: str) -> list[dict]:
    """
    Return every holding for a user, enriched with CURRENT price and
    computed gain/loss. We fetch the current price live (via yfinance,
    same as every other price lookup in this project) rather than storing
    a cached price ourselves -- a stored price would inevitably go stale,
    and "is my portfolio's gain/loss accurate right now" is exactly the
    kind of thing that should never be answered with stale data.

    If a price fetch fails for one ticker, we still return that holding
    with the gain/loss fields as None rather than failing the whole
    response -- same defensive pattern as Phase 13's predict-multi.
    """
    holdings = db.query(PortfolioHolding).filter(PortfolioHolding.user_id == user_id).all()

    results = []
    for holding in holdings:
        ticker = holding.stock.ticker
        entry = {
            "id": str(holding.id),
            "ticker": ticker,
            "quantity": holding.quantity,
            "purchase_price": holding.purchase_price,
            "purchased_at": holding.purchased_at,
            "current_price": None,
            "market_value": None,
            "gain_loss": None,
            "gain_loss_percent": None,
        }

        try:
            recent = fetch_recent_data(ticker, days=5)
            current_price = float(recent["Close"].iloc[-1])
            market_value = current_price * holding.quantity
            cost_basis = holding.purchase_price * holding.quantity
            gain_loss = market_value - cost_basis

            entry["current_price"] = round(current_price, 2)
            entry["market_value"] = round(market_value, 2)
            entry["gain_loss"] = round(gain_loss, 2)
            entry["gain_loss_percent"] = round((gain_loss / cost_basis) * 100, 2)
        except Exception:
            pass  # leave the gain/loss fields as None for this one holding

        results.append(entry)

    return results
