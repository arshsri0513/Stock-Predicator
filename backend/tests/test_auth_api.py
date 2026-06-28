"""
API tests for /auth/signup, /auth/login, /auth/me.

These tests create REAL rows in your database (the same Postgres
container every other part of this project uses) -- there's no separate
test database configured. This is a real, known limitation worth being
upfront about: a more mature test setup would use a separate test
database that gets wiped between runs, so tests never leave behind data
or risk colliding with real accounts. We don't build that isolation here,
which means re-running these tests with the SAME hardcoded test email
twice will correctly fail on the second run's signup step (409 conflict)
-- not a bug in the test, but a direct consequence of this simplification.
"""

import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def unique_email() -> str:
    """Generate a fresh, never-before-used email for each test run, so
    repeated test runs don't collide with previous runs' leftover data --
    a lightweight workaround for not having a real isolated test database."""
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


def test_signup_creates_user():
    email = unique_email()
    response = client.post("/auth/signup", json={"email": email, "password": "testpass123"})
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == email
    assert "id" in body


def test_signup_duplicate_email_rejected():
    email = unique_email()
    client.post("/auth/signup", json={"email": email, "password": "testpass123"})

    duplicate_response = client.post("/auth/signup", json={"email": email, "password": "anotherpass123"})
    assert duplicate_response.status_code == 409


def test_login_with_correct_credentials_returns_token():
    email = unique_email()
    client.post("/auth/signup", json={"email": email, "password": "testpass123"})

    response = client.post("/auth/login", json={"email": email, "password": "testpass123"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_wrong_password_rejected():
    email = unique_email()
    client.post("/auth/signup", json={"email": email, "password": "testpass123"})

    response = client.post("/auth/login", json={"email": email, "password": "wrongpassword"})
    assert response.status_code == 401


def test_me_endpoint_requires_authentication():
    """Calling a protected route with no Authorization header at all
    should be rejected, not silently treated as 'no user'."""
    response = client.get("/auth/me")
    assert response.status_code in (401, 403)


def test_me_endpoint_works_with_valid_token():
    email = unique_email()
    client.post("/auth/signup", json={"email": email, "password": "testpass123"})
    login_response = client.post("/auth/login", json={"email": email, "password": "testpass123"})
    token = login_response.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == email
