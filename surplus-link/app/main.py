from fastapi import FastAPI, HTTPException, Query

from .forecast import forecast
from .matching import match
from .models import Listing, ListingIn, Notification, Pantry, Site, utcnow
from .store import store

MEAL_LBS = 1.2
CO2E_KG_PER_LB = 1.1

app = FastAPI(title="SurplusLink", description="Match surplus food to pantries in real time.")


@app.get("/sites", response_model=list[Site])
def list_sites():
    return list(store.sites.values())


@app.get("/pantries", response_model=list[Pantry])
def list_pantries():
    return list(store.pantries.values())


@app.post("/listings", response_model=Listing, status_code=201)
def post_listing(data: ListingIn):
    try:
        return store.add_listing(data)
    except KeyError:
        raise HTTPException(404, "Unknown site_id")


@app.get("/listings", response_model=list[Listing])
def list_listings():
    return list(store.listings.values())


@app.post("/match")
def run_match():
    now = utcnow()
    for l in store.listings.values():
        if l.status == "open" and l.pickup_deadline <= now:
            l.status = "expired"

    open_listings = [l for l in store.listings.values() if l.status == "open"]
    remaining = {pid: store.remaining(pid) for pid in store.pantries}
    pairs = match(open_listings, store.sites, list(store.pantries.values()), remaining, now)

    matched = []
    for listing_id, pantry_id, sc in pairs:
        l = store.listings[listing_id]
        l.status, l.pantry_id, l.score = "matched", pantry_id, round(sc, 3)
        site = store.sites[l.site_id]
        store.notify(
            listing_id,
            pantry_id,
            f"{site.name} has {l.quantity_lbs:.0f} lbs of {l.food} for pickup by {l.pickup_deadline:%H:%M} UTC",
        )
        matched.append(l)

    return {
        "matched": [l.model_dump(mode="json") for l in matched],
        "still_open": sum(1 for l in store.listings.values() if l.status == "open"),
    }


@app.get("/notifications", response_model=list[Notification])
def list_notifications():
    return store.notifications


@app.get("/forecast")
def get_forecast(days: int = Query(7, ge=1, le=14)):
    return forecast(list(store.sites.values()), days)


@app.get("/impact")
def impact():
    lbs = sum(l.quantity_lbs for l in store.listings.values() if l.status == "matched")
    return {
        "lbs_diverted": round(lbs, 1),
        "meals_saved": round(lbs / MEAL_LBS, 1),
        "co2e_kg_avoided": round(lbs * CO2E_KG_PER_LB, 1),
        "listings_matched": sum(1 for l in store.listings.values() if l.status == "matched"),
    }

from fastapi.responses import RedirectResponse

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/docs")