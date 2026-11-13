import math
from datetime import datetime

import numpy as np
from scipy.optimize import linear_sum_assignment

from .models import Listing, Pantry, Site

WEIGHTS = {"distance": 0.35, "urgency": 0.25, "dietary": 0.20, "capacity": 0.20}
SPEED_KMH = 20
INFEASIBLE = -1e6


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))


def score(listing: Listing, site: Site, pantry: Pantry, remaining: float, now: datetime) -> float:
    qty = listing.quantity_lbs
    mins_left = (listing.pickup_deadline - now).total_seconds() / 60
    km = haversine_km(site.lat, site.lon, pantry.lat, pantry.lon)
    if remaining < qty or mins_left <= 0 or km / SPEED_KMH * 60 > mins_left:
        return INFEASIBLE

    tags = set(listing.dietary_tags)
    parts = {
        "distance": 1 / (1 + km),
        "urgency": 1 / (1 + mins_left / 60),
        "dietary": len(tags & set(pantry.needs)) / len(tags) if tags else 0.5,
        "capacity": min(1.0, remaining / (2 * qty)),
    }
    return sum(WEIGHTS[k] * v for k, v in parts.items())


def match(
    listings: list[Listing],
    sites: dict[int, Site],
    pantries: list[Pantry],
    remaining: dict[int, float],
    now: datetime,
) -> list[tuple[int, int, float]]:
    """Repeated Hungarian assignment rounds. Returns (listing_id, pantry_id, score)."""
    remaining = dict(remaining)
    pending = list(listings)
    result = []

    while pending and pantries:
        m = np.array([[score(l, sites[l.site_id], p, remaining[p.id], now) for p in pantries] for l in pending])
        rows, cols = linear_sum_assignment(m, maximize=True)
        made = [(r, c) for r, c in zip(rows, cols) if m[r, c] > 0]
        if not made:
            break
        for r, c in made:
            result.append((pending[r].id, pantries[c].id, float(m[r, c])))
            remaining[pantries[c].id] -= pending[r].quantity_lbs
        done = {r for r, _ in made}
        pending = [l for i, l in enumerate(pending) if i not in done]

    return result
