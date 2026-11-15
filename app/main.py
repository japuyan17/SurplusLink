from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse

from .auth import current_user, hash_password, make_token, require_role, verify_password
from .forecast import forecast
from .matching import match
from .models import (
    Listing, ListingIn, LoginIn, Notification, Pantry, Resource, Site, User, UserIn, UserOut, ResourceKind, utcnow,
)
from .resources import RESOURCES
from .store import store

MEAL_LBS = 1.2
CO2E_KG_PER_LB = 1.1

app = FastAPI(title="SurplusLink", description="Match surplus food to pantries in real time.")


def session(user: User) -> dict:
    return {"token": make_token(user.id), "user": UserOut.model_validate(user.model_dump())}


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/docs")


@app.post("/auth/register", status_code=201)
def register(data: UserIn):
    if data.role == "donor" and data.site_id is not None and data.site_id not in store.sites:
        raise HTTPException(404, "Unknown site_id")
    try:
        user = store.add_user(data, hash_password(data.password))
    except ValueError:
        raise HTTPException(409, "That email is already registered")
    return session(user)


@app.post("/auth/login")
def login(data: LoginIn):
    user = store.user_by_email(data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return session(user)


@app.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user


@app.get("/sites", response_model=list[Site])
def list_sites():
    return list(store.sites.values())


@app.get("/pantries", response_model=list[Pantry])
def list_pantries():
    return list(store.pantries.values())


@app.get("/resources", response_model=list[Resource])
def list_resources(kind: ResourceKind | None = None):
    return [r for r in RESOURCES if kind is None or r.kind == kind]


@app.post("/listings", response_model=Listing, status_code=201)
def post_listing(data: ListingIn, user: User = Depends(require_role("donor"))):
    try:
        return store.add_listing(data, donor_id=user.id)
    except KeyError:
        raise HTTPException(404, "Unknown site_id")


@app.get("/listings", response_model=list[Listing])
def list_listings():
    return list(store.listings.values())


@app.get("/listings/mine", response_model=list[Listing])
def my_listings(user: User = Depends(require_role("donor"))):
    return [l for l in store.listings.values() if l.donor_id == user.id]


@app.get("/pickups")
def pickups(user: User = Depends(current_user)):
    now = utcnow()
    rows = []
    for l in store.listings.values():
        if l.status == "expired" or l.pickup_deadline <= now:
            continue
        site = store.sites[l.site_id]
        pantry = store.pantries.get(l.pantry_id) if l.pantry_id else None
        rows.append({
            "id": l.id,
            "food": l.food,
            "quantity_lbs": l.quantity_lbs,
            "dietary_tags": l.dietary_tags,
            "pickup_deadline": l.pickup_deadline.isoformat(),
            "status": l.status,
            "site": site.name,
            "site_lat": site.lat,
            "site_lon": site.lon,
            "site_address": site.address,
            "pantry": pantry.name if pantry else None,
            "pantry_lat": pantry.lat if pantry else None,
            "pantry_lon": pantry.lon if pantry else None,
            "pantry_address": pantry.address if pantry else "",
        })
    return sorted(rows, key=lambda r: r["pickup_deadline"])


@app.post("/match")
def run_match(user: User = Depends(current_user)):
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
