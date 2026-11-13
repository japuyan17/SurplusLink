from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.forecast import forecast
from app.main import app
from app.store import store


@pytest.fixture
def client():
    store.reset()
    return TestClient(app)


def payload(site_id=1, qty=100, hours=3, **extra):
    deadline = (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()
    return {"site_id": site_id, "food": "Pasta", "quantity_lbs": qty, "pickup_deadline": deadline, **extra}


def test_post_match_impact(client):
    assert client.post("/listings", json=payload(dietary_tags=["vegetarian"])).status_code == 201
    res = client.post("/match").json()
    assert len(res["matched"]) == 1 and res["still_open"] == 0
    assert len(client.get("/notifications").json()) == 1
    imp = client.get("/impact").json()
    assert imp["lbs_diverted"] == 100
    assert imp["meals_saved"] == round(100 / 1.2, 1)
    assert imp["co2e_kg_avoided"] == 110


def test_unknown_site_404(client):
    assert client.post("/listings", json=payload(site_id=999)).status_code == 404


def test_invalid_quantity_422(client):
    assert client.post("/listings", json=payload(qty=0)).status_code == 422


def test_expired_listing_not_matched(client):
    client.post("/listings", json=payload(hours=-1))
    assert client.post("/match").json()["matched"] == []
    assert client.get("/listings").json()[0]["status"] == "expired"


def test_forecast_shape(client):
    rows = client.get("/forecast?days=5").json()
    assert len(rows) == 5 * len(store.sites)
    assert all(r["predicted_lbs"] >= 0 for r in rows)


def test_forecast_weekday_exceeds_weekend():
    rows = [r for r in forecast([store.sites[1]], 7, start=date(2026, 11, 9))]
    assert rows[1]["predicted_lbs"] > rows[6]["predicted_lbs"]
