"""
Shared rate limiter instance.

Why this lives in its own file rather than being defined in main.py:
route files (app/api/models.py, etc.) need to import the SAME limiter
instance that main.py registers with the FastAPI app, to apply per-route
limits via the @limiter.limit(...) decorator. If we defined it in
main.py and route files tried to import it from there, we'd get a
circular import (main.py imports the routers, routers would import
back from main.py). This tiny separate file breaks that cycle.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
