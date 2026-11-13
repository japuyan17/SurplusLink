from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import store


@pytest.fixture
def client():
    store.reset()
    return TestClient(app)


def signup(client, role="donor", email="a@example.com", **extra):
    body = {"name": "Alex", "email": email, "password": "password123", "role": role, **extra}
    return client.post("/auth/register", json=body)


def bearer(res):
    return {"Authorization": f"Bearer {res.json()['token']}"}


def listing_body():
    deadline = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat()
    return {"site_id": 1, "food": "Rice", "quantity_lbs": 30, "pickup_deadline": deadline}


def test_register_hides_password_hash(client):
    res = signup(client)
    assert res.status_code == 201
    assert "password" not in str(res.json()["user"])
    assert res.json()["user"]["email"] == "a@example.com"


def test_duplicate_email_rejected_case_insensitive(client):
    signup(client)
    assert signup(client, email="A@Example.com").status_code == 409


@pytest.mark.parametrize("body", [
    {"name": "A", "email": "nope", "password": "password123", "role": "donor"},
    {"name": "A", "email": "a@example.com", "password": "short", "role": "donor"},
    {"name": "A", "email": "a@example.com", "password": "password123", "role": "admin"},
])
def test_invalid_signup_422(client, body):
    assert client.post("/auth/register", json=body).status_code == 422


def test_login(client):
    signup(client)
    assert client.post("/auth/login", json={"email": "a@example.com", "password": "wrongpass1"}).status_code == 401
    ok = client.post("/auth/login", json={"email": "A@example.com", "password": "password123"})
    assert ok.status_code == 200
    assert client.get("/auth/me", headers=bearer(ok)).json()["role"] == "donor"


def test_listing_requires_donor(client):
    assert client.post("/listings", json=listing_body()).status_code == 401
    recipient = signup(client, role="recipient", email="r@example.com")
    assert client.post("/listings", json=listing_body(), headers=bearer(recipient)).status_code == 403


def test_tampered_token_rejected(client):
    token = signup(client).json()["token"]
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {token[:-2]}ab"}).status_code == 401
    assert client.get("/auth/me", headers={"Authorization": "Bearer junk"}).status_code == 401


def test_my_listings_only_shows_own(client):
    a = signup(client, email="a@example.com")
    b = signup(client, email="b@example.com")
    client.post("/listings", json=listing_body(), headers=bearer(a))
    assert len(client.get("/listings/mine", headers=bearer(a)).json()) == 1
    assert client.get("/listings/mine", headers=bearer(b)).json() == []


def test_pickups_for_recipient(client):
    donor = signup(client)
    recipient = signup(client, role="recipient", email="r@example.com")
    assert client.get("/pickups").status_code == 401
    client.post("/listings", json=listing_body(), headers=bearer(donor))
    client.post("/match", headers=bearer(recipient))
    rows = client.get("/pickups", headers=bearer(recipient)).json()
    assert len(rows) == 1
    assert rows[0]["site"] == "Crossroads Dining Hall" and rows[0]["pantry"]


def test_resources_filter(client):
    everything = client.get("/resources").json()
    assert everything and {r["kind"] for r in everything} == {"food_bank", "shelter", "volunteer", "donation"}
    shelters = client.get("/resources?kind=shelter").json()
    assert shelters and all(r["kind"] == "shelter" for r in shelters)
    assert client.get("/resources?kind=bogus").status_code == 422
