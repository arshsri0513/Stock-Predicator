"""
Watchlist API routes: GET/POST/DELETE /watchlist.

Every route here is PROTECTED -- it requires Depends(get_current_user),
meaning an unauthenticated request gets a 401 before any watchlist logic
even runs. This is the first set of routes in the project that actually
enforces login, now that Phase 12 built real authentication.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.watchlist_schemas import WatchlistAddRequest, WatchlistItem
from app.services.watchlist_service import add_to_watchlist, remove_from_watchlist, get_watchlist

router = APIRouter()


@router.get("", response_model=list[WatchlistItem])
def list_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns the authenticated user's full watchlist."""
    return get_watchlist(db, str(current_user.id))


@router.post("", response_model=WatchlistItem, status_code=201)
def add_watchlist_item(
    request: WatchlistAddRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adds a ticker to the authenticated user's watchlist."""
    entry = add_to_watchlist(db, str(current_user.id), request.ticker)
    return WatchlistItem(id=str(entry.id), ticker=request.ticker.upper(), added_at=entry.added_at)


@router.delete("/{ticker}", status_code=204)
def remove_watchlist_item(
    ticker: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Removes a ticker from the authenticated user's watchlist."""
    removed = remove_from_watchlist(db, str(current_user.id), ticker)
    if not removed:
        raise HTTPException(status_code=404, detail=f"'{ticker}' is not on your watchlist.")
    return None
