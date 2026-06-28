"""
Shared pytest configuration, auto-discovered by pytest (no import needed
anywhere -- this file's name and location are a pytest convention).

This file currently just exists to mark `backend/` as the root pytest
runs from, so `from app.xxx import yyy` imports inside test files resolve
correctly regardless of which directory you happen to run `pytest` from.
If we add fixtures shared across many test files later (e.g. a reusable
authenticated test client), they'd go here.
"""
