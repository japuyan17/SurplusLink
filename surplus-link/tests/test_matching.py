from datetime import datetime, timedelta, timezone

from app.matching import INFEASIBLE, match, score
from app.models import Listing, Pantry, Site

NOW = datetime(2026, 11, 12, 20, 0, tzinfo=timezone.utc)
SITE = Site(id=1, name="A", kind="dining", lat=37.87, lon=-122.26, avg_lbs=50)
SITES = {1: SITE}


def listing(i, qty=20, hours=3, tags=()):
    return Listing(id=i, site_id=1, food="x", quantity_lbs=qty,
                   pickup_deadline=NOW + timedelta(hours=hours), dietary_tags=list(tags))


def pantry(i, lon=-122.26, cap=100, needs=()):
    return Pantry(id=i, name=f"P{i}", lat=37.87, lon=lon, capacity_lbs=cap, needs=list(needs))


def test_infeasible_over_capacity():
    assert score(listing(1, qty=50), SITE, pantry(1), 10, NOW) == INFEASIBLE


def test_infeasible_past_deadline():
    assert score(listing(1, hours=-1), SITE, pantry(1), 100, NOW) == INFEASIBLE


def test_infeasible_too_far_for_deadline():
    assert score(listing(1, hours=0.1), SITE, pantry(1, lon=-122.0), 100, NOW) == INFEASIBLE


def test_closer_pantry_wins():
    pairs = match([listing(1)], SITES, [pantry(1, lon=-122.0), pantry(2)], {1: 100, 2: 100}, NOW)
    assert [(l, p) for l, p, _ in pairs] == [(1, 2)]


def test_dietary_fit_wins_at_equal_distance():
    pairs = match([listing(1, tags=["vegan"])], SITES, [pantry(1), pantry(2, needs=["vegan"])], {1: 100, 2: 100}, NOW)
    assert pairs[0][1] == 2


def test_one_pantry_per_listing_per_round():
    pairs = match([listing(1), listing(2)], SITES, [pantry(1), pantry(2)], {1: 100, 2: 100}, NOW)
    assert len(pairs) == 2
    assert {p for _, p, _ in pairs} == {1, 2}


def test_capacity_respected_across_rounds():
    listings = [listing(i, qty=40) for i in range(1, 4)]
    pairs = match(listings, SITES, [pantry(1, cap=100)], {1: 100}, NOW)
    assert len(pairs) == 2
